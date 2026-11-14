# long-caption-bot
telegram bot to send media with large caption up to 4096 chars

Telethon user operations go through **private-router** (`PRIVATE_ROUTER_URL` + `PRIVATE_ROUTER_TOKEN`). This bot does not open its own Telethon session.

### run
- ensure private-router is up: `curl -s http://127.0.0.1:3010/health`
- `./restart-long-caption-bot.sh`

### albums
- Bot buffers incoming `media_group_id` items, then copies the whole album when you reply with long text (or reply with an album to long text).
- Caption is applied to the first item of the album, same as Telegram’s native album caption.

### moderation
- After each successful caption, the log channel gets a sender card (name / username / id) with Block/Unblock.
- Blocked users get no replies at all (including `/start`).
- Admin DM commands: `/blocked`, `/block <user_id>`, `/unblock <user_id>` (shown on admin `/start`).
- Blocklist file: `blocked_users.json` (local, gitignored).
