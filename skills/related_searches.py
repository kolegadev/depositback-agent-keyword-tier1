"""Related Searches scraper — free, no API key required.
Scrapes Google's "Related searches" section at the bottom of SERP.
"""
import requests
import urllib.parse
import re


def run(keyword: str, lang: str = "en", region: str = "us", max_results: int = 20):
    """Fetch related searches from Google SERP."""
    encoded = urllib.parse.quote(keyword)
    url = f"https://www.google.com/search?q={encoded}&hl={lang}&gl={region}"
    try:
        resp = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        resp.raise_for_status()
        html = resp.text

        # Look for related searches block
        pattern = r'<a[^>]*class="[^"]*nCaOhf[^"]*"[^>]*><div[^>]*>([^<]+)</div></a>'
        matches = re.findall(pattern, html)

        if not matches:
            # Fallback pattern
            pattern2 = r'<a[^>]*href="[^"]*relatedsearch[^"]*"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern2, html)

        searches = [s.strip() for s in matches if s.strip()][:max_results]

        return {
            "keyword": keyword,
            "related_searches": searches,
            "count": len(searches),
        }
    except Exception as e:
        return {"keyword": keyword, "error": str(e), "related_searches": [], "count": 0}
