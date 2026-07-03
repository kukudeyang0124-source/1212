from __future__ import annotations

import httpx

from .config import Settings


class AgentError(RuntimeError):
    """Raised when the backing language model cannot produce a response."""


class IntelligentAgent:
    """Small OpenAI-compatible chat agent used by the Feishu webhook."""

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self._settings = settings
        self._client = client

    async def answer(self, message: str) -> str:
        api_key = self._settings.openai_api_key.get_secret_value()
        if not api_key:
            return "智能体还未配置 OPENAI_API_KEY，请联系管理员完成模型接入。"

        payload = {
            "model": self._settings.agent_model,
            "messages": [
                {"role": "system", "content": self._settings.agent_system_prompt},
                {"role": "user", "content": message},
            ],
        }
        headers = {"Authorization": f"Bearer {api_key}"}
        url = f"{self._settings.openai_base_url.rstrip('/')}/chat/completions"

        close_client = self._client is None
        client = self._client or httpx.AsyncClient(timeout=self._settings.request_timeout_seconds)
        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as exc:
            raise AgentError("模型服务调用失败") from exc
        finally:
            if close_client:
                await client.aclose()

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise AgentError("模型服务返回格式不正确") from exc

        return str(content).strip() or "我暂时没有生成有效回复，请稍后再试。"
