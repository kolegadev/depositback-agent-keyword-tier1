"""Datamuse API skill — free, no API key required.
Provides semantic keyword expansion, synonyms, related words, and phrases.
"""
import requests
import urllib.parse


def run(seed_keyword: str, max_results: int = 30, relation: str = "ml"):
    """
    relation options:
      ml  = means like (related meaning)
      sl  = sounds like
      sp  = spelled like
      rel_jja = popular nouns modified by the adjective
      rel_jjb = popular adjectives to modify the noun
      rel_syn = synonyms
      rel_ant = antonyms
      rel_trg = triggered by (statistically associated)
    """
    encoded = urllib.parse.quote(seed_keyword)
    url = (
        f"https://api.datamuse.com/words?{relation}={encoded}"
        f"&max={max_results}&md=p"
    )
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        words = resp.json()
        results = []
        for w in words:
            results.append({
                "word": w.get("word"),
                "score": w.get("score"),
                "parts_of_speech": w.get("tags", []),
            })
        return {
            "seed": seed_keyword,
            "relation": relation,
            "expansions": results,
            "count": len(results),
        }
    except Exception as e:
        return {"seed": seed_keyword, "error": str(e), "expansions": [], "count": 0}
