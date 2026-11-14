"""Persistent blocklist for long-caption-bot (JSON on disk, not a DB)."""
from __future__ import annotations

import html
import json
import threading
from datetime import datetime, timezone
from pathlib import Path

from telebot import types

BLOCKLIST_PATH = Path(__file__).resolve().parent / "blocked_users.json"
ADMIN_USERNAMES = {"arashnm80"}

_lock = threading.Lock()
_cache: dict[str, dict] | None = None
# Recent sender cards (log channel /admin list) so Block can keep name/username.
_sender_meta: dict[str, dict] = {}


def _load() -> dict[str, dict]:
    global _cache
    if _cache is not None:
        return _cache
    if BLOCKLIST_PATH.exists():
        try:
            raw = json.loads(BLOCKLIST_PATH.read_text(encoding="utf-8"))
            _cache = {str(k): v for k, v in raw.items()} if isinstance(raw, dict) else {}
        except (json.JSONDecodeError, OSError):
            _cache = {}
    else:
        _cache = {}
    return _cache


def _save(data: dict[str, dict]) -> None:
    global _cache
    _cache = data
    BLOCKLIST_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def is_admin(user) -> bool:
    if not user:
        return False
    username = (getattr(user, "username", None) or "").lower()
    return username in ADMIN_USERNAMES


def is_blocked(user_id: int | str) -> bool:
    with _lock:
        return str(user_id) in _load()


def get_blocked() -> dict[str, dict]:
    with _lock:
        return dict(_load())


def _user_snapshot(user) -> dict:
    return {
        "username": getattr(user, "username", None),
        "first_name": getattr(user, "first_name", None) or "",
        "last_name": getattr(user, "last_name", None) or "",
        "blocked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def remember_sender(user) -> None:
    if not user:
        return
    _sender_meta[str(user.id)] = {
        "username": getattr(user, "username", None),
        "first_name": getattr(user, "first_name", None) or "",
        "last_name": getattr(user, "last_name", None) or "",
    }


def remember_sender_entry(user_id: int | str, entry: dict | None) -> None:
    if not entry:
        return
    _sender_meta[str(user_id)] = {
        "username": entry.get("username"),
        "first_name": entry.get("first_name") or "",
        "last_name": entry.get("last_name") or "",
    }


def sender_meta(user_id: int | str) -> dict | None:
    uid = str(user_id)
    with _lock:
        if uid in _load():
            return dict(_load()[uid])
    return _sender_meta.get(uid)


def block_user(user_id: int | str, user=None, meta: dict | None = None) -> dict:
    uid = str(user_id)
    with _lock:
        data = _load()
        if user is not None:
            entry = _user_snapshot(user)
        elif meta is not None:
            entry = {
                "username": meta.get("username"),
                "first_name": meta.get("first_name") or "",
                "last_name": meta.get("last_name") or "",
                "blocked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
        else:
            entry = data.get(uid) or {
                "username": None,
                "first_name": "",
                "last_name": "",
                "blocked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            if uid in data:
                entry = {**data[uid], "blocked_at": entry["blocked_at"]}
        data[uid] = entry
        _save(data)
        return entry


def unblock_user(user_id: int | str) -> bool:
    uid = str(user_id)
    with _lock:
        data = _load()
        if uid not in data:
            return False
        del data[uid]
        _save(data)
        return True


def display_name(entry_or_user) -> str:
    if hasattr(entry_or_user, "first_name"):
        parts = [
            getattr(entry_or_user, "first_name", None) or "",
            getattr(entry_or_user, "last_name", None) or "",
        ]
    else:
        parts = [
            (entry_or_user or {}).get("first_name") or "",
            (entry_or_user or {}).get("last_name") or "",
        ]
    name = " ".join(p for p in parts if p).strip()
    return name or "—"


def format_sender_card(user_id: int | str, user=None, entry: dict | None = None) -> str:
    """HTML card for the log channel / admin list."""
    uid = str(user_id)
    blocked = is_blocked(uid)
    if user is not None:
        name = display_name(user)
        username = getattr(user, "username", None)
    else:
        entry = entry or get_blocked().get(uid) or {}
        name = display_name(entry)
        username = entry.get("username")

    username_line = f"@{html.escape(username)}" if username else "—"
    status = "🚫 blocked" if blocked else "✅ allowed"
    return (
        f"<b>Sender</b>\n"
        f"name: {html.escape(name)}\n"
        f"username: {username_line}\n"
        f"id: <code>{html.escape(uid)}</code>\n"
        f"status: {status}"
    )


def block_toggle_markup(user_id: int | str) -> types.InlineKeyboardMarkup:
    uid = str(user_id)
    markup = types.InlineKeyboardMarkup()
    if is_blocked(uid):
        markup.add(
            types.InlineKeyboardButton("Unblock", callback_data=f"unblk:{uid}")
        )
    else:
        markup.add(
            types.InlineKeyboardButton("Block", callback_data=f"blk:{uid}")
        )
    return markup
