"""
pages/1_📖_Manual_Guide.py
Sign Language Manual Guide – standalone HTML/CSS/JS page rendered inside Streamlit.
"""

import base64
import mimetypes
import os

import streamlit as st

st.set_page_config(
    page_title="Sign Language Manual Guide",
    layout="wide",
    page_icon="📖",
)

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

# ── Asset paths ──────────────────────────────────────────────────────────────
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CANDIDATE_ASSETS = os.path.join(_PROJECT_ROOT, "assets", "signs")
GUIDE_ASSETS_DIR = _CANDIDATE_ASSETS if os.path.exists(_CANDIDATE_ASSETS) else os.path.join("assets", "signs")
NUMBERS_IMG_DIR = os.path.join(GUIDE_ASSETS_DIR, "numbers")
ALPHABETS_IMG_DIR = os.path.join(GUIDE_ASSETS_DIR, "alphabets")
PHRASES_IMG_DIR = os.path.join(GUIDE_ASSETS_DIR, "phrases")

# ── Sign data (mirrors app.py) ───────────────────────────────────────────────

NUMBERS_GUIDE = {
    "0": {
        "how": "Curl all fingers to touch the thumb tip, forming a circle (like an 'O' shape). No finger points straight up.",
        "tip": "Make sure all fingertips touch the thumb. The hand looks like a round zero.",
    },
    "1": {
        "how": "Extend index finger straight up. Keep thumb, middle, ring, and pinky folded into the palm.",
        "tip": "Only one finger up — the pointer finger. Keep the rest tightly closed.",
    },
    "2": {
        "how": "Extend index and middle fingers upward. Ring finger, pinky, and thumb stay folded.",
        "tip": "Classic peace sign. Two fingers pointing up, spread slightly apart.",
    },
    "3": {
        "how": "Extend thumb, index, and middle fingers. Ring and pinky fingers stay folded into the palm.",
        "tip": "Thumb sticks out to the side while index and middle point up.",
    },
    "4": {
        "how": "Extend index, middle, ring, and pinky fingers upward. Thumb folds across the palm.",
        "tip": "Four fingers up, spread out. Thumb is tucked. All four fingers should be visible.",
    },
    "5": {
        "how": "Spread all five fingers wide open — thumb, index, middle, ring, and pinky all extended.",
        "tip": "Open palm facing camera. Maximum spread for all fingers.",
    },
    "6": {
        "how": "Extend thumb and pinky, fold in index, middle, and ring fingers into the palm.",
        "tip": "Shaka or 'hang loose' sign. Thumb and pinky only.",
    },
    "7": {
        "how": "Extend thumb, index, and middle fingers with the middle finger bent slightly down touching the thumb.",
        "tip": "Thumb touches middle fingertip. Index stays straight up. Ring and pinky folded.",
    },
    "8": {
        "how": "Extend thumb and index finger in an 'L' shape, with the other three fingers loosely curled.",
        "tip": "Like a gun shape. Thumb horizontal, index points forward. Middle/ring/pinky loosely closed.",
    },
    "9": {
        "how": "Curl index finger to touch the thumb tip (like an 'OK' sign). Middle, ring, and pinky extended upward.",
        "tip": "Index and thumb make a loop. Three fingers extend up. Looks like the number 9.",
    },
}

