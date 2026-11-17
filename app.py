import json
import os
import sys
import time
from collections import Counter, deque
from io import BytesIO

# ── Windows DLL setup for MediaPipe and OpenCV ───────────────────────────────
if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
    _APP_DIR = os.path.dirname(os.path.abspath(__file__))
    _DLLS_DIR = os.path.join(_APP_DIR, "dlls")
    if os.path.exists(_DLLS_DIR):
        try:
            os.add_dll_directory(_DLLS_DIR)
        except Exception:
            pass
    try:
        import site
        for sp in site.getsitepackages():
            mp_py = os.path.join(sp, "mediapipe", "python")
            if os.path.exists(mp_py):
                os.add_dll_directory(mp_py)
    except Exception:
        pass

import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

import auth_manager
import login_view
import train_lstm
import user_data_manager

mp_hands = None
mp_drawing = None

# Support both legacy MediaPipe solutions and modern MediaPipe Tasks APIs
try:
    from mediapipe.python.solutions import drawing_utils as mp_drawing
    from mediapipe.python.solutions import hands as mp_hands
except Exception:
    try:
        mp_hands = mp.solutions.hands
        mp_drawing = mp.solutions.drawing_utils
    except Exception:
        pass

if mp_hands is None or mp_drawing is None:
    try:
        import urllib.request
        from mediapipe.tasks.python import BaseOptions, vision

        _APP_DIR = os.path.dirname(os.path.abspath(__file__))
        _MODEL_TASK_PATH = os.path.join(_APP_DIR, "model", "hand_landmarker.task")

        if not os.path.exists(_MODEL_TASK_PATH):
            os.makedirs(os.path.dirname(_MODEL_TASK_PATH), exist_ok=True)
            _MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
            urllib.request.urlretrieve(_MODEL_URL, _MODEL_TASK_PATH)

        HAND_CONNECTIONS = [
            (0, 1), (1, 2), (2, 3), (3, 4),
            (0, 5), (5, 6), (6, 7), (7, 8),
            (5, 9), (9, 10), (10, 11), (11, 12),
            (9, 13), (13, 14), (14, 15), (15, 16),
            (13, 17), (17, 18), (18, 19), (19, 20),
            (0, 17),
        ]

        class _LandmarkPoint:
            def __init__(self, x, y, z=0.0):
                self.x = x
                self.y = y
                self.z = z

        class _HandLandmarksProto:
            def __init__(self, landmarks):
                self.landmark = [_LandmarkPoint(lm.x, lm.y, getattr(lm, "z", 0.0)) for lm in landmarks]

        class _ProcessResult:
            def __init__(self, hands_list):
                self.multi_hand_landmarks = [_HandLandmarksProto(h) for h in hands_list] if hands_list else []

        class _TasksHandsContext:
            def __init__(self, min_detection_confidence=0.5, min_tracking_confidence=0.5, max_num_hands=1, **kwargs):
                self.static_image_mode = kwargs.get("static_image_mode", True)
                self.last_timestamp_ms = 0
                options = vision.HandLandmarkerOptions(
                    base_options=BaseOptions(model_asset_path=_MODEL_TASK_PATH),
                    num_hands=max_num_hands,
                    min_hand_detection_confidence=min_detection_confidence,
                    min_hand_presence_confidence=min_tracking_confidence,
                    running_mode=(
                        vision.RunningMode.IMAGE
                        if self.static_image_mode
                        else vision.RunningMode.VIDEO
                    ),
                )
                self.landmarker = vision.HandLandmarker.create_from_options(options)

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                try:
                    self.close()
                except Exception:
                    pass

            def close(self):
                self.landmarker.close()

            def process(self, image_rgb):
                mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
                if self.static_image_mode:
                    res = self.landmarker.detect(mp_img)
                else:
                    self.last_timestamp_ms = max(
                        self.last_timestamp_ms + 1,
                        int(time.monotonic() * 1000),
                    )
                    res = self.landmarker.detect_for_video(mp_img, self.last_timestamp_ms)
                return _ProcessResult(res.hand_landmarks)

        class _MpHandsModule:
            HAND_CONNECTIONS = HAND_CONNECTIONS
            Hands = _TasksHandsContext

        class _MpDrawingModule:
            @staticmethod
            def draw_landmarks(image_bgr, hand_landmarks, connections=HAND_CONNECTIONS):
                h, w = image_bgr.shape[:2]
                pts = [(int(np.clip(lm.x * w, 0, w - 1)), int(np.clip(lm.y * h, 0, h - 1))) for lm in hand_landmarks.landmark]
                for s, e in connections:
                    if s < len(pts) and e < len(pts):
                        cv2.line(image_bgr, pts[s], pts[e], (0, 255, 0), 2, cv2.LINE_AA)
                for x, y in pts:
                    cv2.circle(image_bgr, (x, y), 5, (0, 0, 255), -1, cv2.LINE_AA)
                    cv2.circle(image_bgr, (x, y), 3, (255, 255, 255), -1, cv2.LINE_AA)

        mp_hands = _MpHandsModule()
        mp_drawing = _MpDrawingModule()
    except Exception as _e:
        print(f"Warning: Failed to initialize modern MediaPipe Tasks API: {_e}")

