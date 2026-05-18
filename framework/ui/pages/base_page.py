"""BasePage — shared waiting / interaction helpers for page objects.

Pages should expose business-meaningful methods (`click_home_odds`,
`enter_stake`) and keep raw selector handling here.
"""
from __future__ import annotations

import re

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

Locator = tuple[str, str]
_MONEY = re.compile(r"-?\d+(?:\.\d+)?")


class BasePage:
    def __init__(self, driver: WebDriver, timeout: int = 15):
        self.driver = driver
        self.timeout = timeout

    def wait(self, timeout: int | None = None) -> WebDriverWait:
        return WebDriverWait(self.driver, timeout or self.timeout)

    def find_visible(self, locator: Locator, timeout: int | None = None) -> WebElement:
        return self.wait(timeout).until(EC.visibility_of_element_located(locator))

    def find_clickable(self, locator: Locator, timeout: int | None = None) -> WebElement:
        return self.wait(timeout).until(EC.element_to_be_clickable(locator))

    def wait_until_gone(self, locator: Locator, timeout: int | None = None) -> None:
        self.wait(timeout).until(EC.invisibility_of_element_located(locator))

    def text_of(self, locator: Locator, timeout: int | None = None) -> str:
        return self.find_visible(locator, timeout).text.strip()

    @staticmethod
    def parse_euro(text: str) -> float:
        """Extract a euro amount from a string like 'Balance: €119.00' or '€5.00'.

        Falls back to a ValueError if no number is found — caller decides what
        to do (most callers will let the test fail loudly).
        """
        match = _MONEY.search(text.replace(",", ""))
        if not match:
            raise ValueError(f"No numeric amount in {text!r}")
        return float(match.group())
