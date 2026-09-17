import re
from typing import Dict, Tuple

BULLISH_TERMS = {
    "surge": 2.0, "soar": 2.0, "rally": 2.0, "record high": 2.5, "all-time high": 2.5,
    "beat estimates": 2.0, "strong earnings": 2.0, "profit jumped": 2.0, "gain": 1.0,
    "growth": 1.0, "bullish": 2.0, "upgrade": 1.5, "outperform": 1.5, "expansion": 1.0,
    "recovery": 1.5, "dividend increase": 1.5, "rebound": 1.5, "optimism": 1.0,
    "rate cut": 1.5, "cooling inflation": 1.5, "breakout": 1.5, "inflow": 1.0, "positive": 1.0
}

BEARISH_TERMS = {
    "plunge": -2.0, "slump": -2.0, "tumble": -2.0, "crash": -2.5, "sell-off": -2.0,
    "recession": -2.0, "stagflation": -2.5, "miss estimates": -2.0, "loss": -1.5,
    "layoffs": -1.5, "downgrade": -1.5, "bearish": -2.0, "decline": -1.0, "fall": -1.0,
    "rate hike": -1.5, "persistent inflation": -1.5, "debt crisis": -2.5, "bankruptcy": -2.5,
    "warning": -1.0, "investigation": -1.5, "downward": -1.0, "outflow": -1.0, "negative": -1.0
}

SECTOR_KEYWORDS = {
    "Tech & AI": ["ai", "nvidia", "apple", "microsoft", "google", "meta", "chips", "semiconductor", "software", "tech", "cloud"],
    "Economy & Fed": ["fed", "federal reserve", "powell", "inflation", "cpi", "gdp", "interest rate", "treasury", "jobs report", "unemployment"],
    "Crypto & Web3": ["bitcoin", "crypto", "ethereum", "btc", "eth", "blockchain", "etf", "binance", "coinbase", "token"],
    "Banking & Finance": ["bank", "jpmorgan", "goldman sachs", "credit", "lending", "morgan stanley", "wall street", "bonds"],
    "Energy & Commodities": ["oil", "gas", "opec", "energy", "petroleum", "crude", "gold", "silver", "metals"],
    "Automotive & Retail": ["tesla", "ev", "auto", "retail", "consumer", "sales", "walmart", "amazon"]
}

class SentimentService:
    @staticmethod
    def analyze(text: str) -> Dict[str, any]:
        if not text:
            return {"sentiment": "neutral", "score": 0.0, "label": "Neutral", "sector": "Economy"}

        lower = text.lower()
        score = 0.0
        matches_bull = 0
        matches_bear = 0

        for term, weight in BULLISH_TERMS.items():
            pattern = r'\b' + re.escape(term) + r'\b'
            matches = len(re.findall(pattern, lower))
            if matches:
                score += weight * matches
                matches_bull += matches

        for term, weight in BEARISH_TERMS.items():
            pattern = r'\b' + re.escape(term) + r'\b'
            matches = len(re.findall(pattern, lower))
            if matches:
                score += weight * matches # weight is negative
                matches_bear += matches

        # Normalization to [-1.0, 1.0]
        total_matches = matches_bull + matches_bear
        if total_matches > 0:
            normalized_score = max(-1.0, min(1.0, score / (total_matches * 2.0)))
        else:
            normalized_score = 0.0

        if normalized_score >= 0.2:
            sentiment = "bullish"
            label = "Bullish" if normalized_score >= 0.5 else "Moderately Bullish"
        elif normalized_score <= -0.2:
            sentiment = "bearish"
            label = "Bearish" if normalized_score <= -0.5 else "Moderately Bearish"
        else:
            sentiment = "neutral"
            label = "Neutral"

        # Detect Sector
        detected_sector = "Economy & Fed"
        highest_sector_count = 0
        for sector, keywords in SECTOR_KEYWORDS.items():
            count = sum(len(re.findall(r'\b' + re.escape(kw) + r'\b', lower)) for kw in keywords)
            if count > highest_sector_count:
                highest_sector_count = count
                detected_sector = sector

        return {
            "sentiment": sentiment,
            "score": round(normalized_score, 2),
            "label": label,
            "sector": detected_sector
        }
