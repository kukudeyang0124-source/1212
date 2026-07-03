import pytest
from fastapi.testclient import TestClient

from feishu_agent.app import _extract_text, create_app
from feishu_agent.config import get_settings


@pytest.fixture(autouse=True)
def clear_settings_cache(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("FEISHU_VERIFICATION_TOKEN", "secret-token")
    yield
    get_settings.cache_clear()


def test_healthz():
    client = TestClient(create_app())

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_feishu_url_verification():
    client = TestClient(create_app())

    response = client.post(
        "/feishu/events",
        json={"type": "url_verification", "token": "secret-token", "challenge": "challenge-code"},
    )

    assert response.status_code == 200
    assert response.json() == {"challenge": "challenge-code"}


def test_rejects_invalid_feishu_token():
    client = TestClient(create_app())

    response = client.post(
        "/feishu/events",
        json={"type": "url_verification", "token": "wrong-token", "challenge": "challenge-code"},
    )

    assert response.status_code == 401


def test_extract_text_from_feishu_message_content():
    assert _extract_text({"message_type": "text", "content": '{"text":"你好"}'}) == "你好"
    assert _extract_text({"message_type": "image", "content": '{"text":"ignored"}'}) == ""
