# Keyword Tier 1 — Core Transactional

> **Agent**: `depositback-agent-keyword-tier1`  
> **Group**: Search (Group 0)  
> **Focus**: Core transactional keywords with immediate purchase intent

## Purpose

Discovers, validates, and monitors the 10–50 core transactional keywords that drive direct conversions to the DepositBack demand letter product. These keywords represent users who are ready to generate a demand letter or template immediately.

## Target Keywords (Immediate)

| Priority | Keyword | Est. Monthly Volume | Intent | Target Page |
|----------|---------|---------------------|--------|-------------|
| 1 | security deposit demand letter | 9,900 | Transactional | Homepage |
| 2 | security deposit demand letter template | 6,600 | Transactional | Homepage + State pages |
| 3 | how to get security deposit back | 27,100 | Info → Transactional | Blog post #1 |
| 4 | landlord won't return security deposit | 5,400 | Transactional | Homepage CTA section |
| 5 | security deposit return letter | 3,600 | Transactional | State pages |
| 6 | demand letter for security deposit | 2,900 | Transactional | State pages |
| 7 | security deposit letter to landlord | 2,400 | Transactional | Homepage |
| 8 | letter to landlord about security deposit | 1,900 | Transactional | State pages |
| 9 | how to write security deposit letter | 1,600 | Info → Transactional | Blog post #6 |
| 10 | security deposit refund letter | 1,300 | Transactional | State pages |

## Skills Used

- `google_suggest` — Scrape autocomplete suggestions for each seed keyword to discover long-tail variants
- `datamuse_expand` — Find semantically related terms and synonyms
- `moonshot` — Classify intent (informational vs transactional), estimate difficulty, assign target pages
- `keyword_discovery` — Orchestrate the full pipeline and output structured JSON

## Output Format

```json
{
  "tier": 1,
  "agent": "depositback-agent-keyword-tier1",
  "generated_at": "2026-05-20T00:00:00Z",
  "keywords": [
    {
      "keyword": "security deposit demand letter",
      "monthly_volume": 9900,
      "intent": "transactional",
      "difficulty": "medium",
      "target_page": "homepage",
      "long_tail_variants": ["..."],
      "priority": 1
    }
  ]
}
```

## Human Escalation Points

- Legal keyword accuracy verification
- Trademark conflicts in keyword targets
- First 50 keyword validations need human QA
