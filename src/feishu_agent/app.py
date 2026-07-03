from __future__ import annotations

import json
from typing import Any

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request

from .agent import AgentError, IntelligentAgent
from .config import Settings, get_settings
from .feishu import FeishuClient


def create_app() -> FastAPI:
    app = FastAPI(title="Feishu Intelligent Agent", version="0.1.0")

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/feishu/events")
    async def feishu_events(
        request: Request,
        background_tasks: BackgroundTasks,
        settings: Settings = Depends(get_settings),
    ) -> dict[str, Any]:
        payload = await request.json()
        _verify_token(payload, settings)

        if payload.get("type") == "url_verification":
            return {"challenge": payload.get("challenge", "")}

        event = payload.get("event", {})
        if event.get("type") != "im.message.receive_v1":
            return {"ok": True, "ignored": True}

        message = event.get("message", {})
        message_id = message.get("message_id")
        text = _extract_text(message)
        if not message_id or not text:
            return {"ok": True, "ignored": True}

        background_tasks.add_task(_answer_and_reply, settings, message_id, text)
        return {"ok": True}

    return app


def _verify_token(payload: dict[str, Any], settings: Settings) -> None:
    expected = settings.feishu_verification_token.get_secret_value()
    actual = payload.get("token") or payload.get("header", {}).get("token")
    if expected and actual != expected:
        raise HTTPException(status_code=401, detail="invalid Feishu verification token")


def _extract_text(message: dict[str, Any]) -> str:
    if message.get("message_type") != "text":
        return ""

    content = message.get("content", "")
    if isinstance(content, str):
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            return content.strip()
    elif isinstance(content, dict):
        parsed = content
    else:
        return ""

    text = parsed.get("text", "")
    return str(text).strip()


async def _answer_and_reply(settings: Settings, message_id: str, text: str) -> None:
    agent = IntelligentAgent(settings)
    feishu = FeishuClient(settings)
    try:
        answer = await agent.answer(text)
    except AgentError as exc:
        answer = f"抱歉，智能体暂时不可用：{exc}。"
    await feishu.reply_text(message_id, answer)


app = create_app()
