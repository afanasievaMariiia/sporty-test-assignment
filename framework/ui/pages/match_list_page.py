"""Match list page object.

The app exposes a stable id pattern on each odds button:
    odds-<match-id>-{home|draw|away}

…and a card id pattern: `match-card-<match-id>`. We use those to scope clicks
and reads to the right card.
"""
from __future__ import annotations

from dataclasses import dataclass

from selenium.webdriver.common.by import By

from .base_page import BasePage


@dataclass(frozen=True)
class MatchCard:
    match_id: str
    home_team: str
    away_team: str
    competition: str
    odds_home: float
    odds_draw: float
    odds_away: float


class MatchListPage(BasePage):
    URL_PATH = "/?user-id={user_id}"

    MATCH_LIST = (By.ID, "match-list")
    UPCOMING_CARDS = (By.CSS_SELECTOR, "#match-list .matchCard")

    def open(self, base_url: str, user_id: str) -> "MatchListPage":
        self.driver.get(f"{base_url.rstrip('/')}/?user-id={user_id}")
        self.find_visible(self.MATCH_LIST)
        return self

    def first_upcoming_card(self) -> MatchCard:
        """Return the first UPCOMING match card in display order.

        We filter on the badge text rather than CSS class so the page object
        survives style refactors.
        """
        self.find_visible(self.MATCH_LIST)
        cards = self.driver.find_elements(*self.UPCOMING_CARDS)
        for card in cards:
            badge = card.find_element(By.CSS_SELECTOR, ".badge").text.strip().upper()
            if badge != "UPCOMING":
                continue
            match_id = card.get_attribute("id").removeprefix("match-card-")
            teams = card.find_elements(By.CSS_SELECTOR, ".teamName")
            meta = card.find_elements(By.CSS_SELECTOR, ".matchMeta span")
            return MatchCard(
                match_id=match_id,
                home_team=teams[0].text.strip(),
                away_team=teams[1].text.strip(),
                competition=meta[1].text.strip() if len(meta) > 1 else "",
                odds_home=float(card.find_element(By.ID, f"odds-{match_id}-home")
                                .find_element(By.CSS_SELECTOR, ".oddsButtonValue").text),
                odds_draw=float(card.find_element(By.ID, f"odds-{match_id}-draw")
                                .find_element(By.CSS_SELECTOR, ".oddsButtonValue").text),
                odds_away=float(card.find_element(By.ID, f"odds-{match_id}-away")
                                .find_element(By.CSS_SELECTOR, ".oddsButtonValue").text),
            )
        raise AssertionError("No UPCOMING matches available to test against")

    def click_home_odds(self, match_id: str) -> None:
        self.find_clickable((By.ID, f"odds-{match_id}-home")).click()

    def click_draw_odds(self, match_id: str) -> None:
        self.find_clickable((By.ID, f"odds-{match_id}-draw")).click()

    def click_away_odds(self, match_id: str) -> None:
        self.find_clickable((By.ID, f"odds-{match_id}-away")).click()