ALPHABETS_GUIDE = {
    "A": {"how": "Make a fist with fingers curled. Thumb rests on the side of the fist, pointing up.", "tip": "Tight fist, thumb visible on the side."},
    "B": {"how": "Hold all four fingers straight up together, thumb folded flat across the palm.", "tip": "Four fingers together pointing up, thumb tucked inside."},
    "C": {"how": "Curve all fingers and thumb into a 'C' shape (like holding a ball).", "tip": "Rounded C-shape with palm facing sideways."},
    "D": {"how": "Touch index finger tip to thumb tip (making a loop). Middle, ring, pinky extend straight up.", "tip": "Index and thumb form a D-loop. Three fingers up."},
    "E": {"how": "Curl all four fingers down so fingertips touch the thumb. Fingers are hooked.", "tip": "All fingers bent inward, fingertips touching thumb."},
    "F": {"how": "Touch index finger tip to thumb tip. Other three fingers (middle, ring, pinky) spread open.", "tip": "OK-like loop with index and thumb, three fingers spread wide."},
    "G": {"how": "Point index finger sideways (horizontally) with thumb extended. Other fingers folded.", "tip": "Index and thumb both horizontal, pointing to the side."},
    "H": {"how": "Extend index and middle fingers horizontally together pointing sideways.", "tip": "Two fingers pointing to the side, flat and parallel."},
    "I": {"how": "Raise pinky finger only. All other fingers folded into palm. Thumb tucked.", "tip": "Only the little (pinky) finger extends up."},
    "J": {"how": "Start like I (pinky up), then draw a J shape in the air by moving the wrist down and curling.", "tip": "It's a motion sign — pinky traces the letter J in the air."},
    "K": {"how": "Extend index and middle fingers in a 'V', with thumb between them touching the middle finger.", "tip": "Peace sign but thumb is between index and middle."},
    "L": {"how": "Extend index finger straight up and thumb horizontal — forming an L-shape.", "tip": "Classic L-shape. Like a gun but only two fingers, index up and thumb out."},
    "M": {"how": "Fold index, middle, and ring fingers over the thumb. Pinky folded. Thumb is under the three fingers.", "tip": "Three fingers over the thumb — the bumps represent M's three humps."},
    "N": {"how": "Fold index and middle fingers over the thumb. Ring and pinky folded. Thumb under two fingers.", "tip": "Two fingers over the thumb — like M but with two fingers (N has two humps)."},
    "O": {"how": "Curve all fingers to meet the thumb, forming a round 'O' shape.", "tip": "Like the number 0 sign. All fingertips touch the thumb forming a circle."},
    "P": {"how": "Like K but rotated — index finger points down, middle up, thumb touches middle.", "tip": "K sign flipped downward. Index points down, middle extends up."},
    "Q": {"how": "Like G but rotated downward — index and thumb point downward.", "tip": "G sign flipped so index and thumb point toward the ground."},
    "R": {"how": "Cross index and middle fingers (like crossing your fingers for luck). Other fingers folded.", "tip": "Index and middle fingers crossed — classic R shape."},
    "S": {"how": "Make a fist with the thumb wrapped over the folded fingers (not under them).", "tip": "Fist with thumb on top of the fingers, not to the side like A."},
    "T": {"how": "Make a fist with the thumb tucked between index and middle fingers.", "tip": "Thumb peeks between index and middle fingers."},
    "U": {"how": "Extend index and middle fingers straight up, held together (not spread). Other fingers folded.", "tip": "Two fingers up, side by side touching. No gap between them."},
    "V": {"how": "Extend index and middle fingers in a V (peace sign). Fingers spread apart.", "tip": "Classic peace/victory sign — two fingers spread in a V shape."},
    "W": {"how": "Extend index, middle, and ring fingers spread apart into a W shape.", "tip": "Three fingers spread wide — like V but with one extra finger."},
    "X": {"how": "Bend (hook) the index finger into a hook shape. Other fingers folded.", "tip": "Only index finger is out, curled like a hook or claw."},
    "Y": {"how": "Extend thumb and pinky (shaka/hang-loose). Index, middle, ring folded.", "tip": "Thumb and pinky out, three middle fingers tucked in."},
    "Z": {"how": "Point index finger and draw the letter Z in the air with a zigzag motion.", "tip": "Motion sign — index traces Z: left → diagonal down-right → left again."},
}

