# Repository Guidelines

## Project Structure & Module Organization

This repository is a flat Python script project for Google Fit data collection, analysis, and reporting. Core API access and summaries live in `fitness_tracker.py`; authentication is handled by `google_fit_auth.py`. Reporting and automation scripts include `fitness_briefing.py`, `fitness_alerts.py`, `dashboard_updater.py`, `night_mode.py`, and `chart_generator.py`. Domain-specific helpers include `cycling_coach.py`, `improvement_engine.py`, and `wallet_tracker.py`. The current test runner is `test_suite.py` at the repository root. Keep new scripts focused and colocated unless a package structure is introduced deliberately.

## Build, Test, and Development Commands

- `python google_fit_auth.py`: start the Google OAuth flow and create local tokens.
- `python fitness_tracker.py`: fetch and print the default daily summary.
- `python fitness_tracker.py weekly`: fetch weekly trend data.
- `python fitness_briefing.py`: generate the morning fitness briefing.
- `python test_suite.py`: run the custom test suite.

The project has no build step. Install runtime dependencies in your environment before running scripts: `google-auth-oauthlib`, `google-auth`, and, for charts, `matplotlib` and `numpy`.

## Coding Style & Naming Conventions

Use Python 3.8+ and follow standard PEP 8 conventions: four-space indentation, `snake_case` for functions and variables, `PascalCase` for classes, and uppercase names for constants such as token paths. Prefer small functions with explicit inputs and outputs. Keep script entry points under `if __name__ == "__main__":` so modules remain importable by tests. Use `pathlib.Path` for filesystem paths, matching the existing code.

## Testing Guidelines

Tests are currently organized in `test_suite.py` with methods named `test_<feature>`. Add focused tests there when changing script behavior, especially for parsing, summary formatting, token handling, and generated recommendations. Use mocks for network calls to Google APIs and avoid relying on live credentials in tests. Before submitting changes, run:

```bash
python test_suite.py
```

## Commit & Pull Request Guidelines

The repository history currently uses short, imperative commit messages such as `Initial commit: Google Fit data tools`. Continue with concise messages that describe the change, for example `Add weekly chart export` or `Fix token refresh error handling`.

Pull requests should include a short summary, the commands used to test the change, and any setup or credential implications. Include screenshots or generated chart examples when changing visual output.

## Security & Configuration Tips

Do not commit OAuth credentials, access tokens, generated token files, or personal fitness exports. Store Google credentials at `credentials/google-fit-credentials.json` as described in `README.md`, and keep local token files out of version control.
