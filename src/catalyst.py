from typing import Dict, List


def classify_catalyst(headline: str) -> Dict:
    """
    Simple rules-based catalyst classifier.
    Later, Gemini can replace or improve this.
    """
    text = (headline or "").lower()

    catalyst_type = "unclear"
    strength = 0
    risk_flags: List[str] = []

    if not text or text in {"no_recent_news_found", "news_fetch_error"}:
        return {
            "catalyst_type": "no_confirmed_news",
            "catalyst_strength": 0,
            "risk_flags": ["missing_catalyst"]
        }

    # Earnings / guidance
    if any(word in text for word in ["earnings", "revenue", "profit", "eps", "quarterly results"]):
        catalyst_type = "earnings_related"
        strength += 15

    if any(word in text for word in ["raises guidance", "raised guidance", "guidance raise", "beats estimates", "beat estimates"]):
        catalyst_type = "earnings_beat_or_guidance_raise"
        strength += 25

    if any(word in text for word in ["misses estimates", "cuts guidance", "lowered guidance", "weak outlook"]):
        catalyst_type = "negative_earnings_or_guidance"
        strength -= 25
        risk_flags.append("negative_fundamental_news")

    # Analyst changes
    if any(word in text for word in ["upgrade", "upgraded", "price target raised", "raises price target"]):
        catalyst_type = "analyst_upgrade"
        strength += 15

    if any(word in text for word in ["downgrade", "downgraded", "price target cut", "cuts price target"]):
        catalyst_type = "analyst_downgrade"
        strength -= 15
        risk_flags.append("analyst_negative")

    # Corporate actions / M&A
    if any(word in text for word in ["acquire", "acquisition", "merger", "buyout", "takeover"]):
        catalyst_type = "m_and_a"
        strength += 20

    if any(word in text for word in ["offering", "dilution", "share sale", "stock sale", "atm program"]):
        catalyst_type = "dilution_or_offering"
        strength -= 30
        risk_flags.append("dilution_risk")

    # Regulation / legal
    if any(word in text for word in ["lawsuit", "probe", "investigation", "sec charges", "doj", "antitrust"]):
        catalyst_type = "legal_or_regulatory_risk"
        strength -= 20
        risk_flags.append("legal_regulatory_risk")

    # Product / AI / contracts
    if any(word in text for word in ["contract", "partnership", "deal", "launches", "new product"]):
        catalyst_type = "business_development"
        strength += 10

    if any(word in text for word in ["ai", "artificial intelligence", "data center", "cloud"]):
        if catalyst_type == "unclear":
            catalyst_type = "ai_or_cloud_related"
        strength += 8

    # Biotech/FDA
    if any(word in text for word in ["fda approval", "approved by fda", "phase 3", "clinical trial"]):
        catalyst_type = "biotech_or_fda"
        strength += 25
        risk_flags.append("binary_event_risk")

    # Generic risk flags
    if any(word in text for word in ["plunges", "falls", "drops", "slumps", "tumbles"]):
        risk_flags.append("negative_price_reaction")

    if any(word in text for word in ["surges", "soars", "jumps", "rallies"]):
        risk_flags.append("gap_chase_risk")

    if not risk_flags:
        risk_flags.append("none_detected")

    return {
        "catalyst_type": catalyst_type,
        "catalyst_strength": max(-50, min(50, strength)),
        "risk_flags": risk_flags
    }
