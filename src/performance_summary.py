from pathlib import Path
import pandas as pd


DATA_PATH = Path("data/paper_trades.csv")


def summarize_performance():
    df = pd.read_csv(DATA_PATH)

    completed_1d = df.dropna(subset=["result_1d_pct"])
    completed_3d = df.dropna(subset=["result_3d_pct"])

    print("\n=== 1-Day Performance ===")
    if not completed_1d.empty:
        print(f"Trades tracked: {len(completed_1d)}")
        print(f"Average return: {completed_1d['result_1d_pct'].mean():.2f}%")
        print(f"Median return: {completed_1d['result_1d_pct'].median():.2f}%")
        print(f"Win rate: {(completed_1d['result_1d_pct'] > 0).mean() * 100:.1f}%")

        if "beat_spy_1d" in completed_1d.columns:
            print(f"Beat SPY rate: {(completed_1d['beat_spy_1d'] == True).mean() * 100:.1f}%")

        if "beat_qqq_1d" in completed_1d.columns:
            print(f"Beat QQQ rate: {(completed_1d['beat_qqq_1d'] == True).mean() * 100:.1f}%")
    else:
        print("No completed 1-day results yet.")

    print("\n=== 3-Day Performance ===")
    if not completed_3d.empty:
        print(f"Trades tracked: {len(completed_3d)}")
        print(f"Average return: {completed_3d['result_3d_pct'].mean():.2f}%")
        print(f"Median return: {completed_3d['result_3d_pct'].median():.2f}%")
        print(f"Win rate: {(completed_3d['result_3d_pct'] > 0).mean() * 100:.1f}%")

        if "beat_spy_3d" in completed_3d.columns:
            print(f"Beat SPY rate: {(completed_3d['beat_spy_3d'] == True).mean() * 100:.1f}%")

        if "beat_qqq_3d" in completed_3d.columns:
            print(f"Beat QQQ rate: {(completed_3d['beat_qqq_3d'] == True).mean() * 100:.1f}%")
    else:
        print("No completed 3-day results yet.")

    print("\n=== By Catalyst Type ===")
    if "catalyst_type" in df.columns and not completed_3d.empty:
        print(
            completed_3d.groupby("catalyst_type")["result_3d_pct"]
            .agg(["count", "mean", "median"])
            .sort_values("mean", ascending=False)
        )


if __name__ == "__main__":
    summarize_performance()