try:
    import pyttsx3
except Exception:
    pyttsx3 = None

try:
    import joblib
except Exception:
    joblib = None

# Configure Streamlit page
st.set_page_config(
    page_title="Sign Language Studio",
    page_icon="🤟",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Authentication Gate ─────────────────────────────────────────────────────────
if "authenticated_user" not in st.session_state or not st.session_state.authenticated_user:
    login_view.render_login_page()
    st.stop()

# User is authenticated
current_user = st.session_state.authenticated_user
user_info = st.session_state.get("user_info") or auth_manager.get_user_profile(current_user) or {}
display_name = user_info.get("display_name", current_user.capitalize())
avatar = user_info.get("avatar", "🧑‍💻")
email = user_info.get("email", "")

# Hide default multi-page navigation from left sidebar
st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"], 
    [data-testid="stSidebarNavItems"],
    [data-testid="stSidebarNavSeparator"] {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Inject "Manual Guide" into the top-right three-dot menu (⋮)
st.html(
    """
    <script>
    (function() {
        const parentDoc = window.parent.document;
        if (!parentDoc) return;

        function injectManualGuideItem() {
            if (parentDoc.getElementById('st-custom-manual-guide-menuitem')) return;

            const items = parentDoc.querySelectorAll('[role="menuitem"]');
            if (!items || items.length === 0) return;

            let recordItem = null;
            let printItem = null;

            for (const item of items) {
                const text = (item.textContent || '').trim().toLowerCase();
                if (text.includes('record screen') || text.includes('record a screencast') || text.includes('record')) {
                    recordItem = item;
                    break;
                }
                if (text.includes('print')) {
                    printItem = item;
                }
            }

            const target = recordItem || printItem;
            if (!target) return;

            const guideItem = target.cloneNode(true);
            guideItem.id = 'st-custom-manual-guide-menuitem';
            
            const walker = parentDoc.createTreeWalker(guideItem, NodeFilter.SHOW_TEXT, null, false);
            let textNode;
            let replaced = false;
            while ((textNode = walker.nextNode())) {
                const val = (textNode.nodeValue || '').trim();
                if (val.toLowerCase().includes('record') || val.toLowerCase().includes('print')) {
                    textNode.nodeValue = '📖 Manual Guide';
                    replaced = true;
                } else if (val.toUpperCase() === 'ESC') {
                    textNode.nodeValue = '';
                }
            }
            if (!replaced) {
                guideItem.textContent = '📖 Manual Guide';
            }

            guideItem.style.cursor = 'pointer';
            guideItem.setAttribute('aria-label', 'Manual Guide');

            guideItem.onclick = function(e) {
                e.preventDefault();
                e.stopPropagation();
                const mm = parentDoc.querySelector('[data-testid="stMainMenu"] button, button[aria-label="View app menu"]');
                if (mm) mm.click();
                window.parent.open('/Manual_Guide', '_blank');
            };

            target.insertAdjacentElement('afterend', guideItem);
        }

        injectManualGuideItem();

        if (!window.__st_menu_observer_installed) {
            window.__st_menu_observer_installed = true;
            const observer = new MutationObserver(function() {
                injectManualGuideItem();
            });
            observer.observe(parentDoc.body, { childList: true, subtree: true });
        }
    })();
    </script>
    """,
    unsafe_allow_javascript=True,
)

# Verify MediaPipe is available
if mp_hands is None or mp_drawing is None:
    st.error(
        "MediaPipe Hands APIs are unavailable in this environment. "
        "Please ensure mediapipe is properly installed: pip install --upgrade mediapipe"
    )
    st.stop()


# ── Isolated Per-User Data Accessors ──────────────────────────────────────────
def load_db():
    return user_data_manager.load_user_db(current_user, seed_if_empty=False)


def save_db(db):
    user_data_manager.save_user_db(current_user, db)


def bytes_to_bgr(uploaded):
    file_bytes = np.asarray(bytearray(uploaded.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    return img


def normalize_landmarks(hand_landmarks):
    points = np.array([[lm.x, lm.y] for lm in hand_landmarks.landmark], dtype=np.float32)
    points = points - points[0]
    scale = np.max(np.linalg.norm(points, axis=1)) + 1e-6
    points = points / scale
    return points.flatten()


def augment_embedding(embedding, rng, noise_std=0.015, scale_jitter=0.03):
    augmented = np.array(embedding, dtype=np.float32).copy()
    augmented = augmented.reshape(-1, 2)
    scale = float(rng.uniform(1.0 - scale_jitter, 1.0 + scale_jitter))
    noise = rng.normal(0.0, noise_std, size=augmented.shape).astype(np.float32)
    augmented = (augmented * scale) + noise
    augmented = augmented.reshape(-1)
    return np.clip(augmented, -2.0, 2.0).astype(np.float32)


def collect_samples_for_label(db, label, embedding, sample_count=20, include_original=True):
    label = label.strip().upper()
    if not label:
        return 0

    rng = np.random.default_rng()
    db.setdefault(label, [])

    added = 0
    if include_original:
        db[label].append(np.array(embedding, dtype=np.float32).tolist())
        added += 1

    while added < sample_count:
        db[label].append(augment_embedding(embedding, rng).tolist())
        added += 1

    save_db(db)
    return added


def detect_hand_and_embedding(image_bgr, min_conf=0.5, detector=None):
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    if detector is None:
        with mp_hands.Hands(
            static_image_mode=True,
            max_num_hands=1,
            min_detection_confidence=min_conf,
            min_tracking_confidence=min_conf,
        ) as image_detector:
            result = image_detector.process(image_rgb)
    else:
        result = detector.process(image_rgb)

    annotated = image_bgr.copy()
    if not result.multi_hand_landmarks:
        return None, annotated

    hand_landmarks = result.multi_hand_landmarks[0]
    mp_drawing.draw_landmarks(annotated, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    return normalize_landmarks(hand_landmarks), annotated


def heuristic_predict(embedding):
    points = embedding.reshape(21, 2)
    wrist = points[0]

    def extended(tip, pip):
        return points[tip][1] < points[pip][1]

    index_on = extended(8, 6)
    middle_on = extended(12, 10)
    ring_on = extended(16, 14)
    pinky_on = extended(20, 18)

    thumb_dist = np.linalg.norm(points[4] - wrist)
    thumb_on = thumb_dist > 0.32

    fingers = [thumb_on, index_on, middle_on, ring_on, pinky_on]
    count = int(sum(fingers))

    if count >= 4:
        return "OPEN_PALM", 0.62
    if count == 0:
        return "FIST", 0.64
    if index_on and middle_on and not ring_on and not pinky_on:
        return "PEACE", 0.66
    if index_on and not middle_on and not ring_on and not pinky_on:
        return "POINT", 0.60
    return "UNKNOWN_HAND_SIGN", 0.50


def flatten_db(db):
    vectors, labels = [], []
    for label, samples in db.items():
        for sample in samples:
            vectors.append(np.array(sample, dtype=np.float32))
            labels.append(label)
    if not vectors:
        return np.array([]), []
    return np.vstack(vectors), labels


def build_supervised_arrays(db, target_labels=None):
    X, y = [], []
    if target_labels is None:
        target_labels = sorted(db.keys())
    label_to_idx = {lbl: i for i, lbl in enumerate(target_labels)}

    for lbl, samples in db.items():
        if lbl not in label_to_idx:
            continue
        for sample in samples:
            X.append(np.array(sample, dtype=np.float32))
            y.append(label_to_idx[lbl])

    if not X:
        return None, None, target_labels
    return np.vstack(X), np.array(y), target_labels


def evaluate_model_holdout(clf, db, model_labels):
    X, y, labels = build_supervised_arrays(db, target_labels=model_labels)
    if X is None or y is None:
        return None, "No compatible labeled samples found for current trained model labels."

    class_counts = np.bincount(y, minlength=len(labels))
    if np.min(class_counts) < 2 or len(labels) < 2:
        return None, "Need at least 2 samples per label and at least 2 labels for stratified holdout evaluation."

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    y_proba = clf.predict_proba(X_test)
    y_conf = np.max(y_proba, axis=1)

    acc = float(accuracy_score(y_test, y_pred))
    cm = confusion_matrix(y_test, y_pred, labels=np.arange(len(labels)))
    cm_df = pd.DataFrame(cm, index=[f"true_{l}" for l in labels], columns=[f"pred_{l}" for l in labels])

    report = classification_report(y_test, y_pred, target_names=labels, output_dict=True, zero_division=0)
    report_df = pd.DataFrame(report).transpose().round(3)

    mis_rows = []
    for idx, (yt, yp) in enumerate(zip(y_test, y_pred)):
        if yt != yp:
            mis_rows.append(
                {
                    "sample_index": int(idx),
                    "true_label": labels[int(yt)],
                    "pred_label": labels[int(yp)],
                    "pred_confidence": float(y_conf[idx]),
                }
            )
    mis_df = pd.DataFrame(mis_rows)

    return {
        "accuracy": acc,
        "cm_df": cm_df,
        "report_df": report_df,
        "mis_df": mis_df,
        "test_samples": int(len(y_test)),
    }, None


def is_bootstrap_number_dataset(db):
    expected_labels = [str(i) for i in range(10)]
    if sorted(db.keys()) != expected_labels:
        return False
    counts = [len(db[label]) for label in expected_labels]
    return len(set(counts)) == 1 and counts[0] >= 50


def knn_predict(embedding, db, k=3):
    X, y = flatten_db(db)
    if len(y) == 0:
        return None, 0.0

    dists = np.linalg.norm(X - embedding, axis=1)
    idx = np.argsort(dists)[: min(k, len(dists))]
    nearest_labels = [y[i] for i in idx]
    nearest_dists = dists[idx]

    scores = {}
    for lbl, d in zip(nearest_labels, nearest_dists):
        scores[lbl] = scores.get(lbl, 0.0) + 1.0 / (d + 1e-6)

    best_label = max(scores, key=scores.get)
    confidence = scores[best_label] / (sum(scores.values()) + 1e-9)
    return best_label, float(confidence)


def load_trained_model():
    if not joblib:
        return None, None, False
    model_path, labels_path, is_personal = user_data_manager.get_user_model_paths(current_user)
    if not (model_path and labels_path and os.path.exists(model_path) and os.path.exists(labels_path)):
        return None, None, False
    try:
        clf = joblib.load(model_path)
        with open(labels_path, "r", encoding="utf-8") as f:
            labels = json.load(f)
        return clf, labels, is_personal
    except Exception:
        return None, None, False


def model_predict(embedding, clf, labels):
    prob = clf.predict_proba([embedding])[0]
    idx = int(np.argmax(prob))
    return labels[idx], float(prob[idx])


def predict_label(embedding, clf, model_labels, db):
    pred_label, pred_conf = None, 0.0
    if clf is not None and model_labels is not None:
        pred_label, pred_conf = model_predict(embedding, clf, model_labels)
        mode_used = "Trained RandomForest"
    else:
        pred_label, pred_conf = knn_predict(embedding, db, k=5)
        mode_used = "Few-shot kNN"

    if pred_label is None:
        pred_label, pred_conf = heuristic_predict(embedding)
        mode_used = "No-dataset heuristic"

    return pred_label, pred_conf, mode_used


def smooth_prediction(history):
    if not history:
        return None, 0.0

    labels = [item[0] for item in history]
    label_counts = Counter(labels)
    max_count = max(label_counts.values())
    candidates = [lbl for lbl, cnt in label_counts.items() if cnt == max_count]

    if len(candidates) == 1:
        chosen = candidates[0]
    else:
        avg_conf = {}
        for lbl in candidates:
            confs = [conf for item_lbl, conf in history if item_lbl == lbl]
            avg_conf[lbl] = sum(confs) / max(1, len(confs))
        chosen = max(avg_conf, key=avg_conf.get)

    chosen_confs = [conf for item_lbl, conf in history if item_lbl == chosen]
    return chosen, float(sum(chosen_confs) / max(1, len(chosen_confs)))


def add_to_sentence(text, confidence, threshold):
    if confidence < threshold:
        return
    if not st.session_state.sentence or st.session_state.sentence[-1] != text:
        st.session_state.sentence.append(text)


def add_to_sentence_with_cooldown(text, confidence, threshold, cooldown_sec=0.0):
    if confidence < threshold:
        return

    now_ts = time.time()
    last_added_by_label = st.session_state.get("last_added_by_label", {})
    last_added_ts = float(last_added_by_label.get(text, 0.0))

    if cooldown_sec > 0 and (now_ts - last_added_ts) < cooldown_sec:
        return

    if not st.session_state.sentence or st.session_state.sentence[-1] != text:
        st.session_state.sentence.append(text)
        last_added_by_label[text] = now_ts
        st.session_state.last_added_by_label = last_added_by_label


def compute_adaptive_cooldown(base_cooldown, confidence, low_conf_cutoff, max_multiplier):
    if base_cooldown <= 0:
        return 0.0
    if confidence >= low_conf_cutoff:
        return float(base_cooldown)

    normalized_gap = (low_conf_cutoff - confidence) / max(low_conf_cutoff, 1e-6)
    normalized_gap = min(max(normalized_gap, 0.0), 1.0)
    multiplier = 1.0 + normalized_gap * (max_multiplier - 1.0)
    return float(base_cooldown * multiplier)


def detect_unstable_trend(conf_history, label_history, conf_std_limit, switch_limit):
    if len(conf_history) < 4 or len(label_history) < 4:
        return False, "warming_up"

    conf_std = float(np.std(np.array(conf_history, dtype=np.float32)))
    switches = sum(1 for i in range(1, len(label_history)) if label_history[i] != label_history[i - 1])

    if conf_std >= conf_std_limit or switches >= switch_limit:
        reason = f"std={conf_std:.3f}, switches={switches}"
        return True, reason

    return False, f"std={conf_std:.3f}, switches={switches}"


def speak(text):
    if not pyttsx3:
        st.warning("Text-to-speech is unavailable. Install pyttsx3 to enable it.")
        return
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        st.warning(f"Audio playback notice: {e}")


NUMBER_LABELS = [str(i) for i in range(10)]
NUMBER_WORDS = {
    "0": "ZERO",
    "1": "ONE",
    "2": "TWO",
    "3": "THREE",
    "4": "FOUR",
    "5": "FIVE",
    "6": "SIX",
    "7": "SEVEN",
    "8": "EIGHT",
    "9": "NINE",
}

if "sentence" not in st.session_state:
    st.session_state.sentence = []

if "last_prediction" not in st.session_state:
    st.session_state.last_prediction = None

if "last_added_by_label" not in st.session_state:
    st.session_state.last_added_by_label = {}

if "smart_lock_until" not in st.session_state:
    st.session_state.smart_lock_until = 0.0

# Load user-isolated personal dataset and model
db = load_db()
clf, model_labels, is_personal_model = load_trained_model()
total_user_samples = sum(len(v) for v in db.values())

# ── Studio Header Styling & User Workspace Banner ──────────────────────────────
st.markdown(
    f"""
    <style>
    .studio-user-bar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.85));
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 14px 22px;
        margin-bottom: 20px;
        backdrop-filter: blur(20px);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    }}
    .studio-user-left {{
        display: flex;
        align-items: center;
        gap: 14px;
    }}
    .studio-user-avatar {{
        font-size: 2rem;
        width: 48px;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(99, 102, 241, 0.18);
        border: 1px solid rgba(99, 102, 241, 0.35);
        border-radius: 14px;
    }}
    .studio-user-details h3 {{
        margin: 0;
        font-size: 1.15rem;
        font-weight: 700;
        color: #ffffff;
    }}
    .studio-user-meta {{
        font-size: 0.82rem;
        color: #94a3b8;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .vault-tag {{
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 2px 8px;
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 9999px;
        color: #6ee7b7;
        font-weight: 600;
        font-size: 0.75rem;
    }}
    .studio-user-right {{
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    .badge-chip {{
        padding: 6px 14px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        font-size: 0.82rem;
        color: #cbd5e1;
        font-weight: 600;
    }}
    </style>
    <div class="studio-user-bar">
        <div class="studio-user-left">
            <div class="studio-user-avatar">{avatar}</div>
            <div class="studio-user-details">
                <h3>{display_name}</h3>
                <div class="studio-user-meta">
                    <span>@{current_user}</span>
                    <span>&bull;</span>
                    <span class="vault-tag">🔒 Private Vault Active</span>
                </div>
            </div>
        </div>
        <div class="studio-user-right">
            <div class="badge-chip">📊 {len(db)} Labels ({total_user_samples} Samples)</div>
            <div class="badge-chip">{'🧠 Personal Model' if is_personal_model else '⚡ Baseline Classifier'}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar Account & Isolated Dataset Controls ──────────────────────────────
with st.sidebar:
    st.markdown(
        f"""
        <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 14px; padding: 14px 16px; margin-bottom: 16px;">
            <div style="font-size: 0.75rem; text-transform: uppercase; color: #818cf8; font-weight: 700; letter-spacing: 0.05em; margin-bottom: 6px;">Signed In As</div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.5rem;">{avatar}</span>
                <div>
                    <div style="font-weight: 700; font-size: 0.95rem; color: #f8fafc;">{display_name}</div>
                    <div style="font-size: 0.8rem; color: #94a3b8;">@{current_user}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("🚪 Sign Out", key="logout_btn", type="secondary", width="stretch"):
        st.session_state.authenticated_user = None
        st.session_state.user_info = None
        st.session_state.sentence = []
        st.session_state.last_prediction = None
        st.success("Signed out successfully.")
        st.rerun()

    st.markdown("---")
    st.header("Personal Dataset Builder")
    st.caption(f"All gestures collected here are saved strictly to **@{current_user}**'s personal storage.")

    mode = st.radio("Gesture mode", ["Custom labels", "Number signs (0-9)"], index=1)
    if mode == "Number signs (0-9)":
        label_name = st.selectbox("Label name", NUMBER_LABELS, index=1)
        st.info("Number mode is active. Save and train using digits 0-9.")
    else:
        label_name = st.text_input("Label name", value="HELLO")
    real_sample_count = st.slider("Samples to collect at once", 5, 50, 20, 1)
    conf_threshold = st.slider("Sentence confidence threshold", 0.3, 0.99, 0.65, 0.01)

    st.write(f"My Samples per label ({total_user_samples} total)")
    sample_stats = {k: len(v) for k, v in db.items()}
    st.json(sample_stats if sample_stats else {"No personal labels yet": 0})

    if not db:
        if st.button("📥 Import Starter Numbers (0-9)", help="Seed your personal account with starter number dataset"):
            user_data_manager.seed_user_db_from_global(current_user)
            st.success("Starter number dataset imported into your private vault!")
            st.rerun()

    if st.button("Clear my saved samples", type="secondary"):
        save_db({})
        st.success(f"All saved samples cleared for @{current_user}.")
        st.rerun()

# ── Studio Main View ──────────────────────────────────────────────────────────
st.title("Sign Language Detection Studio")
st.caption("Capture from camera, upload images, train personalized AI classifiers, and synthesize sign sentences.")

if db:
    if is_bootstrap_number_dataset(db):
        st.warning(
            "Bootstrap number dataset is active in your private vault. Number prediction is working, but adding your own camera samples will improve accuracy further."
        )
    else:
        st.success(f"Personal dataset active ({len(db)} labels, {total_user_samples} samples). Use Training Dashboard to inspect accuracy or train your personal model.")
else:
    st.info("No personal samples found yet. Use the sidebar to import starter numbers, or collect your own camera/upload samples.")

left, right = st.columns(2)

with left:
    st.subheader("Capture on Spot")
    cam_file = st.camera_input("Take a hand sign picture")

with right:
    st.subheader("Upload Image")
    upload_file = st.file_uploader("Upload a hand sign image", type=["png", "jpg", "jpeg"])

source_file = cam_file if cam_file is not None else upload_file

if source_file is not None:
    source_file = BytesIO(source_file.getvalue())
    image = bytes_to_bgr(source_file)
    if image is None:
        st.error("Unable to decode image. Try another image.")
    else:
        embedding, annotated = detect_hand_and_embedding(image)
        col_a, col_b = st.columns(2)
        col_a.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), caption="Input", width="stretch")
        col_b.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), caption="Detected Hand", width="stretch")

        if embedding is None:
            st.warning("No hand detected. Ensure your full hand is visible and well-lit.")
        else:
            add_sample_col, infer_col, sentence_col = st.columns(3)
            if add_sample_col.button(f"Save sample to {label_name.strip().upper()}"):
                db.setdefault(label_name.strip().upper(), []).append(embedding.tolist())
                save_db(db)
                st.success(f"Sample added to your personal label: {label_name.strip().upper()}")
                st.rerun()

            if st.button("Collect real samples now (augmented)"):
                collected = collect_samples_for_label(
                    db,
                    label_name,
                    embedding,
                    sample_count=real_sample_count,
                    include_original=True,
                )
                st.success(f"Collected {collected} samples for personal label: {label_name.strip().upper()}")
                st.rerun()

            pred_label, pred_conf, mode_used = predict_label(embedding, clf, model_labels, db)
            st.session_state.last_prediction = (pred_label, pred_conf, mode_used)

            if infer_col.button("Add prediction to sentence"):
                add_to_sentence(pred_label, pred_conf, conf_threshold)

            if sentence_col.button("Clear sentence"):
                st.session_state.sentence = []

# ── Real-Time Webcam Stream ──────────────────────────────────────────────────
st.subheader("Real-time Webcam Stream")

# Use the browser camera through WebRTC; server-side VideoCapture cannot access it.
try:
    from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
    import av
    _WEBRTC_AVAILABLE = True
except ImportError as _webrtc_error:
    _WEBRTC_AVAILABLE = False
    _WEBRTC_IMPORT_ERROR = _webrtc_error

rt_col1, rt_col2 = st.columns(2)
with rt_col1:
    run_realtime = st.checkbox("Enable live camera", value=True)
with rt_col2:
    realtime_mode = st.radio("Realtime action", ["Only predict", "Predict + auto add to sentence"], index=1)

smoothing_on = st.checkbox("Enable smoothing (majority vote)", value=True)
smoothing_window = st.slider("Smoothing window size", 3, 9, 5, 1)
conf_threshold_rt = st.slider("Realtime sentence confidence threshold", 0.3, 0.99, 0.65, 0.01)
cooldown_on = st.checkbox("Enable temporal cooldown", value=True)
cooldown_sec = st.slider("Cooldown per label (seconds)", 0.0, 5.0, 1.2, 0.1)

if run_realtime:
    if not _WEBRTC_AVAILABLE:
        st.error(
            "Live camera support is unavailable because streamlit-webrtc or PyAV "
            f"could not be imported: {_WEBRTC_IMPORT_ERROR}. Install the project "
            "dependencies and restart the app."
        )
    else:
        # ── WebRTC live camera processor ──────────────────────────────────────
        st.info("Allow camera access, then click **START** in the webcam panel to begin live detection.")

        _clf_snap = clf
        _model_labels_snap = model_labels
        _db_snap = db

        class HandSignProcessor(VideoProcessorBase):
            def __init__(self):
                self.prediction_history = deque(maxlen=smoothing_window)
                self.last_label = None
                self.last_conf = 0.0
                self.last_mode = ""
                self.hands = mp_hands.Hands(
                    static_image_mode=False,
                    max_num_hands=1,
                    min_detection_confidence=0.6,
                    min_tracking_confidence=0.6,
                )

            def recv(self, frame):
                img_bgr = frame.to_ndarray(format="bgr24")
                embedding, annotated = detect_hand_and_embedding(
                    img_bgr,
                    min_conf=0.6,
                    detector=self.hands,
                )
                if embedding is not None:
                    pred_label, pred_conf, mode_used = predict_label(
                        embedding, _clf_snap, _model_labels_snap, _db_snap
                    )
                    final_label, final_conf = pred_label, pred_conf
                    if smoothing_on:
                        self.prediction_history.append((pred_label, pred_conf))
                        sl, sc = smooth_prediction(self.prediction_history)
                        if sl is not None:
                            final_label, final_conf = sl, sc

                    self.last_label = final_label
                    self.last_conf = final_conf
                    self.last_mode = mode_used

                    cv2.putText(
                        annotated,
                        f"{final_label} ({final_conf:.2f})",
                        (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.2,
                        (0, 255, 80),
                        2,
                        cv2.LINE_AA,
                    )
                    return av.VideoFrame.from_ndarray(annotated, format="bgr24")
                else:
                    cv2.putText(
                        img_bgr,
                        "No hand detected",
                        (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.0,
                        (0, 80, 255),
                        2,
                        cv2.LINE_AA,
                    )
                    return av.VideoFrame.from_ndarray(img_bgr, format="bgr24")

            def on_ended(self):
                self.hands.close()

        RTC_CONFIG = RTCConfiguration(
            {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
        )

        ctx = webrtc_streamer(
            key="hand-sign-live",
            video_processor_factory=HandSignProcessor,
            rtc_configuration=RTC_CONFIG,
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True,
        )

        if ctx.video_processor and ctx.state.playing:
            proc = ctx.video_processor
            if proc.last_label:
                st.info(
                    f"🔍 Detected: **{proc.last_label}** | Confidence: {proc.last_conf:.2f} | Mode: {proc.last_mode}"
                )
                if realtime_mode == "Predict + auto add to sentence":
                    add_to_sentence_with_cooldown(
                        proc.last_label,
                        proc.last_conf,
                        conf_threshold_rt,
                        cooldown_sec=cooldown_sec if cooldown_on else 0.0,
                    )
                st.session_state.last_prediction = (
                    proc.last_label,
                    proc.last_conf,
                    proc.last_mode,
                )

# ── Prediction & Sentence Builder ─────────────────────────────────────────────
st.subheader("Prediction")
if st.session_state.last_prediction:
    label, conf, mode = st.session_state.last_prediction
    st.info(f"Mode: {mode} | Predicted: {label} | Confidence: {conf:.2f}")
else:
    st.write("Capture or upload an image to get prediction.")

st.subheader("Sentence Builder")
sentence = " ".join(st.session_state.sentence)
if sentence:
    display_sentence = " ".join(NUMBER_WORDS.get(token, token) for token in st.session_state.sentence)
    st.write(display_sentence)
else:
    st.write("Sentence is empty.")

word_map = {
    "H E L L O": "HELLO",
    "H I": "HI",
    "B Y E": "BYE",
}

detected_word = None
if st.session_state.sentence and all(token in NUMBER_LABELS for token in st.session_state.sentence):
    st.success(f"Number sequence detected: {' '.join(st.session_state.sentence)}")

if sentence in word_map:
    detected_word = word_map[sentence]
    st.success(f"Word Detected: {detected_word}")

act1, act2, act3 = st.columns(3)
if act1.button("🗣️ Speak Sentence"):
    if sentence:
        speak(" ".join(NUMBER_WORDS.get(token, token) for token in st.session_state.sentence))
    else:
        st.warning("Sentence is empty.")

if act2.button("💾 Save to My History"):
    if sentence:
        user_data_manager.save_user_sentence_item(current_user, sentence, detected_word)
        st.success("Sentence saved to your personal history!")
    else:
        st.warning("Sentence is empty.")

if act3.button("Clear Current Sentence"):
    st.session_state.sentence = []
    st.rerun()

# ── User's Personal Sentence History Archive ──────────────────────────────────
saved_sentences = user_data_manager.load_user_sentences(current_user)
with st.expander(f"📜 My Personal Saved Sentences Archive ({len(saved_sentences)} saved)"):
    if saved_sentences:
        for idx, item in enumerate(saved_sentences):
            word_badge = f" [Word: {item['detected_word']}]" if item.get("detected_word") else ""
            st.markdown(
                f"- **{item.get('text', '')}**{word_badge} &mdash; <span style='color:#64748b; font-size: 0.8rem;'>{item.get('timestamp', '')}</span>",
                unsafe_allow_html=True,
            )
        if st.button("Clear My Saved Sentences History", type="secondary"):
            user_data_manager.clear_user_sentences(current_user)
            st.success("Personal sentence history cleared.")
            st.rerun()
    else:
        st.caption("No sentences saved yet. Build a sentence above and click 'Save to My History'.")

# ── Training Dashboard ────────────────────────────────────────────────────────
st.subheader("Training Dashboard")
st.caption(f"Inspecting personal gesture repository for **@{current_user}**.")

if sample_stats:
    stats_df = pd.DataFrame(
        {"label": list(sample_stats.keys()), "samples": list(sample_stats.values())}
    ).sort_values("label")
    st.write("Per-label sample distribution")
    st.dataframe(stats_df, width="stretch")
    st.bar_chart(stats_df.set_index("label"))
else:
    st.info("No samples found yet. Save samples first to see dashboard metrics.")

# 1-Click Model Training directly in Studio
st.markdown("#### Personalized AI Model")
train_col1, train_col2 = st.columns([1, 1])

with train_col1:
    train_now = st.button("🚀 Train My Personal AI Model Now", type="primary")

with train_col2:
    st.caption(
        f"Trains an ensemble classifier (RandomForest + ExtraTrees) strictly on @{current_user}'s samples and saves to your private vault."
    )

if train_now:
    if total_user_samples < 10 or len(db) < 2:
        st.warning(f"Need at least 10 samples across at least 2 labels to train. You currently have {total_user_samples} samples across {len(db)} labels.")
    else:
        with st.spinner(f"Training personalized model for @{current_user}..."):
            train_ok, train_msg, rep = train_lstm.train_model_for_user(current_user, db)
            if train_ok:
                st.success(train_msg)
                if rep:
                    st.text(rep)
                st.rerun()
            else:
                st.error(f"Training failed: {train_msg}")

eval_col1, eval_col2 = st.columns(2)
with eval_col1:
    run_eval = st.button("Run Holdout Evaluation on My Data")
with eval_col2:
    st.caption("Uses stratified 80/20 split on your personal dataset for quality evaluation.")

if run_eval:
    if clf is None or model_labels is None:
        st.warning("Train a model first or import starter data to run evaluation.")
    else:
        eval_result, eval_error = evaluate_model_holdout(clf, db, model_labels)
        if eval_error:
            st.warning(eval_error)
        else:
            st.success(
                f"Holdout Accuracy: {eval_result['accuracy']:.3f} on {eval_result['test_samples']} test samples"
            )
            st.write("Confusion Matrix")
            st.dataframe(eval_result["cm_df"], width="stretch")
            st.write("Classification Report")
            st.dataframe(eval_result["report_df"], width="stretch")
            st.write("Misclassified Samples")
            if eval_result["mis_df"].empty:
                st.info("No misclassifications in this holdout split.")
            else:
                st.dataframe(eval_result["mis_df"], width="stretch")

# Personal Data Export
st.markdown("#### Personal Data Export")
exp_col1, exp_col2 = st.columns(2)
with exp_col1:
    st.download_button(
        "📥 Download My Personal embeddings.json",
        data=json.dumps(db, indent=2),
        file_name=f"embeddings_{current_user}.json",
        mime="application/json",
        key="download_personal_db",
    )
with exp_col2:
    st.download_button(
        "📥 Download My Sentences History (JSON)",
        data=json.dumps(saved_sentences, indent=2),
        file_name=f"sentences_{current_user}.json",
        mime="application/json",
        key="download_personal_sentences",
    )

st.markdown("---")
st.markdown(
    """
    <div style="background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(168,85,247,0.1)); border: 1px solid rgba(99,102,241,0.25); border-radius: 14px; padding: 18px 24px; margin: 15px 0;">
        <h4 style="margin: 0 0 6px 0; color: #a5b4fc; font-weight: 600;">📖 Sign Language Manual Guide</h4>
        <p style="margin: 0; color: #cbd5e1; font-size: 0.95rem;">
            Need visual help making hand signs for Numbers, Alphabets, or Common Phrases? 
            Access the full visual guide anytime from the top-right <strong>⋮ (three-dot) menu &rarr; Manual Guide</strong>, or 
            <a href="/Manual_Guide" target="_blank" style="color:#38bdf8; text-decoration: underline; font-weight: 500;">open Manual Guide in a new tab &nearr;</a>.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")
st.markdown("### Advanced Features Included")
st.markdown("- **User Authentication & Isolation**: Individual logins, registration, and private dataset vaults")
st.markdown("- **Dual Input Modes**: Real-time camera capture and image upload")
st.markdown("- **Instant Model Personalization**: Train custom RandomForest + ExtraTrees ensembles in 1-click")
st.markdown("- **Confidence-Gated Sentence Builder**: Text-to-speech engine and personal translation history archive")
st.markdown("- **Real-time Webcam Stream**: Frame smoothing, adaptive cooldown, and confidence-trend smart locks")
