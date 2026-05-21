"""Google Trends skill — free, no API key required.
Uses the unofficial Google Trends API to get interest-over-time and related queries.
"""
import requests
import urllib.parse


def run(keywords: list, timeframe: str = "today 12-m", geo: str = "US"):
    """
    keywords: list of up to 5 keywords to compare
    timeframe: e.g. 'today 12-m', 'today 5-y', 'now 7-d'
    geo: region code, e.g. 'US', 'GB', 'CA'
    """
    if isinstance(keywords, str):
        keywords = [keywords]
    keywords = keywords[:5]

    # Build the comparison token
    token = ",".join(keywords)
    encoded = urllib.parse.quote(token)

    # Related queries endpoint (unofficial)
    url = (
        f"https://trends.google.com/trends/api/explore?"
        f"hl=en-US&tz=-480&req={{%22comparisonItem%22:[{{%22keyword%22:%22{encoded}%22,"
        f"%22geo%22:%22{geo}%22,%22time%22:%22{timeframe}%22}}],"
        f"%22category%22:0,%22property%22:%22%22}}&token=APP6_UEAAAAAZ"
    )

    try:
        resp = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        })
        # Google Trends returns JSONP-like data starting with )]}",

        text = resp.text
        if text.startswith(")]}\',"):
            text = text[5:]
        data = __import__('json').loads(text)

        widgets = data.get("widgets", [])
        related_queries_widget = next((w for w in widgets if w.get("id") == "RELATED_QUERIES"), None)

        related = {}
        if related_queries_widget:
            req_body = related_queries_widget.get("request", {})
            token = related_queries_widget.get("token", "")
            req_url = (
                f"https://trends.google.com/trends/api/widgetdata/relatedsearches?"
                f"hl=en-US&tz=-480&req={urllib.parse.quote(__import__('json').dumps(req_body))}"
                f"&token={urllib.parse.quote(token)}"
            )
            r2 = requests.get(req_url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            t2 = r2.text
            if t2.startswith(")]}\',"):
                t2 = t2[5:]
            d2 = __import__('json').loads(t2)
            for entry in d2.get("default", {}).get("rankedList", []):
                for item in entry.get("rankedKeyword", []):
                    term = item.get("query", "")
                    if term:
                        related[term] = item.get("value", 0)

        return {
            "keywords": keywords,
            "timeframe": timeframe,
            "geo": geo,
            "related_queries": related,
            "total_related": len(related),
        }
    except Exception as e:
        return {"keywords": keywords, "error": str(e), "related_queries": {}, "total_related": 0}
