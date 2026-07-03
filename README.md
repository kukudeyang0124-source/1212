# Feishu Intelligent Agent

This repository contains a minimal FastAPI service that connects a Feishu custom bot to an OpenAI-compatible intelligent agent.

## Features

- Handles Feishu `url_verification` callbacks.
- Receives `im.message.receive_v1` text messages.
- Calls an OpenAI-compatible `/chat/completions` model endpoint.
- Replies to the original Feishu message through the Feishu Open Platform API.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
uvicorn feishu_agent.app:app --host 0.0.0.0 --port 8000
```

Expose `POST /feishu/events` to Feishu as the event subscription callback URL.

## Feishu setup checklist

1. Create a Feishu app in the Feishu developer console.
2. Enable bot capability and event subscriptions.
3. Subscribe to `im.message.receive_v1`.
4. Grant message read/reply permissions required by the bot, then publish or install the app.
5. Configure the callback URL: `https://<your-domain>/feishu/events`.
6. Copy app credentials and verification token into `.env`.

## Environment variables

See `.env.example` for all required variables. `OPENAI_BASE_URL` can point to any OpenAI-compatible provider that supports `/chat/completions`.

## Notes

Encrypted Feishu callbacks are not enabled in this minimal service yet. Leave callback encryption disabled in Feishu, or add decrypt middleware before production use.