PHRASES_GUIDE = {
    "HELLO": {
        "how": "Hold hand flat near forehead with palm facing out, then wave it sideways away from the forehead (like a salute-wave).",
        "label": "HELLO",
        "tip": "Start with a flat hand at forehead level, then sweep outward.",
    },
    "THANK YOU": {
        "how": "Touch flat fingers to lips/chin, then move the hand forward and downward — like blowing a kiss toward someone.",
        "label": "THANKS",
        "tip": "Start at chin with flat hand, extend forward gracefully.",
    },
    "PLEASE": {
        "how": "Place flat hand on chest and move it in a circular motion (clockwise).",
        "label": "PLEASE",
        "tip": "Rub your chest in a circle with a flat hand.",
    },
    "YES": {
        "how": "Make a fist and nod it up and down — mimicking a head nodding yes.",
        "label": "YES",
        "tip": "Fist bobbing up and down. Simple nod motion with the hand.",
    },
    "NO": {
        "how": "Extend index and middle fingers and tap them against the thumb twice — like a snapping motion.",
        "label": "NO",
        "tip": "Index and middle meet thumb repeatedly. Like snapping without sound.",
    },
    "SORRY": {
        "how": "Make a fist and rub it in a circular motion on the chest (clockwise).",
        "label": "SORRY",
        "tip": "Like 'please' but uses a fist. Rubbing fist on chest.",
    },
    "HELP": {
        "how": "Place thumb up fist (like a thumbs-up) on the open palm of the other hand, then lift both hands upward together.",
        "label": "HELP",
        "tip": "Thumbs-up hand riding on an open palm, both moving upward.",
    },
    "GOOD": {
        "how": "Touch flat fingers to chin/lips, then bring hand forward with palm facing up — like presenting something good.",
        "label": "GOOD",
        "tip": "Similar to thank you but ends with palm facing up toward receiver.",
    },
    "BAD": {
        "how": "Touch flat fingers to chin, then flip hand down so fingers point downward.",
        "label": "BAD",
        "tip": "Like GOOD but the hand flips downward at the end.",
    },
    "I LOVE YOU": {
        "how": "Extend thumb, index, and pinky while keeping middle and ring fingers folded. Hold still.",
        "label": "ILY",
        "tip": "Combines I (pinky), L (index+thumb), Y (pinky+thumb) into one handshape.",
    },
    "WATER": {
        "how": "Form a W (three fingers spread) and tap it to the chin twice.",
        "label": "WATER",
        "tip": "W handshape tapping chin. Three fingers spread, touch chin.",
    },
    "FOOD / EAT": {
        "how": "Bring flattened fingers and thumb together (like pinching) and tap them to the mouth twice.",
        "label": "EAT",
        "tip": "Pinch fingers to mouth — like putting food in your mouth.",
    },
}


# ── Image helpers ─────────────────────────────────────────────────────────────

def find_sign_image(folder, label):
    """Search for label image with various extensions and casing."""
    candidates = [
        f"{label}.png", f"{label}.jpg", f"{label}.jpeg", f"{label}.webp", f"{label}.svg",
        f"{label.lower()}.png", f"{label.lower()}.jpg", f"{label.lower()}.jpeg",
        f"{label.lower()}.webp", f"{label.lower()}.svg",
        f"{label.upper()}.png", f"{label.upper()}.jpg", f"{label.upper()}.jpeg",
        f"{label.upper()}.webp", f"{label.upper()}.svg",
    ]
    for c in candidates:
        p = os.path.join(folder, c)
        if os.path.exists(p):
            return p
    return None


