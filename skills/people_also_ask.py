"""People Also Ask scraper — free, no API key required.
Scrapes Google's "People also ask" questions for a given keyword.
"""
import requests
import urllib.parse
import re


def run(keyword: str, lang: str = "en", region: str = "us", max_questions: int = 10):
    """Fetch People Also Ask questions from Google SERP."""
    encoded = urllib.parse.quote(keyword)
    url = f"https://www.google.com/search?q={encoded}&hl={lang}&gl={region}"
    try:
        resp = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        resp.raise_for_status()
        html = resp.text

        # Extract PAA questions using regex
        pattern = r'data-qh="[^"]*"[^>]*aria-level="3"[^>]*>([^<]+)</span>'
        matches = re.findall(pattern, html)
        
        # Alternative pattern
        if not matches:
            pattern2 = r'<span[^>]*class="[^"]*BNeawe[^"]*"[^>]*>([^<]+)</span>'
            matches = re.findall(pattern2, html)

        questions = [q.strip() for q in matches if q.strip() and "?" in q][:max_questions]

        return {
            "keyword": keyword,
            "questions": questions,
            "count": len(questions),
        }
    except Exception as e:
        return {"keyword": keyword, "error": str(e), "questions": [], "count": 0}
