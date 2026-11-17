import hashlib
import json
import os
import re
import secrets
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")


def _ensure_data_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


def _hash_password(password: str, salt: str) -> str:
    """Derive secure key using PBKDF2 HMAC SHA-256."""
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
    ).hex()


def load_users() -> Dict[str, Dict[str, Any]]:
    """Load all registered users from storage."""
    _ensure_data_dir()
    if not os.path.exists(USERS_FILE):
        return _seed_default_users()
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return _seed_default_users()
            return data
    except Exception:
        return _seed_default_users()


def save_users(users: Dict[str, Dict[str, Any]]) -> None:
    """Save all registered users safely to storage."""
    _ensure_data_dir()
    temp_file = USERS_FILE + ".tmp"
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)
    os.replace(temp_file, USERS_FILE)


def _seed_default_users() -> Dict[str, Dict[str, Any]]:
    """Create a default demo user for instant testing if storage is empty."""
    demo_salt = secrets.token_hex(16)
    demo_user = {
        "username": "demo",
        "display_name": "Demo Explorer",
        "email": "demo@signstudio.ai",
        "password_hash": _hash_password("demo123", demo_salt),
        "salt": demo_salt,
        "avatar": "⚡",
        "created_at": datetime.now().isoformat(),
        "last_login": datetime.now().isoformat(),
        "role": "demo",
    }
    users = {"demo": demo_user}
    save_users(users)
    return users


def register_user(
    username: str,
    display_name: str,
    email: str,
    password: str,
    avatar: str = "🧑‍💻",
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Register a new individual user account."""
    username = username.strip().lower()
    display_name = display_name.strip()
    email = email.strip().lower()

    if not username:
        return False, "Username cannot be empty.", None

    if not re.match(r"^[a-zA-Z0-9_.-]{3,24}$", username):
        return (
            False,
            "Username must be 3-24 characters and only contain letters, numbers, underscores, dots, or dashes.",
            None,
        )

    if not display_name:
        display_name = username.capitalize()

    if not email or "@" not in email or "." not in email:
        return False, "Please enter a valid email address.", None

    if len(password) < 6:
        return False, "Password must be at least 6 characters long.", None

    users = load_users()

    # Check for existing username
    if username in users:
        return False, f"Username '{username}' is already taken. Please choose another.", None

    # Check for existing email
    for existing_user in users.values():
        if existing_user.get("email", "").lower() == email:
            return (
                False,
                f"An account with email '{email}' already exists. Please sign in.",
                None,
            )

    salt = secrets.token_hex(16)
    password_hash = _hash_password(password, salt)
    now_iso = datetime.now().isoformat()

    user_record = {
        "username": username,
        "display_name": display_name,
        "email": email,
        "password_hash": password_hash,
        "salt": salt,
        "avatar": avatar or "🧑‍💻",
        "created_at": now_iso,
        "last_login": now_iso,
        "role": "user",
    }

    users[username] = user_record
    save_users(users)

    # Return safe user record without salt or password hash
    safe_user = dict(user_record)
    safe_user.pop("password_hash", None)
    safe_user.pop("salt", None)
    return True, f"Welcome aboard, {display_name}! Account created successfully.", safe_user


def authenticate_user(
    username_or_email: str, password: str
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Authenticate an existing user with username/email and password."""
    target = username_or_email.strip().lower()
    if not target or not password:
        return False, "Please enter both username/email and password.", None

    users = load_users()
    matched_user = None

    if target in users:
        matched_user = users[target]
    else:
        for u in users.values():
            if u.get("email", "").lower() == target:
                matched_user = u
                break

    if not matched_user:
        return False, "Invalid credentials. Please verify username/email and password.", None

    salt = matched_user.get("salt", "")
    expected_hash = matched_user.get("password_hash", "")
    computed_hash = _hash_password(password, salt)

    if not secrets.compare_digest(expected_hash, computed_hash):
        return False, "Invalid credentials. Incorrect password.", None

    # Update last login timestamp
    matched_user["last_login"] = datetime.now().isoformat()
    save_users(users)

    safe_user = dict(matched_user)
    safe_user.pop("password_hash", None)
    safe_user.pop("salt", None)
    return True, f"Welcome back, {safe_user.get('display_name')}!", safe_user


def get_user_profile(username: str) -> Optional[Dict[str, Any]]:
    """Get public user profile information."""
    users = load_users()
    u = users.get(username.strip().lower())
    if not u:
        return None
    safe_u = dict(u)
    safe_u.pop("password_hash", None)
    safe_u.pop("salt", None)
    return safe_u
