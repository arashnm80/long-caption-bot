from config import *
import time

# Telegram delivers each album item as its own update; keep them until the user replies.
# reply_to_message often omits media_group_id, so we also index by message_id.
ALBUM_CACHE_TTL_SEC = 60 * 60
_album_cache: dict[tuple[int, str], dict] = {}
_message_to_album: dict[tuple[int, int], tuple[int, str]] = {}


def _purge_stale_albums(now: float | None = None) -> None:
    now = time.monotonic() if now is None else now
    stale = [
        key
        for key, entry in _album_cache.items()
        if now - entry["updated_at"] > ALBUM_CACHE_TTL_SEC
    ]
    for key in stale:
        entry = _album_cache.pop(key, None)
        if not entry:
            continue
        chat_id = key[0]
        for message_id in entry["message_ids"]:
            _message_to_album.pop((chat_id, message_id), None)


def remember_album_ids(
    chat_id: int,
    message_ids: list[int],
    media_group_id: str | None = None,
) -> None:
    """Index a full album (user-sent or bot-sent) for later text-reply resolution."""
    ids = sorted({int(mid) for mid in message_ids})
    if len(ids) < 2:
        return
    now = time.monotonic()
    _purge_stale_albums(now)
    gid = str(media_group_id) if media_group_id else f"local-{ids[0]}-{ids[-1]}"
    key = (chat_id, gid)
    _album_cache[key] = {"message_ids": ids, "updated_at": now}
    for mid in ids:
        _message_to_album[(chat_id, mid)] = key


def remember_album_message(message) -> None:
    """Record one media-group item so a later text reply can resolve the full album."""
    media_group_id = getattr(message, "media_group_id", None)
    if not media_group_id:
        return
    now = time.monotonic()
    _purge_stale_albums(now)
    key = (message.chat.id, str(media_group_id))
    entry = _album_cache.get(key)
    if entry is None:
        entry = {"message_ids": [], "updated_at": now}
        _album_cache[key] = entry
    if message.message_id not in entry["message_ids"]:
        entry["message_ids"].append(message.message_id)
        entry["message_ids"].sort()
    entry["updated_at"] = now
    _message_to_album[(message.chat.id, message.message_id)] = key


def resolve_media_message_ids(chat_id: int, reply_to_message) -> list[int]:
    """All message ids for a replied-to album, or a single id for non-album media."""
    _purge_stale_albums()
    media_group_id = getattr(reply_to_message, "media_group_id", None)
    key = None
    if media_group_id:
        key = (chat_id, str(media_group_id))
    if key is None or key not in _album_cache:
        # Bot API usually strips media_group_id from reply_to_message.
        key = _message_to_album.get((chat_id, reply_to_message.message_id))

    if key:
        entry = _album_cache.get(key)
        if entry and entry["message_ids"]:
            ids = list(entry["message_ids"])
            if reply_to_message.message_id not in ids:
                ids.append(reply_to_message.message_id)
                ids.sort()
            return ids
    return [reply_to_message.message_id]
