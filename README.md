# Sporty — Test Assignment

Automation framework and 2 high-value tests for the Sports Betting QA assessment app
(<https://qae-assignment-tau.vercel.app>).

- **TC-001** — Place single bet, end-to-end happy path → [`tests/ui/test_place_bet_e2e.py`](tests/ui/test_place_bet_e2e.py)
- **TC-002** — Stake boundary validation → [`tests/api/test_stake_boundaries.py`](tests/api/test_stake_boundaries.py)

Full deliverables:

| Document | Path |
|---|---|
| Test plan (5 prioritized scenarios) | [`docs/test-plan.md`](docs/test-plan.md) |
| Bug reports (3 manual QA defects) | [`docs/bug-reports.md`](docs/bug-reports.md) |
| Automated test execution log | [`docs/execution-results.md`](docs/execution-results.md) |
| Strategy & scaling recommendations | [`docs/strategy.md`](docs/strategy.md) |

---

## Quick start

Requires **Python 3.10+** and **Google Chrome** installed locally. ChromeDriver is fetched
automatically by `webdriver-manager` on first run.

```bash
# 1. clone & enter
git clone <your-repo-url> sporty-test-assignment
cd sporty-test-assignment

# 2. create venv & install
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. (optional) override defaults
cp .env.example .env
# edit .env — the defaults already point at the live assessment app

# 4. run
pytest                 # all tests
pytest -m api          # API tests only (fast, ~10s)
pytest -m ui           # UI E2E only (Selenium, ~25s)
pytest -m smoke        # critical-path subset
pytest -v              # verbose
```

To run the UI test with a visible browser, set `HEADLESS=false` in your `.env` (or env var).

## Configuration

All config is environment-driven (see [`framework/config.py`](framework/config.py)):

| Variable     | Default                                       | Meaning |
|--------------|-----------------------------------------------|---------|
| `BASE_URL`   | `https://qae-assignment-tau.vercel.app`       | Root URL — UI and `/api` |
| `USER_ID`    | `candidate-X0qwCNvZr4`                        | Sent as `x-user-id` header |
| `BROWSER`    | `chrome`                                      | Only Chrome is wired today |
| `HEADLESS`   | `true`                                        | Set `false` to watch the browser |
| `UI_TIMEOUT` | `15`                                          | Default explicit-wait timeout (seconds) |

## Project layout

```
sporty-test-assignment/
├── framework/                      # reusable test framework
│   ├── config.py                   # env-driven Config dataclass
│   ├── api/
│   │   └── client.py               # requests.Session-backed BettingApiClient
│   └── ui/
│       ├── driver.py               # Chrome WebDriver factory
│       └── pages/                  # page object model
│           ├── base_page.py        # shared waits + euro-string helper
│           ├── header.py
│           ├── match_list_page.py
│           ├── bet_slip.py
│           └── bet_receipt.py
├── tests/
│   ├── conftest.py                 # fixtures: config, api_client, driver, pages
│   ├── api/
│   │   └── test_stake_boundaries.py   # TC-002
│   └── ui/
│       └── test_place_bet_e2e.py      # TC-001
├── docs/                           # test plan, execution results, strategy
├── reports/                        # captured pytest output
├── requirements.txt
├── pytest.ini
└── .env.example
```

## Design notes

- **Page Object Model** for the UI: each page object exposes business-meaningful methods
  (`click_home_odds`, `enter_stake`, `snapshot`) and keeps raw selectors local. Tests
  read like a story, not a Selenium script.
- **Stable element IDs over CSS class names.** The app exposes IDs like
  `#bet-slip-stake-input`, `#modal-success-payout`, `odds-<match-id>-home` — these are
  the most resilient selectors available, so they're what the page objects use.
- **Explicit waits only.** `driver.implicitly_wait(0)` in the `driver` fixture; every
  page-object lookup goes through `WebDriverWait(...).until(EC.visibility_of(...))`. No
  `time.sleep`.
- **API tests treat the API as the source of truth.** `BettingApiClient` returns a small
  `ApiResponse` dataclass exposing both status code and parsed body, so negative cases
  can assert both at once.
- **Test isolation.** The live environment provides only one valid user-id, and the
  `/api/reset-balance` endpoint does not actually reset to €125.50 (documented bug — see
  [`docs/execution-results.md`](docs/execution-results.md)). Tests therefore read the
  *actual* starting balance via `/api/balance` and assert on relative change, never on
  absolute amount.

## Tooling choices beyond the required stack

The assignment requires Python 3, Selenium WebDriver + Pytest, the `requests`
library and desktop Chrome. Two small additions, each with a single-line rationale:

- **`webdriver-manager`** — downloads a ChromeDriver that matches the locally
  installed Chrome. Removes the "wrong driver version" failure mode from setup.
- **`python-dotenv`** — picks up a `.env` file so contributors can override
  `BASE_URL` / `USER_ID` / `HEADLESS` without exporting variables in every shell.

No other frameworks (Poetry, Allure, pytest-bdd, etc.) — pytest + the standard
library cover everything the assignment needs.

## Known issues caught by the suite

The UI test (`TC-001`) currently fails — that is the intended outcome. The app
has a real bug where the success receipt shows an incorrect potential payout
(BUG-003). See [`docs/bug-reports.md`](docs/bug-reports.md) for the full record.
