from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf


DATA_PATH = Path("data/paper_trades.csv")


def get_close_on_or_after(ticker: str, target_date: pd.Timestamp, max_days_ahead: int = 7):
    """
    Get the first available market close on or after target_date.
    This handles weekends and market holidays approximately.
    """
    start = target_date.strftime("%Y-%m-%d")
    end = (target_date + timedelta(days=max_days_ahead)).strftime("%Y-%m-%d")

    try:
        hist = yf.Ticker(ticker).history(start=start, end=end, interval="1d")
    except Exception:
        return None, None

    if hist.empty:
        return None, None

    close_price = float(hist["Close"].iloc[0])
    actual_date = hist.index[0].date().isoformat()

    return close_price, actual_date


def pct_return(start_price, end_price):
    if start_price is None or end_price is None:
        return None
    if start_price == 0:
        return None

    return round(((end_price - start_price) / start_price) * 100, 2)


def update_results():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing file: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    required_cols = ["date", "ticker", "last_close"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column in paper_trades.csv: {col}")

    # Add result columns if missing.
    default_columns = {
        "close_1d": None,
        "close_1d_date": None,
        "result_1d_pct": None,
        "spy_1d_pct": None,
        "qqq_1d_pct": None,
        "beat_spy_1d": None,
        "beat_qqq_1d": None,
        "close_3d": None,
        "close_3d_date": None,
        "result_3d_pct": None,
        "spy_3d_pct": None,
        "qqq_3d_pct": None,
        "beat_spy_3d": None,
        "beat_qqq_3d": None,
    }

    for col, default in default_columns.items():
        if col not in df.columns:
            df[col] = default

    today = pd.Timestamp(datetime.now().date())

    for idx, row in df.iterrows():
        ticker = row["ticker"]

        # Skip benchmark rows if your scanner logs SPY/QQQ themselves.
        if ticker in {"SPY", "QQQ"}:
            continue

        try:
            pick_date = pd.Timestamp(row["date"])
        except Exception:
            continue

        start_price = row.get("last_close")

        if pd.isna(start_price):
            continue

        start_price = float(start_price)

        # 1-day result
        target_1d = pick_date + timedelta(days=1)

        if pd.isna(row.get("result_1d_pct")) and today >= target_1d:
            close_1d, actual_1d_date = get_close_on_or_after(ticker, target_1d)
            spy_1d, _ = get_close_on_or_after("SPY", target_1d)
            qqq_1d, _ = get_close_on_or_after("QQQ", target_1d)

            stock_ret_1d = pct_return(start_price, close_1d)
            spy_ret_1d = pct_return(start_price=None, end_price=None)
            qqq_ret_1d = pct_return(start_price=None, end_price=None)

            # Compare benchmarks from their own pick-date close.
            spy_start, _ = get_close_on_or_after("SPY", pick_date)
            qqq_start, _ = get_close_on_or_after("QQQ", pick_date)

            spy_ret_1d = pct_return(spy_start, spy_1d)
            qqq_ret_1d = pct_return(qqq_start, qqq_1d)

            df.at[idx, "close_1d"] = close_1d
            df.at[idx, "close_1d_date"] = actual_1d_date
            df.at[idx, "result_1d_pct"] = stock_ret_1d
            df.at[idx, "spy_1d_pct"] = spy_ret_1d
            df.at[idx, "qqq_1d_pct"] = qqq_ret_1d

            if stock_ret_1d is not None and spy_ret_1d is not None:
                df.at[idx, "beat_spy_1d"] = stock_ret_1d > spy_ret_1d

            if stock_ret_1d is not None and qqq_ret_1d is not None:
                df.at[idx, "beat_qqq_1d"] = stock_ret_1d > qqq_ret_1d

        # 3-day result
        target_3d = pick_date + timedelta(days=3)

        if pd.isna(row.get("result_3d_pct")) and today >= target_3d:
            close_3d, actual_3d_date = get_close_on_or_after(ticker, target_3d)
            spy_3d, _ = get_close_on_or_after("SPY", target_3d)
            qqq_3d, _ = get_close_on_or_after("QQQ", target_3d)

            stock_ret_3d = pct_return(start_price, close_3d)

            spy_start, _ = get_close_on_or_after("SPY", pick_date)
            qqq_start, _ = get_close_on_or_after("QQQ", pick_date)

            spy_ret_3d = pct_return(spy_start, spy_3d)
            qqq_ret_3d = pct_return(qqq_start, qqq_3d)

            df.at[idx, "close_3d"] = close_3d
            df.at[idx, "close_3d_date"] = actual_3d_date
            df.at[idx, "result_3d_pct"] = stock_ret_3d
            df.at[idx, "spy_3d_pct"] = spy_ret_3d
            df.at[idx, "qqq_3d_pct"] = qqq_ret_3d

            if stock_ret_3d is not None and spy_ret_3d is not None:
                df.at[idx, "beat_spy_3d"] = stock_ret_3d > spy_ret_3d

            if stock_ret_3d is not None and qqq_ret_3d is not None:
                df.at[idx, "beat_qqq_3d"] = stock_ret_3d > qqq_ret_3d

    df.to_csv(DATA_PATH, index=False)

    print(f"Updated results in {DATA_PATH}")
    print(df.tail(10)[[
        "date",
        "ticker",
        "score",
        "result_1d_pct",
        "spy_1d_pct",
        "beat_spy_1d",
        "result_3d_pct",
        "spy_3d_pct",
        "beat_spy_3d"
    ]])


if __name__ == "__main__":
    update_results()
