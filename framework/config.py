"""Test configuration loaded from environment variables.

Values fall back to sensible defaults that target the live assessment app.
Override per run via env vars (or a .env file picked up by python-dotenv).
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Config:
    base_url: str
    user_id: str
    browser: str
    headless: bool
    ui_timeout: int

    @property
    def api_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/api"

    def ui_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/?user-id={self.user_id}"


def load() -> Config:
    return Config(
        base_url=os.getenv("BASE_URL", "https://qae-assignment-tau.vercel.app"),
        user_id=os.getenv("USER_ID", "candidate-X0qwCNvZr4"),
        browser=os.getenv("BROWSER", "chrome").lower(),
        headless=_bool("HEADLESS", True),
        ui_timeout=int(os.getenv("UI_TIMEOUT", "15")),
    )
