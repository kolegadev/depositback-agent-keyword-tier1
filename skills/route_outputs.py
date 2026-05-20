"""Route Outputs skill — pushes keyword artifacts to Content Production agent inboxes."""
import os
import json
import base64
import requests
from datetime import datetime, timezone

OWNER = "kolegadev"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

CONTENT_AGENTS = {
    "geo_content_generator": "depositback-agent-geo-content-generator",
    "social_content_creator": "depositback-agent-social-content-creator",
    "landing_page_optimizer": "depositback-agent-landing-page-optimizer",
    "email_copywriter": "depositback-agent-email-copywriter",
}


def _put_file(repo: str, path: str, content: str, message: str):
    if not GITHUB_TOKEN:
        return {"error": "GITHUB_TOKEN not set"}
    url = f"https://api.github.com/repos/{OWNER}/{repo}/contents/{path}"
    b64 = base64.b64encode(content.encode()).decode()
    payload = {"message": message, "content": b64}
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    r = requests.put(url, headers=headers, json=payload)
    if r.status_code == 422:
        get_r = requests.get(url, headers={"Authorization": f"Bearer {GITHUB_TOKEN}"})
        if get_r.status_code == 200:
            sha = get_r.json().get("sha")
            payload["sha"] = sha
            r = requests.put(url, headers=headers, json=payload)
    return {"status": r.status_code, "repo": repo, "path": path}


def run(artifact_path: str, tier: int, agent_name: str):
    if not os.path.exists(artifact_path):
        return {"error": f"Artifact not found: {artifact_path}"}

    with open(artifact_path, "r") as f:
        artifact = json.load(f)

    # The artifact is wrapped by runtime/main.py. The actual skill result is inside results[].result
    keywords = []
    raw_result = None
    if "results" in artifact and artifact["results"]:
        raw_result = artifact["results"][0].get("result", {})
    else:
        raw_result = artifact

    # Flatten keywords from nested tier 3 structure or direct array
    if "keywords" in raw_result:
        keywords = raw_result["keywords"]
    elif "states" in raw_result:
        for state_data in raw_result["states"].values():
            keywords.extend(state_data.get("keywords", []))

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    routed = []

    # Route to geo-content-generator (all tiers with state pages)
    if tier in (1, 3):
        state_keywords = [k for k in keywords if k.get("target_page", "").startswith("/")]
        if state_keywords:
            brief = {
                "request_id": f"brief-{ts}-geo",
                "agent": agent_name,
                "tier": tier,
                "task": "generate_state_landing_pages",
                "keywords": state_keywords[:50],
                "instructions": "Generate state-specific landing page content for each keyword. Include H1, meta description, and FAQ schema.",
            }
            path = f"data/inbox/brief-{ts}-geo.json"
            res = _put_file(CONTENT_AGENTS["geo_content_generator"], path, json.dumps(brief, indent=2), f"📥 Keyword brief from {agent_name}")
            routed.append({"target": "geo_content_generator", "path": path, "result": res})

    # Route to landing-page-optimizer (homepage + transactional)
    if tier == 1:
        transactional = [k for k in keywords if k.get("target_page") == "homepage" or "transactional" in k.get("intent", "")]
        if transactional:
            brief = {
                "request_id": f"brief-{ts}-lpo",
                "agent": agent_name,
                "tier": tier,
                "task": "optimize_landing_pages",
                "keywords": transactional[:20],
                "instructions": "Generate A/B test briefs and copy variations for homepage and transactional landing pages.",
            }
            path = f"data/inbox/brief-{ts}-lpo.json"
            res = _put_file(CONTENT_AGENTS["landing_page_optimizer"], path, json.dumps(brief, indent=2), f"📥 Keyword brief from {agent_name}")
            routed.append({"target": "landing_page_optimizer", "path": path, "result": res})

    # Route to social-content-creator (problem-aware)
    if tier == 2:
        problem_keywords = [k for k in keywords if "problem" in k.get("intent", "") or "blog" in k.get("content_strategy", "")]
        if problem_keywords:
            brief = {
                "request_id": f"brief-{ts}-social",
                "agent": agent_name,
                "tier": tier,
                "task": "create_social_hooks",
                "keywords": problem_keywords[:20],
                "instructions": "Generate TikTok/Reel hooks and short-form scripts based on problem-aware keywords and emotional hooks.",
            }
            path = f"data/inbox/brief-{ts}-social.json"
            res = _put_file(CONTENT_AGENTS["social_content_creator"], path, json.dumps(brief, indent=2), f"📥 Keyword brief from {agent_name}")
            routed.append({"target": "social_content_creator", "path": path, "result": res})

    # Route to email-copywriter (all tiers)
    all_keywords = keywords[:30]
    if all_keywords:
        brief = {
            "request_id": f"brief-{ts}-email",
            "agent": agent_name,
            "tier": tier,
            "task": "draft_email_sequence",
            "keywords": all_keywords,
            "instructions": "Draft email subject lines and body copy targeting these keywords. Focus on security deposit recovery urgency.",
        }
        path = f"data/inbox/brief-{ts}-email.json"
        res = _put_file(CONTENT_AGENTS["email_copywriter"], path, json.dumps(brief, indent=2), f"📥 Keyword brief from {agent_name}")
        routed.append({"target": "email_copywriter", "path": path, "result": res})

    return {
        "agent": agent_name,
        "tier": tier,
        "total_keywords": len(keywords),
        "routed": routed,
    }
