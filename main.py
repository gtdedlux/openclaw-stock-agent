from datetime import datetime
from pathlib import Path
import pandas as pd
import yfinance as yf
from src.news import get_latest_news
from src.catalyst import classify_catalyst
from src.liquidity import get_liquidity_snapshot

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)
pd.set_option("display.max_colwidth", 80)

WATCHLIST = [
    "AAPL", "MSFT", "NVDA", "AMD", "TSLA",
    "META", "GOOGL", "AMZN", "PLTR", "SMCI"
]

REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)

def get_stock_snapshot(ticker: str) -> dict:
    stock = yf.Ticker(ticker)
    hist = stock.history(period="5d", interval="1d")

    if hist.empty:
        return {
            "ticker": ticker,
            "error": "No price data found"
        }

    last_close = float(hist["Close"].iloc[-1])
    prev_close = float(hist["Close"].iloc[-2]) if len(hist) > 1 else last_close
    change_pct = ((last_close - prev_close) / prev_close) * 100 if prev_close else 0

    return {
        "ticker": ticker,
        "last_close": round(last_close, 2),
        "prev_close": round(prev_close, 2),
        "change_pct": round(change_pct, 2),
    }

def score_stock(row: dict) -> int:
    score = 50

    change_pct = row.get("change_pct") or 0
    last_close = row.get("last_close") or 0
    catalyst_strength = row.get("catalyst_strength") or 0
    premarket_volume_ratio = row.get("premarket_volume_ratio")
    dollar_volume = row.get("dollar_volume") or 0

    # Basic price momentum
    if change_pct > 1:
        score += 10
    if change_pct > 3:
        score += 10

    # Avoid very low-priced names
    if last_close > 5:
        score += 10
    else:
        score -= 20

    # Avoid chasing extreme moves
    if change_pct > 12:
        score -= 10
    if change_pct > 20:
        score -= 15

    # Catalyst adjustment
    score += catalyst_strength

    # Liquidity adjustment
    liquidity_pass = row.get("liquidity_pass")

    if liquidity_pass is True:
        score += 10
    elif liquidity_pass is False:
        score -= 15
    else:
        # Unknown liquidity; do not heavily punish.
        score -= 3
        
    if premarket_volume_ratio is not None:
        if premarket_volume_ratio >= 0.05:
            score += 10
        elif premarket_volume_ratio >= 0.02:
            score += 5
        elif premarket_volume_ratio < 0.01:
            score -= 10

    if dollar_volume >= 10_000_000:
        score += 5

    return max(0, min(100, int(score)))

def get_market_context() -> dict:
    context = {}

    for ticker in ["SPY", "QQQ", "IWM"]:
        snapshot = get_stock_snapshot(ticker)
        context[ticker] = snapshot.get("change_pct")

    return context

def main():
    rows = []

    for ticker in WATCHLIST:
        snapshot = get_stock_snapshot(ticker)
        
        if "error" not in snapshot:
            latest_news = get_latest_news(ticker, limit=1)
            top_news = latest_news[0] if latest_news else {}

            snapshot["latest_headline"] = top_news.get("headline", "")
            snapshot["news_source"] = top_news.get("publisher", "")
            snapshot["news_link"] = top_news.get("link", "")

            catalyst = classify_catalyst(snapshot["latest_headline"])

            snapshot["catalyst_type"] = catalyst["catalyst_type"]
            snapshot["catalyst_strength"] = catalyst["catalyst_strength"]
            snapshot["risk_flags"] = ", ".join(catalyst["risk_flags"])

            liquidity = get_liquidity_snapshot(ticker)

            snapshot["premarket_price"] = liquidity["premarket_price"]
            snapshot["premarket_change_pct"] = liquidity["premarket_change_pct"]
            snapshot["premarket_volume"] = liquidity["premarket_volume"]
            snapshot["avg_daily_volume"] = liquidity["avg_daily_volume"]
            snapshot["premarket_volume_ratio"] = liquidity["premarket_volume_ratio"]
            snapshot["dollar_volume"] = liquidity["dollar_volume"]
            snapshot["liquidity_pass"] = liquidity["liquidity_pass"]
            snapshot["liquidity_flags"] = ", ".join(liquidity["liquidity_flags"])

            snapshot["score"] = score_stock(snapshot)
        
        rows.append(snapshot)

    df = pd.DataFrame(rows)
    if "score" in df.columns:
        df = df.sort_values("score", ascending=False)
        
    market_context = get_market_context()

    today = datetime.now().strftime("%Y-%m-%d")
    report_path = REPORT_DIR / f"{today}-premarket-watchlist.md"
    
    report_columns = [
        "ticker",
        "last_close",
        "prev_close",
        "change_pct",
        "premarket_price",
        "premarket_change_pct",
        "premarket_volume",
        "premarket_volume_ratio",
        "dollar_volume",
        "liquidity_pass",
        "score",
        "latest_headline",
        "news_source",
        "catalyst_type",
        "catalyst_strength",
        "risk_flags",
        "liquidity_flags"
    ]


    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# Premarket Watchlist — {today}\n\n")
        f.write("Prototype only. This is for paper-trading review, not financial advice.\n\n")

        f.write("## Market Context\n\n")
        for ticker, change in market_context.items():
            f.write(f"- {ticker}: {change}%\n")
        f.write("\n")

        f.write("## Watchlist\n\n")
        f.write(df.to_markdown(index=False))

    # Save today's watchlist to the paper-trading log
    log_path = Path("data/paper_trades.csv")
    log_path.parent.mkdir(exist_ok=True)

    df_to_log = df.copy()
    df_to_log.insert(0, "date", today)
    df_to_log["result_1d_pct"] = None
    df_to_log["result_3d_pct"] = None
    df_to_log["notes"] = "prototype_fixed_watchlist"

    if log_path.exists() and log_path.stat().st_size > 0:
        old = pd.read_csv(log_path)
        combined = pd.concat([old, df_to_log], ignore_index=True)
    else:
        combined = df_to_log

    combined.to_csv(log_path, index=False)

    print(f"Report written to: {report_path}")
    print(f"Paper-trading log updated: {log_path}")
    display_columns = [
        "ticker",
        "change_pct",
        "premarket_change_pct",
        "score",
        "premarket_volume",
        "premarket_volume_ratio",
        "dollar_volume",
        "liquidity_pass",
        "latest_headline",
        "news_source",
        "catalyst_type",
        "catalyst_strength",
        "risk_flags",
        "liquidity_flags"
    ]

    existing_columns = [col for col in display_columns if col in df.columns]
    print(df[existing_columns])
    
    

if __name__ == "__main__":
    main()
