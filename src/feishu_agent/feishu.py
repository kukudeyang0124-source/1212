from __future__ import annotations

import time

import httpx

from .config import Settings


class FeishuClient:
    """Minimal Feishu Open Platform client for replying to incoming messages."""

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self._settings = settings
        self._client = client
        self._tenant_token: str | None = None
        self._tenant_token_expires_at = 0.0

    async def reply_text(self, message_id: str, text: str) -> None:
        token = await self._get_tenant_access_token()
        payload = {"msg_type": "text", "content": {"text": text}}
        await self._request(
            "POST",
            f"/open-apis/im/v1/messages/{message_id}/reply",
            headers={"Authorization": f"Bearer {token}"},
            json=payload,
        )

    async def _get_tenant_access_token(self) -> str:
        if self._tenant_token and time.time() < self._tenant_token_expires_at:
            return self._tenant_token

        app_secret = self._settings.feishu_app_secret.get_secret_value()
        response = await self._request(
            "POST",
            "/open-apis/auth/v3/tenant_access_token/internal",
            json={"app_id": self._settings.feishu_app_id, "app_secret": app_secret},
        )
        token = response.get("tenant_access_token")
        if not token:
            raise RuntimeError("Feishu tenant_access_token is missing")

        expire = int(response.get("expire", 7200))
        self._tenant_token = token
        self._tenant_token_expires_at = time.time() + max(expire - 120, 60)
        return token

    async def _request(self, method: str, path: str, **kwargs: object) -> dict:
        close_client = self._client is None
        client = self._client or httpx.AsyncClient(base_url="https://open.feishu.cn", timeout=self._settings.request_timeout_seconds)
        try:
            response = await client.request(method, path, **kwargs)
            response.raise_for_status()
            data = response.json()
        finally:
            if close_client:
                await client.aclose()

        if data.get("code", 0) != 0:
            raise RuntimeError(f"Feishu API error: {data}")
        return data
