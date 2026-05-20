# Keyword Tier 1 — Core Transactional

> **Agent**: `depositback-agent-keyword-tier1`  
> **Group**: Search (Group 0)  
> **Product**: DepositBack — Security Deposit Demand Letter Service

## Purpose

Discovers and validates core transactional keywords (demand letter, template, refund).

## Runtime

```bash
pip install -r requirements.txt
python runtime/main.py
```

## Secrets Required

- `MOONSHOT_API_KEY` — AI-powered keyword analysis and clustering
- `GITHUB_TOKEN` — Auto-provided for Actions

## Skills

| Skill | Description | Source |
|-------|-------------|--------|
| `noop` | Health check | Local |
| `moonshot` | Moonshot Kimi K2.6 AI client | Local |
| `google_suggest` | Google autocomplete scraper (no API key) | Local |
| `datamuse_expand` | Semantic keyword expansion via Datamuse (free) | Local |
| `keyword_discovery` | Orchestrates tier-specific keyword research | Local |

## Workflow

1. Poll `data/inbox/` for task manifests.
2. Resolve required skills via `skills/skill_resolver.py`.
3. Execute keyword discovery, validation, or monitoring workflow.
4. Write keyword artifacts (JSON) to `data/outbox/`.
5. Update `data/state.json` with status and artifact references.
