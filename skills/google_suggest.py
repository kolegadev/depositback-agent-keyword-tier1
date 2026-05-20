"""Google Suggest scraper — free, no API key required.
Fetches autocomplete suggestions from Google for any seed keyword.
"""
import requests
import urllib.parse
import json


def run(seed_keyword: str, language: str = "en", region: str = "us"):
    """
    Returns a list of autocomplete suggestions for the seed keyword.
    """
    encoded = urllib.parse.quote(seed_keyword)
    url = (
        f"http://suggestqueries.google.com/complete/search?"
        f"q={encoded}&hl={language}&gl={region}&client=firefox&ds=yt"
    )
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        data = resp.json()
        suggestions = data[1] if len(data) > 1 else []
        return {
            "seed": seed_keyword,
            "suggestions": suggestions,
            "count": len(suggestions),
        }
    except Exception as e:
        return {"seed": seed_keyword, "error": str(e), "suggestions": [], "count": 0}
