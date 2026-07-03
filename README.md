# Feishu Intelligent Agent

This repository contains a minimal FastAPI service that connects a Feishu custom bot to an OpenAI-compatible intelligent agent.

## Features

- Handles Feishu `url_verification` callbacks.
- Receives `im.message.receive_v1` text messages.
- Calls an OpenAI-compatible `/chat/completions` model endpoint.
- Replies to the original Feishu message through the Feishu Open Platform API.

## Install dependencies

From the repository root, create and activate a virtual environment, then install the project dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The `requirements.txt` file includes the packages needed to run the service locally, including FastAPI, Uvicorn, HTTPX, and Pydantic Settings. It also includes Pytest for local checks.

## Run the service

Start the FastAPI app from the repository root with:

```bash
uvicorn app:app --reload --port 8000
```

The root `app.py` file exposes the FastAPI application as `app`, so the command above works after a fresh `pip install -r requirements.txt` without requiring an editable package install.

## Expected output

When the service starts successfully, Uvicorn prints output similar to:

```text
INFO:     Will watch for changes in these directories: ['<repo path>']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

You can verify the service in another terminal:

```bash
curl http://127.0.0.1:8000/healthz
```

Expected response:

```json
{"status":"ok"}
```

Expose `POST /feishu/events` to Feishu as the event subscription callback URL.

## Feishu setup checklist

1. Create a Feishu app in the Feishu developer console.
2. Enable bot capability and event subscriptions.
3. Subscribe to `im.message.receive_v1`.
4. Grant message read/reply permissions required by the bot, then publish or install the app.
5. Configure the callback URL: `https://<your-domain>/feishu/events`.
6. Copy app credentials and verification token into `.env` or export the environment variables before starting Uvicorn.

## Environment variables

The service reads configuration from environment variables and optionally from a local `.env` file:

| Variable | Required | Description |
| --- | --- | --- |
| `FEISHU_APP_ID` | For Feishu replies | Feishu app ID. |
| `FEISHU_APP_SECRET` | For Feishu replies | Feishu app secret. |
| `FEISHU_VERIFICATION_TOKEN` | Recommended | Verification token checked on Feishu callbacks. |
| `FEISHU_ENCRYPT_KEY` | No | Reserved for encrypted callback support. |
| `OPENAI_API_KEY` | For model replies | API key for the OpenAI-compatible model provider. |
| `OPENAI_BASE_URL` | No | Defaults to `https://api.openai.com/v1`. |
| `AGENT_MODEL` | No | Defaults to `gpt-4.1-mini`. |
| `AGENT_SYSTEM_PROMPT` | No | System prompt used by the agent. |
| `REQUEST_TIMEOUT_SECONDS` | No | HTTP request timeout, default `20.0`. |

If `OPENAI_API_KEY` is not configured, the webhook still starts and returns a friendly message indicating that the model is not configured.

## Notes

Encrypted Feishu callbacks are not enabled in this minimal service yet. Leave callback encryption disabled in Feishu, or add decrypt middleware before production use.
