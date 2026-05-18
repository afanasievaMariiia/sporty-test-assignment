"""Bet slip — the right-hand panel where the user reviews and places the bet."""
from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .base_page import BasePage


class BetSlip(BasePage):
    PANEL = (By.ID, "bet-slip")
    SELECTION = (By.CSS_SELECTOR, "#bet-slip .betSelectionCard")
    SELECTION_TEAMS = (By.CSS_SELECTOR, "#bet-slip .betSelectionTeams")
    SELECTION_MARKET = (By.CSS_SELECTOR, "#bet-slip .betSelectionMarket")
    SELECTION_ODDS = (By.CSS_SELECTOR, "#bet-slip .betSelectionOdds")
    STAKE_INPUT = (By.ID, "bet-slip-stake-input")
    TOTAL_STAKE = (By.ID, "bet-slip-total-stake")
    POTENTIAL_PAYOUT = (By.ID, "bet-slip-potential-payout")
    PLACE_BET_BUTTON = (By.ID, "bet-slip-place-bet")
    EMPTY_STATE = (By.CSS_SELECTOR, "#bet-slip .betSlipBodyEmpty")

    def wait_until_selection_visible(self) -> None:
        self.find_visible(self.SELECTION)

    def teams_text(self) -> str:
        return self.text_of(self.SELECTION_TEAMS)

    def market_text(self) -> str:
        """Returns text like 'Match Winner: Home'."""
        return self.text_of(self.SELECTION_MARKET)

    def odds_text(self) -> str:
        """Returns text like 'Odds: 2.30'."""
        return self.text_of(self.SELECTION_ODDS)

    def odds_value(self) -> float:
        return self.parse_euro(self.odds_text())

    def enter_stake(self, stake: str) -> None:
        """Type a stake value. Accepts the raw string (e.g. '5.00')."""
        field = self.find_clickable(self.STAKE_INPUT)
        field.click()
        field.send_keys(Keys.CONTROL, "a")
        field.send_keys(Keys.DELETE)
        field.clear()
        field.send_keys(stake)

    def potential_payout(self) -> float:
        return self.parse_euro(self.text_of(self.POTENTIAL_PAYOUT))

    def total_stake(self) -> float:
        return self.parse_euro(self.text_of(self.TOTAL_STAKE))

    def place_bet_button(self):
        return self.find_visible(self.PLACE_BET_BUTTON)

    def is_place_bet_enabled(self) -> bool:
        btn = self.place_bet_button()
        return btn.is_enabled() and "placeBetButtonDisabled" not in (btn.get_attribute("class") or "")

    def click_place_bet(self) -> None:
        self.find_clickable(self.PLACE_BET_BUTTON).click()

    def is_empty(self) -> bool:
        try:
            return self.find_visible(self.EMPTY_STATE, timeout=2).is_displayed()
        except Exception:
            return False
