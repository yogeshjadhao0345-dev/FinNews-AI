import os
import json
import uuid
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from app.models.schemas import UserProfile

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
USERS_FILE = DATA_DIR / "users.json"

class AuthService:
    _users: Dict[str, Dict[str, Any]] = {}
    _sessions: Dict[str, str] = {}  # token -> email

    @classmethod
    def initialize(cls):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if USERS_FILE.exists():
            try:
                with open(USERS_FILE, "r", encoding="utf-8") as f:
                    cls._users = json.load(f)
            except Exception:
                cls._users = {}

        # Ensure demo user exists
        demo_email = "demo@finnews.ai"
        if demo_email not in cls._users:
            salt = "finnews_demo_salt"
            hashed = cls._hash_password("password123", salt)
            cls._users[demo_email] = {
                "id": "usr-demo-001",
                "name": "Alex Vance",
                "email": demo_email,
                "salt": salt,
                "password_hash": hashed,
                "role": "Demo Investor"
            }
            cls._save_users()

    @classmethod
    def _save_users(cls):
        try:
            with open(USERS_FILE, "w", encoding="utf-8") as f:
                json.dump(cls._users, f, indent=2)
        except Exception as e:
            print(f"[AuthService] Error saving users: {e}")

    @classmethod
    def _hash_password(cls, password: str, salt: str) -> str:
        return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()

    @classmethod
    def _get_initials(cls, name: str) -> str:
        parts = [p for p in name.strip().split() if p]
        if not parts:
            return "U"
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[-1][0]).upper()

    @classmethod
    def register(cls, name: str, email: str, password: str) -> Tuple[bool, str, Optional[UserProfile], Optional[str]]:
        email = email.strip().lower()
        name = name.strip()
        if not email or "@" not in email:
            return False, "Please provide a valid email address.", None, None
        if len(password) < 6:
            return False, "Password must be at least 6 characters.", None, None
        if not name:
            return False, "Please provide your name.", None, None

        if email in cls._users:
            return False, "An account with this email already exists. Please sign in.", None, None

        salt = uuid.uuid4().hex[:16]
        pwd_hash = cls._hash_password(password, salt)
        user_id = f"usr-{uuid.uuid4().hex[:8]}"

        cls._users[email] = {
            "id": user_id,
            "name": name,
            "email": email,
            "salt": salt,
            "password_hash": pwd_hash,
            "role": "Retail Investor"
        }
        cls._save_users()

        token = f"tok-{uuid.uuid4().hex}"
        cls._sessions[token] = email

        profile = UserProfile(
            id=user_id,
            name=name,
            email=email,
            initials=cls._get_initials(name),
            role="Retail Investor"
        )
        return True, "Account created successfully!", profile, token

    @classmethod
    def login(cls, email: str, password: str) -> Tuple[bool, str, Optional[UserProfile], Optional[str]]:
        email = email.strip().lower()
        if email not in cls._users:
            return False, "Invalid email or password.", None, None

        user_data = cls._users[email]
        hashed = cls._hash_password(password, user_data["salt"])
        if hashed != user_data["password_hash"]:
            return False, "Invalid email or password.", None, None

        token = f"tok-{uuid.uuid4().hex}"
        cls._sessions[token] = email

        profile = UserProfile(
            id=user_data["id"],
            name=user_data["name"],
            email=email,
            initials=cls._get_initials(user_data["name"]),
            role=user_data.get("role", "Retail Investor")
        )
        return True, "Welcome back!", profile, token

    @classmethod
    def demo_login(cls) -> Tuple[UserProfile, str]:
        demo_email = "demo@finnews.ai"
        user_data = cls._users.get(demo_email)
        token = f"tok-{uuid.uuid4().hex}"
        cls._sessions[token] = demo_email
        profile = UserProfile(
            id=user_data["id"],
            name=user_data["name"],
            email=demo_email,
            initials=cls._get_initials(user_data["name"]),
            role="Demo Investor"
        )
        return profile, token

    @classmethod
    def verify_token(cls, token: str) -> Optional[UserProfile]:
        if not token or token not in cls._sessions:
            return None
        email = cls._sessions[token]
        if email not in cls._users:
            return None
        user_data = cls._users[email]
        return UserProfile(
            id=user_data["id"],
            name=user_data["name"],
            email=email,
            initials=cls._get_initials(user_data["name"]),
            role=user_data.get("role", "Retail Investor")
        )

# Initialize on import
AuthService.initialize()
