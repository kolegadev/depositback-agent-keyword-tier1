"""Keyword Discovery skill for Tier 1 — Core Transactional Keywords.
Orchestrates google_suggest + datamuse_expand + moonshot to produce
a structured transactional keyword portfolio.
"""
import json
import os
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SKILLS_DIR))

import google_suggest
import datamuse_expand
import moonshot

TIER1_SEEDS = [
    "security deposit demand letter",
    "security deposit demand letter template",
    "how to get security deposit back",
    "landlord won't return security deposit",
    "security deposit return letter",
    "demand letter for security deposit",
    "security deposit letter to landlord",
    "letter to landlord about security deposit",
    "how to write security deposit letter",
    "security deposit refund letter",
]


def run():
    portfolio = []
    for seed in TIER1_SEEDS:
        print(f"   🔍 Discovering: {seed}")

        # 1. Google autocomplete long-tail variants
        suggest = google_suggest.run(seed)
        variants = suggest.get("suggestions", [])

        # 2. Datamuse semantic expansion
        semantic = datamuse_expand.run(seed, max_results=20, relation="ml")
        related = [r["word"] for r in semantic.get("expansions", []) if r.get("score", 0) > 500]

        # 3. Moonshot intent classification & difficulty estimation
        prompt = f"""You are an expert SEO keyword analyst for a US tenant-rights SaaS called DepositBack.
Analyze this keyword: "{seed}"

Provide ONLY a JSON object with these exact keys:
- intent: one of [transactional, informational, navigational, problem_aware]
- difficulty: one of [low, medium, high]
- estimated_monthly_volume: integer (your best estimate based on search behavior)
- target_page: one of [homepage, state_pages, blog_post, faq]
- priority: integer 1-10
- rationale: string explaining your reasoning (max 200 chars)

Output raw JSON only. No markdown fences."""

        try:
            ai_raw = moonshot.run(
                system_prompt="You are an expert SEO keyword analyst.",
                user_prompt=prompt,
                temperature=0.3,
                max_tokens=512,
            )
            ai_raw = ai_raw.strip().strip("`").strip("json").strip("`").strip()
            ai_analysis = json.loads(ai_raw)
        except Exception as e:
            ai_analysis = {
                "intent": "transactional",
                "difficulty": "medium",
                "estimated_monthly_volume": 0,
                "target_page": "homepage",
                "priority": 5,
                "rationale": f"AI parse error: {e}",
            }

        portfolio.append({
            "keyword": seed,
            "intent": ai_analysis.get("intent", "transactional"),
            "difficulty": ai_analysis.get("difficulty", "medium"),
            "monthly_volume": ai_analysis.get("estimated_monthly_volume", 0),
            "target_page": ai_analysis.get("target_page", "homepage"),
            "priority": ai_analysis.get("priority", 5),
            "rationale": ai_analysis.get("rationale", ""),
            "long_tail_variants": variants[:15],
            "semantic_expansions": related[:10],
        })

    return {
        "tier": 1,
        "agent": "depositback-agent-keyword-tier1",
        "generated_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "total_keywords": len(portfolio),
        "keywords": portfolio,
    }
