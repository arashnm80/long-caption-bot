# long-caption-bot
telegram bot to send media with large caption up to 4096 chars

Telethon user operations go through **private-router** (`PRIVATE_ROUTER_URL` + `PRIVATE_ROUTER_TOKEN`). This bot does not open its own Telethon session.

### run
- ensure private-router is up: `curl -s http://127.0.0.1:3010/health`
- `./restart-long-caption-bot.sh`

### to-do
- support caption for media group (we can check media_group_id in a small timeframe to bind the pack together)
