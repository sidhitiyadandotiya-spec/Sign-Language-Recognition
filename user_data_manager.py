import json
import os
import shutil
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
GLOBAL_DB_PATH = os.path.join(DATA_DIR, "embeddings.json")
GLOBAL_MODEL_DIR = os.path.join(BASE_DIR, "model")
GLOBAL_MODEL_PATH = os.path.join(GLOBAL_MODEL_DIR, "gesture_rf.joblib")
GLOBAL_LABELS_PATH = os.path.join(GLOBAL_MODEL_DIR, "labels.json")

USER_DATA_ROOT = os.path.join(DATA_DIR, "user_data")


def get_user_root(username: str) -> str:
    """Get the isolated directory for a specific user."""
    safe_username = "".join(c for c in username.lower() if c.isalnum() or c in ("_", "-"))
    user_dir = os.path.join(USER_DATA_ROOT, safe_username)
    os.makedirs(user_dir, exist_ok=True)
    os.makedirs(os.path.join(user_dir, "model"), exist_ok=True)
    return user_dir


def get_user_db_path(username: str) -> str:
    """Return the file path for the user's personal embeddings database."""
    return os.path.join(get_user_root(username), "embeddings.json")


def get_user_sentences_path(username: str) -> str:
    """Return the file path for the user's saved sentences and translations."""
    return os.path.join(get_user_root(username), "sentences.json")


def get_user_model_paths(username: str) -> Tuple[Optional[str], Optional[str], bool]:
    """
    Return (model_path, labels_path, is_personal_model).
    Prioritizes user's own trained model. Falls back to global model if available.
    """
    user_root = get_user_root(username)
    user_model = os.path.join(user_root, "model", "gesture_rf.joblib")
    user_labels = os.path.join(user_root, "model", "labels.json")

    if os.path.exists(user_model) and os.path.exists(user_labels):
        return user_model, user_labels, True

    if os.path.exists(GLOBAL_MODEL_PATH) and os.path.exists(GLOBAL_LABELS_PATH):
        return GLOBAL_MODEL_PATH, GLOBAL_LABELS_PATH, False

    return None, None, False


def load_user_db(username: str, seed_if_empty: bool = True) -> Dict[str, List[List[float]]]:
    """
    Load a user's isolated embeddings database.
    If it doesn't exist and seed_if_empty is True, seeds from global embeddings.json.
    """
    db_path = get_user_db_path(username)
    if not os.path.exists(db_path):
        if seed_if_empty and os.path.exists(GLOBAL_DB_PATH):
            try:
                shutil.copyfile(GLOBAL_DB_PATH, db_path)
            except Exception:
                return {}
        else:
            return {}

    try:
        with open(db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_user_db(username: str, db: Dict[str, List[List[float]]]) -> None:
    """Safely persist the user's isolated embeddings."""
    db_path = get_user_db_path(username)
    temp_path = db_path + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2)
    os.replace(temp_path, db_path)


def clear_user_db(username: str) -> None:
    """Clear only the active user's personal samples."""
    save_user_db(username, {})


def seed_user_db_from_global(username: str) -> bool:
    """Import the baseline starter dataset into the user's personal store."""
    if not os.path.exists(GLOBAL_DB_PATH):
        return False
    db_path = get_user_db_path(username)
    shutil.copyfile(GLOBAL_DB_PATH, db_path)
    return True


def load_user_sentences(username: str) -> List[Dict[str, Any]]:
    """Load the user's personal translation/sentence history."""
    path = get_user_sentences_path(username)
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            items = json.load(f)
            return items if isinstance(items, list) else []
    except Exception:
        return []


def save_user_sentence_item(username: str, text: str, detected_word: Optional[str] = None) -> None:
    """Append a newly constructed sentence to the user's personal history."""
    if not text.strip():
        return
    history = load_user_sentences(username)
    record = {
        "text": text.strip(),
        "detected_word": detected_word or "",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    history.insert(0, record)  # most recent first
    # Keep up to 100 sentences
    history = history[:100]

    path = get_user_sentences_path(username)
    temp_path = path + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)
    os.replace(temp_path, path)


def clear_user_sentences(username: str) -> None:
    """Clear the user's personal translation history."""
    path = get_user_sentences_path(username)
    if os.path.exists(path):
        os.remove(path)


def get_user_stats(username: str) -> Dict[str, Any]:
    """Compute summary statistics for a user's isolated data."""
    db = load_user_db(username, seed_if_empty=False)
    total_samples = sum(len(v) for v in db.values())
    labels = sorted(db.keys())
    sentences = load_user_sentences(username)
    user_root = get_user_root(username)
    has_personal_model = os.path.exists(os.path.join(user_root, "model", "gesture_rf.joblib"))

    return {
        "total_samples": total_samples,
        "label_count": len(labels),
        "labels": labels,
        "sentences_count": len(sentences),
        "has_personal_model": has_personal_model,
        "db_size_kb": round(os.path.getsize(get_user_db_path(username)) / 1024, 1)
        if os.path.exists(get_user_db_path(username))
        else 0,
    }