def img_to_data_uri(img_path):
    """Convert local image to a base64 data URI string."""
    if not img_path or not os.path.exists(img_path):
        return None
    if img_path.lower().endswith(".svg"):
        mime = "image/svg+xml"
    else:
        mime, _ = mimetypes.guess_type(img_path)
        if not mime:
            mime = "image/png"
    try:
        with open(img_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        return f"data:{mime};base64,{data}"
    except Exception:
        return None


# ── Build JS data arrays ──────────────────────────────────────────────────────

def build_numbers_js():
    rows = []
    for digit, info in NUMBERS_GUIDE.items():
        img_path = find_sign_image(NUMBERS_IMG_DIR, digit)
        uri = img_to_data_uri(img_path) or ""
        rows.append({
            "id": digit,
            "title": f"Number {digit}",
            "how": info["how"],
            "tip": info["tip"],
            "img": uri,
            "motion": False,
        })
    return rows


def build_alphabets_js():
    motion_signs = {"J", "Z"}
    rows = []
    for letter, info in ALPHABETS_GUIDE.items():
        img_path = find_sign_image(ALPHABETS_IMG_DIR, letter)
        uri = img_to_data_uri(img_path) or ""
        rows.append({
            "id": letter,
            "title": f"Letter {letter}",
            "how": info["how"],
            "tip": info["tip"],
            "img": uri,
            "motion": letter in motion_signs,
        })
    return rows


def build_phrases_js():
    rows = []
    for phrase, info in PHRASES_GUIDE.items():
        phrase_key = phrase.replace(" ", "_").replace("/", "_")
        img_path = (
            find_sign_image(PHRASES_IMG_DIR, info["label"])
            or find_sign_image(PHRASES_IMG_DIR, phrase_key)
            or find_sign_image(PHRASES_IMG_DIR, phrase)
        )
        uri = img_to_data_uri(img_path) or ""
        rows.append({
            "id": info["label"],
            "title": phrase,
            "label": info["label"],
            "how": info["how"],
            "tip": info["tip"],
            "img": uri,
            "motion": False,
        })
    return rows


import json as _json

numbers_data = _json.dumps(build_numbers_js())
alphabets_data = _json.dumps(build_alphabets_js())
phrases_data = _json.dumps(build_phrases_js())

# ── HTML/CSS/JS Template ──────────────────────────────────────────────────────

HTML = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Sign Language Manual Guide</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet"/>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  :root {{
    --bg:       #0b0f1a;
    --surface:  #111827;
    --card:     #161d2e;
    --border:   #1e293b;
    --accent1:  #6366f1;
    --accent2:  #8b5cf6;
    --accent3:  #06b6d4;
    --text:     #e2e8f0;
    --muted:    #94a3b8;
    --tip-bg:   rgba(99,102,241,0.12);
    --motion-bg:#fef3c7;
    --motion-tx:#92400e;
    --radius:   14px;
    --shadow:   0 4px 24px rgba(0,0,0,0.45);
  }}

  html {{ scroll-behavior: smooth; }}

  body {{
    font-family: 'Inter', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    padding: 0 0 60px;
    /* Prevent any inner iframe scroll */
    overflow: visible;
  }}

  /* ── Header — no sticky: outer Streamlit page scrolls, not the iframe ── */
  .header {{
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    border-bottom: 1px solid var(--border);
    padding: 32px 32px 20px;
    position: relative;
    z-index: 100;
  }}
  .header-inner {{ max-width: 1400px; margin: 0 auto; }}
  .header h1 {{
    font-size: 2rem; font-weight: 800;
    background: linear-gradient(90deg, #a5b4fc, #c084fc, #67e8f9);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 6px;
  }}
  .header p {{ color: var(--muted); font-size: 0.95rem; margin-bottom: 18px; }}

  /* ── Search ── */
  .search-wrap {{ position: relative; max-width: 420px; }}
  .search-wrap svg {{ position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--muted); pointer-events: none; }}
  #searchInput {{
    width: 100%; padding: 11px 16px 11px 42px;
    background: rgba(255,255,255,0.05); border: 1px solid var(--border);
    border-radius: 50px; color: var(--text); font-size: 0.95rem;
    outline: none; transition: border-color .2s, box-shadow .2s;
  }}
  #searchInput:focus {{ border-color: var(--accent1); box-shadow: 0 0 0 3px rgba(99,102,241,0.2); }}
  #searchInput::placeholder {{ color: var(--muted); }}

  /* ── Tabs ── */
  .tabs-bar {{
    max-width: 1400px; margin: 0 auto;
    display: flex; gap: 8px;
    padding: 20px 32px 0;
  }}
  .tab-btn {{
    padding: 10px 26px; border-radius: 50px; border: 1px solid var(--border);
    background: transparent; color: var(--muted); font-size: 0.92rem; font-weight: 500;
    cursor: pointer; transition: all .22s; white-space: nowrap;
    font-family: 'Inter', sans-serif;
  }}
  .tab-btn:hover {{ color: var(--text); border-color: var(--accent1); background: rgba(99,102,241,0.08); }}
  .tab-btn.active {{
    background: linear-gradient(135deg, var(--accent1), var(--accent2));
    border-color: transparent; color: #fff; box-shadow: 0 4px 16px rgba(99,102,241,0.35);
  }}

  /* ── Tab panels ── */
  .tab-panel {{ display: none; max-width: 1400px; margin: 0 auto; padding: 28px 32px; }}
  .tab-panel.active {{ display: block; animation: fadeIn .3s ease; }}
  @keyframes fadeIn {{ from {{ opacity:0; transform:translateY(8px) }} to {{ opacity:1; transform:none }} }}

  /* ── Section heading ── */
  .section-title {{ font-size: 1.4rem; font-weight: 700; margin-bottom: 6px; }}
  .section-sub {{ color: var(--muted); font-size: 0.88rem; margin-bottom: 20px; }}

  /* ── Info banner ── */
  .info-banner {{
    display: flex; align-items: flex-start; gap: 10px;
    background: rgba(6,182,212,0.1); border: 1px solid rgba(6,182,212,0.3);
    border-radius: 10px; padding: 12px 16px;
    color: #67e8f9; font-size: 0.88rem; margin-bottom: 22px;
    line-height: 1.5;
  }}
  .info-banner svg {{ flex-shrink: 0; margin-top: 2px; }}

  .warn-banner {{
    display: flex; align-items: flex-start; gap: 10px;
    background: rgba(251,191,36,0.1); border: 1px solid rgba(251,191,36,0.3);
    border-radius: 10px; padding: 12px 16px;
    color: #fbbf24; font-size: 0.88rem; margin-bottom: 22px;
    line-height: 1.5;
  }}

  /* ── Grid ── */
  .grid-2 {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 20px; }}
  .grid-3 {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 18px; }}

  /* ── Sign Card ── */
  .sign-card {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 20px;
    box-shadow: var(--shadow);
    transition: transform .2s, border-color .2s, box-shadow .2s;
    position: relative; overflow: hidden;
  }}
  .sign-card::before {{
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, var(--accent1), var(--accent2), var(--accent3));
    opacity: 0; transition: opacity .2s;
  }}
  .sign-card:hover {{ transform: translateY(-3px); border-color: var(--accent1); box-shadow: 0 8px 32px rgba(99,102,241,0.2); }}
  .sign-card:hover::before {{ opacity: 1; }}

  .card-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 14px; }}
  .card-title {{ font-size: 1.3rem; font-weight: 700; }}
  .card-label-badge {{
    font-size: 0.75rem; background: rgba(99,102,241,0.15); border: 1px solid rgba(99,102,241,0.3);
    color: #a5b4fc; border-radius: 20px; padding: 3px 10px; white-space: nowrap;
  }}
  .motion-badge {{
    display: inline-block; font-size: 0.72rem; background: rgba(251,191,36,0.15);
    border: 1px solid rgba(251,191,36,0.3); color: #fbbf24;
    border-radius: 20px; padding: 2px 9px; margin-left: 8px; vertical-align: middle;
  }}

  /* ── Image area ── */
  .img-area {{
    background: rgba(255,255,255,0.03); border: 1px dashed var(--border);
    border-radius: 10px; min-height: 160px;
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 14px; overflow: hidden;
  }}
  .img-area img {{ max-height: 200px; max-width: 100%; object-fit: contain; border-radius: 8px; }}
  .img-placeholder {{
    text-align: center; color: var(--muted); font-size: 0.82rem; padding: 20px;
  }}
  .img-placeholder .icon {{ font-size: 2rem; margin-bottom: 6px; display: block; }}

  /* ── How & tip text ── */
  .how-label {{ font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: .05em; color: var(--muted); margin-bottom: 4px; }}
  .how-text {{ font-size: 0.91rem; color: var(--text); line-height: 1.6; margin-bottom: 12px; }}
  .tip-box {{
    background: var(--tip-bg); border-left: 3px solid var(--accent1);
    border-radius: 0 8px 8px 0; padding: 8px 12px;
    font-size: 0.85rem; color: #a5b4fc; line-height: 1.5;
  }}
  .tip-box::before {{ content: '💡 '; }}

  /* ── Training steps ── */
  .steps-box {{
    background: rgba(99,102,241,0.07); border: 1px solid rgba(99,102,241,0.2);
    border-radius: 12px; padding: 20px; margin-top: 32px;
  }}
  .steps-box h3 {{ font-size: 1rem; font-weight: 700; margin-bottom: 12px; color: #a5b4fc; }}
  .steps-box ol {{ padding-left: 20px; color: var(--muted); font-size: 0.9rem; line-height: 1.9; }}
  .steps-box ol li strong {{ color: var(--text); }}

  /* ── No-results ── */
  .no-results {{ text-align: center; color: var(--muted); padding: 60px 20px; font-size: 1rem; }}
  .no-results span {{ display: block; font-size: 2.5rem; margin-bottom: 10px; }}

  /* ── No inner scrollbar needed — outer Streamlit page scrolls ── */
  ::-webkit-scrollbar {{ width: 0; }}

  @media (max-width: 600px) {{
    .header {{ padding: 20px 16px 16px; }}
    .tabs-bar {{ padding: 14px 16px 0; }}
    .tab-panel {{ padding: 20px 16px; }}
    .header h1 {{ font-size: 1.5rem; }}
    .grid-2, .grid-3 {{ grid-template-columns: 1fr; }}
  }}
  .back-link {{
    display: inline-flex; align-items: center; gap: 8px;
    color: #a5b4fc; text-decoration: none; font-size: 0.88rem; font-weight: 600;
    padding: 7px 16px; border-radius: 50px;
    background: rgba(99,102,241,0.14); border: 1px solid rgba(99,102,241,0.3);
    transition: all .2s; margin-bottom: 12px;
  }}
  .back-link:hover {{
    background: rgba(99,102,241,0.28); color: #fff;
    transform: translateX(-3px); box-shadow: 0 4px 14px rgba(99,102,241,0.3);
  }}
</style>
<!-- Auto-resize: send full content height to Streamlit so iframe has no inner scroll -->
<script>
  function notifyHeight() {{
    const h = document.documentElement.scrollHeight || document.body.scrollHeight;
    window.parent.postMessage({{type: 'streamlit:setFrameHeight', height: h}}, '*');
  }}
  // Fire immediately and after any DOM/image changes
  document.addEventListener('DOMContentLoaded', notifyHeight);
  window.addEventListener('load', notifyHeight);
  // Re-notify whenever tab buttons or search change visible content
  const _ro = new ResizeObserver(notifyHeight);
  document.addEventListener('DOMContentLoaded', function() {{
    _ro.observe(document.body);
    // Also fire on every tab / search interaction
    document.addEventListener('click', function() {{ setTimeout(notifyHeight, 80); }});
    document.addEventListener('input', function() {{ setTimeout(notifyHeight, 80); }});
  }});
</script>
</head>
<body>

<div class="header">
  <div class="header-inner">
    <div>
      <a href="/" target="_self" class="back-link">
        <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        Back to Detection Studio
      </a>
    </div>
    <h1>📖 Sign Language Manual Guide</h1>
    <p>Learn hand positions for numbers, alphabets, and common phrases. Use this guide to train your own model.</p>
    <div class="search-wrap">
      <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
      </svg>
      <input id="searchInput" type="text" placeholder="Search signs..." oninput="filterCards(this.value)"/>
    </div>
  </div>
</div>

<div class="tabs-bar">
  <button class="tab-btn active" onclick="switchTab('numbers', this)" id="tab-numbers">🔢 Numbers (0–9)</button>
  <button class="tab-btn" onclick="switchTab('alphabets', this)" id="tab-alphabets">🔤 Alphabets (A–Z)</button>
  <button class="tab-btn" onclick="switchTab('phrases', this)" id="tab-phrases">💬 Common Phrases</button>
</div>

<!-- ── Numbers Panel ── -->
<div class="tab-panel active" id="panel-numbers">
  <div class="section-title">Hand Signs for Numbers 0–9</div>
  <div class="section-sub">Learn each number sign and capture it with your camera to build your dataset.</div>
  <div class="info-banner">
    <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
      <circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>
    </svg>
    Place sign images in <code style="background:rgba(255,255,255,0.08);padding:1px 6px;border-radius:4px;font-size:0.85em">assets/signs/numbers/</code>
    &nbsp;— supported formats: .svg, .png, .jpg, .jpeg, .webp
  </div>
  <div class="grid-2" id="grid-numbers"></div>
  <div class="steps-box" id="steps-numbers">
    <h3>Training Steps for Numbers</h3>
    <ol>
      <li>Look at the sign description and image above</li>
      <li>Practice the hand position in front of your camera</li>
      <li>Go to <strong>Sign Language Studio</strong> (main page) and set your label</li>
      <li>Use <strong>Capture on Spot</strong> → take a photo → click <strong>Save sample to label</strong></li>
      <li>Repeat for all 10 digits (0–9)</li>
      <li>Once done, run <code style="background:rgba(255,255,255,0.08);padding:1px 6px;border-radius:4px">python train_lstm.py</code> from terminal to train the model</li>
    </ol>
  </div>
</div>

<!-- ── Alphabets Panel ── -->
<div class="tab-panel" id="panel-alphabets">
  <div class="section-title">ASL Hand Signs for Alphabets A–Z</div>
  <div class="section-sub">Static and motion signs for the full English alphabet.</div>
  <div class="info-banner">
    <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
      <circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>
    </svg>
    Place sign images in <code style="background:rgba(255,255,255,0.08);padding:1px 6px;border-radius:4px;font-size:0.85em">assets/signs/alphabets/</code>
    &nbsp;— supported formats: .svg, .png, .jpg, .jpeg, .webp
  </div>
  <div class="warn-banner">
    <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
      <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><path d="M12 9v4M12 17h.01"/>
    </svg>
    <strong>Motion signs:</strong>&nbsp; Letters <strong>J</strong> and <strong>Z</strong> are drawn in the air. Capture the starting position of the motion for training.
  </div>
  <div class="grid-3" id="grid-alphabets"></div>
  <div class="steps-box" id="steps-alphabets">
    <h3>Full Alphabet Training Workflow</h3>
    <ol>
      <li>Start with easy letters: <strong>A, B, C, L, O, V, Y</strong></li>
      <li>Go to the <strong>Sign Language Studio</strong> main page and set the label</li>
      <li>Head to <strong>Capture on Spot</strong> and take a photo</li>
      <li>Click <strong>Save sample to label</strong> (or <strong>Collect real samples now</strong> for more data)</li>
      <li>Repeat for each letter</li>
      <li>Train the model via <code style="background:rgba(255,255,255,0.08);padding:1px 6px;border-radius:4px">python train_lstm.py</code> when you have 5+ samples per letter</li>
    </ol>
  </div>
</div>

<!-- ── Phrases Panel ── -->
<div class="tab-panel" id="panel-phrases">
  <div class="section-title">Common Sign Language Phrases</div>
  <div class="section-sub">Everyday signs for greetings, expressions, and essential communication.</div>
  <div class="info-banner">
    <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
      <circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>
    </svg>
    Place sign images in <code style="background:rgba(255,255,255,0.08);padding:1px 6px;border-radius:4px;font-size:0.85em">assets/signs/phrases/</code>
    &nbsp;— supported formats: .svg, .png, .jpg, .jpeg, .webp
  </div>
  <div class="info-banner" style="background:rgba(139,92,246,0.1);border-color:rgba(139,92,246,0.3);color:#c4b5fd;">
    <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
    </svg>
    Many phrase signs involve <strong>motion</strong>. Capture the <strong>key frame</strong> — the most distinctive hand position in the gesture.
  </div>
  <div class="grid-2" id="grid-phrases"></div>
  <div class="steps-box" id="steps-phrases">
    <h3>Training Tips for Phrases</h3>
    <ol>
      <li>Read the description and study the key hand position</li>
      <li>Go to <strong>Sign Language Studio</strong> and set the label to the phrase label shown on the card</li>
      <li>Make the hand shape, freeze at the key frame, then capture</li>
      <li>Collect at least 10–20 samples per phrase for reliable detection</li>
    </ol>
  </div>
</div>

<script>
const NUMBERS   = {numbers_data};
const ALPHABETS = {alphabets_data};
const PHRASES   = {phrases_data};

function escHtml(s) {{
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}}

function buildCard(item, size) {{
  const motionBadge = item.motion ? '<span class="motion-badge">Motion</span>' : '';
  const imgHtml = item.img
    ? `<img src="${{escHtml(item.img)}}" alt="${{escHtml(item.title)}}" loading="lazy"/>`
    : `<div class="img-placeholder"><span class="icon">🖐️</span>No image added yet</div>`;

  const labelBadge = item.label
    ? `<span class="card-label-badge">Label: ${{escHtml(item.label)}}</span>`
    : '';

  return `
    <div class="sign-card" data-search="${{escHtml((item.title + ' ' + item.how + ' ' + item.tip).toLowerCase())}}">
      <div class="card-header">
        <div>
          <div class="card-title">${{escHtml(item.title)}}${{motionBadge}}</div>
          ${{labelBadge}}
        </div>
      </div>
      <div class="img-area">${{imgHtml}}</div>
      <div class="how-label">How to sign</div>
      <div class="how-text">${{escHtml(item.how)}}</div>
      <div class="tip-box">${{escHtml(item.tip)}}</div>
    </div>`;
}}

function renderGrid(containerId, data, size) {{
  const grid = document.getElementById(containerId);
  grid.innerHTML = data.map(d => buildCard(d, size)).join('');
}}

renderGrid('grid-numbers',   NUMBERS,   2);
renderGrid('grid-alphabets', ALPHABETS, 3);
renderGrid('grid-phrases',   PHRASES,   2);

// ── Tab switching ──
let activeTab = 'numbers';
function switchTab(name, btn) {{
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('panel-' + name).classList.add('active');
  btn.classList.add('active');
  activeTab = name;
  filterCards(document.getElementById('searchInput').value);
}}

// ── Search / Filter ──
function filterCards(query) {{
  query = query.trim().toLowerCase();
  const gridId = 'grid-' + activeTab;
  const stepsId = 'steps-' + activeTab;
  const grid = document.getElementById(gridId);
  if (!grid) return;

  let visible = 0;
  grid.querySelectorAll('.sign-card').forEach(card => {{
    const match = !query || card.dataset.search.includes(query);
    card.style.display = match ? '' : 'none';
    if (match) visible++;
  }});

  // remove old no-results
  const old = grid.querySelector('.no-results');
  if (old) old.remove();
  if (visible === 0 && query) {{
    grid.insertAdjacentHTML('afterbegin', `<div class="no-results" style="grid-column:1/-1"><span>🔍</span>No signs match "<strong>${{escHtml(query)}}"</strong></div>`);
  }}

  if (document.getElementById(stepsId)) {{
    document.getElementById(stepsId).style.display = query ? 'none' : '';
  }}
}}
</script>
</body>
</html>
"""

# ── Navigation bar & User status ──────────────────────────────────────────────
nav_col1, nav_col2 = st.columns([1, 1])
with nav_col1:
    st.markdown("[← Return to Sign Language Studio](/)")
with nav_col2:
    current_u = st.session_state.get("authenticated_user")
    if current_u:
        u_info = st.session_state.get("user_info") or {}
        st.markdown(
            f"<div style='text-align: right; color: #a5b4fc; font-size: 0.9rem;'>"
            f"👤 Workspace: <strong>{u_info.get('avatar', '🧑‍💻')} {u_info.get('display_name', current_u)}</strong> (@{current_u})"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div style='text-align: right; color: #94a3b8; font-size: 0.85rem;'><a href='/' target='_self'>Sign in to Studio</a></div>",
            unsafe_allow_html=True,
        )

# ── Render ─────────────────────────────────────────────────────────────────────
# st.iframe with height="content" automatically resizes to full content height,
# eliminating any nested/inner scrollbars so only the main page scrolls.
st.iframe(HTML, height="content")

