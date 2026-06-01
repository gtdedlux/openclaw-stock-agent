from datetime import time
from typing import Dict, List

import pandas as pd
import yfinance as yf


def get_liquidity_snapshot(ticker: str) -> Dict:
    """
    Prototype liquidity/premarket filter using yfinance.

    Limitations:
    - yfinance premarket data may be delayed/incomplete.
    - For serious trading, replace with Polygon, Alpaca, Finnhub, Benzinga, etc.
    """

    result = {
        "premarket_price": None,
        "premarket_change_pct": None,
        "premarket_volume": 0,
        "avg_daily_volume": None,
        "premarket_volume_ratio": None,
        "dollar_volume": 0,
        "liquidity_pass": False,
        "liquidity_flags": []
    }

    try:
        stock = yf.Ticker(ticker)

        # 5-day daily data for previous close and average volume.
        daily = stock.history(period="20d", interval="1d")

        # 1-day 1-minute data including pre/post-market.
        intraday = stock.history(period="1d", interval="1m", prepost=True)
    except Exception as e:
        result["liquidity_flags"].append(f"liquidity_fetch_error:{e}")
        return result

    if daily.empty:
        result["liquidity_flags"].append("missing_daily_data")
        return result

    if intraday.empty:
        result["liquidity_flags"].append("missing_intraday_data")
        return result

    # Previous close from daily candles.
    prev_close = float(daily["Close"].iloc[-2]) if len(daily) >= 2 else float(daily["Close"].iloc[-1])

    # Average daily volume over recent days.
    avg_daily_volume = float(daily["Volume"].tail(20).mean())
    result["avg_daily_volume"] = round(avg_daily_volume)

    # yfinance index is usually timezone-aware.
    # Convert to US/Eastern because market hours are defined in ET.
    if intraday.index.tz is not None:
        intraday = intraday.tz_convert("America/New_York")

    # Premarket window: 4:00 AM to 9:30 AM ET.
    premarket = intraday[
        (intraday.index.time >= time(4, 0)) &
        (intraday.index.time < time(9, 30))
    ]

    if premarket.empty:
        result["liquidity_flags"].append("no_premarket_rows")
        return result

    # Last available premarket close.
    last_premarket_price = float(premarket["Close"].dropna().iloc[-1])
    premarket_change_pct = ((last_premarket_price - prev_close) / prev_close) * 100

    # Premarket volume. Caution: Yahoo premarket volume may be incomplete.
    premarket_volume = float(premarket["Volume"].fillna(0).sum())

    dollar_volume = premarket_volume * last_premarket_price

    if avg_daily_volume > 0:
        premarket_volume_ratio = premarket_volume / avg_daily_volume
    else:
        premarket_volume_ratio = None

    result["premarket_price"] = round(last_premarket_price, 2)
    result["premarket_change_pct"] = round(premarket_change_pct, 2)
    result["premarket_volume"] = round(premarket_volume)
    result["premarket_volume_ratio"] = round(premarket_volume_ratio, 4) if premarket_volume_ratio is not None else None
    result["dollar_volume"] = round(dollar_volume)

    flags: List[str] = []

    # Basic tradability filters.
    volume_unavailable = premarket_volume == 0

    if volume_unavailable:
        flags.append("premarket_volume_unavailable_yfinance")
    else:
        if premarket_volume < 50_000:
            flags.append("low_premarket_volume")

        if dollar_volume < 5_000_000:
            flags.append("low_premarket_dollar_volume")

        if premarket_volume_ratio is not None and premarket_volume_ratio < 0.01:
            flags.append("premarket_volume_ratio_under_1pct_avg_daily")

    result["liquidity_flags"] = flags

    # Pass/fail rule.
    if volume_unavailable:
        result["liquidity_pass"] = None
    else:
        result["liquidity_pass"] = (
            last_premarket_price >= 5 and
            avg_daily_volume >= 1_000_000 and
            premarket_volume >= 50_000 and
            dollar_volume >= 5_000_000
        )

    return result
