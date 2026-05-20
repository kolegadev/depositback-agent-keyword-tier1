"""Multi-Source Keyword Suggest — adapted from ClawHub keyword-research1 by brasco05.
Fetches real-time autocomplete suggestions from Google, YouTube, Amazon, DuckDuckGo, and Bing.
No API key required.
"""
import json
import urllib.request
import urllib.parse
import time


def fetch_google(keyword, lang="en", region="us"):
    url = (
        f"https://suggestqueries.google.com/complete/search?"
        f"client=firefox&q={urllib.parse.quote(keyword)}&hl={lang}&gl={region}"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
            return data[1] if len(data) > 1 else []
    except Exception:
        return []


def fetch_youtube(keyword, region="us"):
    url = (
        f"https://suggestqueries.google.com/complete/search?"
        f"client=youtube&q={urllib.parse.quote(keyword)}&ds=yt"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
            return data[1] if len(data) > 1 else []
    except Exception:
        return []


def fetch_amazon(keyword, region="us"):
    tld = "com" if region == "us" else region
    url = (
        f"https://completion.amazon.{tld}/search/complete?"
        f"method=completion&q={urllib.parse.quote(keyword)}&search-alias=aps"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
            return data[1] if len(data) > 1 else []
    except Exception:
        return []


def fetch_ddg(keyword):
    url = f"https://duckduckgo.com/ac/?q={urllib.parse.quote(keyword)}&type=list"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
            return data[1] if len(data) > 1 else []
    except Exception:
        return []


def fetch_bing(keyword, lang="en"):
    url = (
        f"https://api.bing.com/osjson.aspx?"
        f"query={urllib.parse.quote(keyword)}&language={lang}"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
            return data[1] if len(data) > 1 else []
    except Exception:
        return []


def expand_suggestions(base_suggestions, source_fn, lang="en"):
    all_expanded = []
    seen = set(base_suggestions)
    for suggestion in base_suggestions[:5]:
        time.sleep(0.25)
        expanded = source_fn(suggestion, lang)
        for s in expanded:
            if s not in seen:
                seen.add(s)
                all_expanded.append(s)
    return all_expanded


def run(keyword: str, sources: list = None, lang: str = "en", region: str = "us", expand: bool = False):
    """
    Fetch multi-source autocomplete suggestions.
    
    sources: list of strings, e.g. ["google", "youtube", "amazon", "ddg", "bing"]
    expand: if True, fetches 2nd-level suggestions from Google for ~10x more keywords
    """
    if sources is None:
        sources = ["google", "youtube", "amazon", "ddg", "bing"]

    source_map = {
        "google": lambda: fetch_google(keyword, lang, region),
        "youtube": lambda: fetch_youtube(keyword, region),
        "amazon": lambda: fetch_amazon(keyword, region),
        "ddg": lambda: fetch_ddg(keyword),
        "bing": lambda: fetch_bing(keyword, lang),
    }

    results = {}
    for src in sources:
        fn = source_map.get(src)
        if not fn:
            continue
        base = fn()
        if expand and src == "google" and base:
            expanded = expand_suggestions(base, fetch_google, lang)
            results[src] = {"base": base, "expanded": expanded}
        else:
            results[src] = base

    total = 0
    for src, data in results.items():
        if isinstance(data, dict):
            total += len(data.get("base", [])) + len(data.get("expanded", []))
        else:
            total += len(data)

    return {
        "seed": keyword,
        "sources": sources,
        "lang": lang,
        "region": region,
        "expand": expand,
        "results": results,
        "total_suggestions": total,
    }
