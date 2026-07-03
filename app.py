"""Root ASGI entrypoint for local uvicorn runs.

This module exposes the FastAPI application as ``app`` so the service can be
started from a fresh checkout with:

    uvicorn app:app --reload --port 8000
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from feishu_agent.app import app  # noqa: E402

__all__ = ["app"]
