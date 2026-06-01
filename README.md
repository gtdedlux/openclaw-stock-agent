# OpenClaw Stock Agent

A local premarket stock research pipeline that uses Python and OpenClaw to generate a ranked paper-trading watchlist.

This project is designed to help review short-term stock candidates using price movement, recent news headlines, catalyst classification, liquidity checks, and paper-trading performance tracking.

> This project is for research and paper-trading review only. It is not financial advice, does not place trades, and should not be used as an automated trading system.

## Features

* Pulls recent price data for a watchlist of stocks
* Fetches recent news headlines
* Classifies potential catalysts using rules-based logic
* Adds catalyst strength and risk flags
* Checks premarket price and liquidity fields
* Generates a ranked Markdown watchlist report
* Logs watchlist results to `paper_trades.csv`
* Tracks 1-day and 3-day paper-trading performance
* Compares results against SPY and QQQ
* Includes a Streamlit dashboard for easier review
* Can be wrapped as an OpenClaw skill

## Current Status

This is an MVP/prototype.

The system currently works as a local research assistant, but it still has limitations:

* `yfinance` data may be delayed, incomplete, or unreliable for premarket volume
* The watchlist is currently predefined rather than fully market-wide
* Catalyst classification is rules-based and should not be treated as definitive
* Scores are ranking heuristics, not predictions
* Results must be validated over time using paper-trading performance

## Project Structure

```text
premarket-stock-agent/
  main.py
  dashboard.py
  requirements.txt
  README.md
  LICENSE
  .gitignore
  src/
    news.py
    catalyst.py
    liquidity.py
    update_results.py
    performance_summary.py
  data/
    paper_trades.csv    # generated locally, not committed
  reports/
    YYYY-MM-DD-premarket-watchlist.md
```

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

If `requirements.txt` does not exist yet, create it with:

```bash
pip freeze > requirements.txt
```

## Run the Scanner

```bash
python main.py
```

This generates:

```text
reports/YYYY-MM-DD-premarket-watchlist.md
data/paper_trades.csv
```

## Update Paper-Trading Results

```bash
python src/update_results.py
```

This updates logged picks with 1-day and 3-day performance results when enough time has passed.

## View Performance Summary

```bash
python src/performance_summary.py
```

This prints summary statistics such as average return, median return, win rate, and whether picks beat SPY/QQQ.

## Run the Dashboard

```bash
streamlit run dashboard.py
```

The dashboard provides a cleaner way to inspect:

* latest watchlist
* ranked candidates
* catalyst types
* risk flags
* liquidity status
* historical paper-trading results

## OpenClaw Skill Usage

This project can be run through an OpenClaw skill wrapper.

Example skill location:

```text
~/.openclaw/skills/premarket-stock-research/
```

Example `run.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$HOME/projects/premarket-stock-agent"

cd "$PROJECT_DIR"
source .venv/bin/activate

python main.py
python src/update_results.py
python src/performance_summary.py
```

Then run from OpenClaw:

```text
Run premarket-stock-research. Show only the command output and keep the response concise.
```

## Scoring Logic

The current score is based on:

* recent price movement
* catalyst strength
* risk flags
* basic liquidity checks
* premarket movement when available

Scores are not probabilities. They are only used to rank watchlist candidates for paper-trading review.

## Data Sources

Current prototype source:

* `yfinance`

Known limitation:

* Premarket volume from `yfinance` may be unavailable or unreliable. When unavailable, the system marks it as `premarket_volume_unavailable_yfinance`.

Future improvements may include:

* Alpaca
* Finnhub
* Polygon/Massive
* Benzinga
* SEC EDGAR filings
* earnings calendars
* analyst upgrade/downgrade feeds

## Disclaimer

This project is for educational research and paper-trading review only.

It does not provide financial advice, investment advice, or trade recommendations. It does not guarantee future performance. Any real trading decision requires independent research, risk management, and compliance with applicable laws and broker rules.

## License

This project is licensed under the MIT License.

