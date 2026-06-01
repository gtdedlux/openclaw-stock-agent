from datetime import datetime
from typing import List, Dict
import yfinance as yf


def _safe_get_nested(data: dict, path: list, default=""):
    """Safely get nested dictionary values."""
    current = data

    for key in path:
        if not isinstance(current, dict):
            return default
        current = current.get(key)

    return current if current is not None else default


def get_latest_news(ticker: str, limit: int = 3) -> List[Dict]:
    """
    Pulls latest news from yfinance.

    yfinance news structure can vary, so this handles both:
    - old flat format: title, publisher, link, providerPublishTime
    - newer nested format: content.title, content.provider.displayName, etc.
    """
    try:
        stock = yf.Ticker(ticker)
        news_items = stock.news or []
    except Exception as e:
        return [{
            "ticker": ticker,
            "headline": "news_fetch_error",
            "publisher": "yfinance",
            "link": "",
            "published": "",
            "error": str(e)
        }]

    results = []

    for item in news_items[:limit]:
        content = item.get("content", {}) if isinstance(item, dict) else {}

        # Try old yfinance format first, then newer nested format.
        title = (
            item.get("title")
            or content.get("title")
            or content.get("headline")
            or ""
        )

        publisher = (
            item.get("publisher")
            or _safe_get_nested(content, ["provider", "displayName"])
            or _safe_get_nested(content, ["provider", "name"])
            or ""
        )

        link = (
            item.get("link")
            or _safe_get_nested(content, ["clickThroughUrl", "url"])
            or _safe_get_nested(content, ["canonicalUrl", "url"])
            or ""
        )

        published_ts = (
            item.get("providerPublishTime")
            or content.get("pubDate")
            or content.get("displayTime")
            or ""
        )

        published = ""

        if isinstance(published_ts, int):
            published = datetime.fromtimestamp(published_ts).isoformat()
        elif isinstance(published_ts, str):
            published = published_ts

        results.append({
            "ticker": ticker,
            "headline": title,
            "publisher": publisher,
            "link": link,
            "published": published,
            "error": ""
        })

    if not results:
        results.append({
            "ticker": ticker,
            "headline": "no_recent_news_found",
            "publisher": "",
            "link": "",
            "published": "",
            "error": ""
        })

    return results