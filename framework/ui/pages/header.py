"""Header component — exposes the shared balance pill."""
from __future__ import annotations

from selenium.webdriver.common.by import By

from .base_page import BasePage


class Header(BasePage):
    BALANCE = (By.ID, "header-balance")

    def balance(self) -> float:
        return self.parse_euro(self.text_of(self.BALANCE))
