# Google Fit Data Project

Python tools for fetching, analyzing, and reporting fitness data from Google Fit API.

## Scripts

| Script | Purpose |
|--------|---------|
| `fitness_tracker.py` | Core data fetcher + daily/weekly summaries |
| `google_fit_auth.py` | OAuth device flow for headless auth |
| `fitness_alerts.py` | Proactive alerts based on patterns |
| `fitness_briefing.py` | Morning briefing generator |
| `chart_generator.py` | Visual chart generation |
| `cycling_coach.py` | Cycling-specific coaching insights |
| `dashboard_updater.py` | Dashboard data refresh |
| `improvement_engine.py` | Performance tracking & recommendations |
| `night_mode.py` | Evening/sleep-focused reports |
| `test_suite.py` | Test suite for all components |
| `wallet_tracker.py` | Health-related expense tracking |

## Setup

1. Place your Google OAuth credentials in `credentials/google-fit-credentials.json`
2. Run `google_fit_auth.py` to get tokens
3. Use `fitness_tracker.py` to fetch data

## Usage

```bash
# Daily summary (yesterday)
python fitness_tracker.py

# Weekly trends
python fitness_tracker.py weekly

# Morning briefing
python fitness_briefing.py
```

## Requirements

- Python 3.8+
- `google-auth-oauthlib`
- `google-auth`

## License

MIT
