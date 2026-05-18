"""Shared fixtures.

Fixture scopes:
    config        session   — env-driven config, immutable
    api_client    function  — fresh session per test, easy to inspect history
    driver        function  — fresh browser per UI test for isolation
    reset_balance function  — explicit opt-in; not every test wants this
"""
from __future__ import annotations

from collections.abc import Generator

import pytest

from framework import config as config_module
from framework.api.client import BettingApiClient
from framework.config import Config
from framework.ui.driver import make_chrome
from framework.ui.pages.bet_receipt import BetReceipt
from framework.ui.pages.bet_slip import BetSlip
from framework.ui.pages.header import Header
from framework.ui.pages.match_list_page import MatchListPage


@pytest.fixture(scope="session")
def config() -> Config:
    return config_module.load()


@pytest.fixture
def api_client(config: Config) -> Generator[BettingApiClient, None, None]:
    with BettingApiClient(base_url=config.base_url, user_id=config.user_id) as client:
        yield client


@pytest.fixture
def reset_balance(api_client: BettingApiClient) -> None:
    """Best-effort balance reset before a test.

    NOTE: the live `/api/reset-balance` endpoint is documented as
    "response payload may differ from persisted balance" — and in practice it
    does not actually restore €125.50. Tests should therefore read the actual
    balance after this fixture, never assume €125.50.
    """
    api_client.reset_balance()


@pytest.fixture
def driver(config: Config):
    drv = make_chrome(headless=config.headless)
    drv.implicitly_wait(0)  # rely on explicit waits in page objects
    try:
        yield drv
    finally:
        drv.quit()


@pytest.fixture
def match_list_page(driver, config: Config) -> MatchListPage:
    page = MatchListPage(driver, timeout=config.ui_timeout)
    page.open(config.base_url, config.user_id)
    return page


@pytest.fixture
def header(driver, config: Config) -> Header:
    return Header(driver, timeout=config.ui_timeout)


@pytest.fixture
def bet_slip(driver, config: Config) -> BetSlip:
    return BetSlip(driver, timeout=config.ui_timeout)


@pytest.fixture
def bet_receipt(driver, config: Config) -> BetReceipt:
    return BetReceipt(driver, timeout=config.ui_timeout)
