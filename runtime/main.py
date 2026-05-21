"""Runtime for tier1 with automatic downstream routing via CROSS_REPO_PAT."""
import json
import shutil
import sys
import importlib.util
from datetime import datetime, timezone
from pathlib import Path

AGENT_NAME = "tier1"
AGENT_ID = "26"
BASE_DIR = Path(__file__).resolve().parent.parent
INBOX = BASE_DIR / "data" / "inbox"
OUTBOX = BASE_DIR / "data" / "outbox"
ARCHIVE = BASE_DIR / "data" / "archive"
SKILLS_DIR = BASE_DIR / "skills"
STATE_FILE = BASE_DIR / "data" / "state.json"

sys.path.insert(0, str(SKILLS_DIR))


def load_manifest(path: Path):
    with open(path, "r") as f:
        return json.load(f)


def save_state(status: str, meta=None):
    payload = {
        "agent": AGENT_NAME,
        "agent_id": AGENT_ID,
        "status": status,
        "updated": datetime.now(timezone.utc).isoformat(),
        "meta": meta or {},
    }
    with open(STATE_FILE, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"   💾 state.json → {status}")


def write_artifact(kind: str, data: dict):
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    name = f"{ts}_{kind}.json"
    path = OUTBOX / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"   📝 Artifact: {path}")
    return str(path)


def process_manifest(path: Path):
    manifest = load_manifest(path)
    print(f"   📄 Manifest: {manifest.get('request_id', 'unknown')}")

    steps = manifest.get("workflow", {}).get("steps", [])
    if not steps:
        print("   ⚠️  No steps found")
        save_state("idle")
        return

    results = []
    for step in steps:
        skill_id = step.get("skill")
        params = step.get("params", {})
        print(f"   🔧 Skill: {skill_id}")

        resolver = importlib.import_module("skill_resolver")
        fn = resolver.resolve_skill(skill_id)
        if fn is None:
            raise RuntimeError(f"Skill '{skill_id}' not resolved")

        result = resolver.execute_skill(fn, params)
        results.append({"step_id": step.get("id"), "skill": skill_id, "result": result})
        print(f"   ✅ Result: {str(result)[:200]}")

    artifact = {
        "agent": AGENT_NAME,
        "agent_id": AGENT_ID,
        "manifest": manifest,
        "results": results,
    }
    artifact_path = write_artifact("output", artifact)

    # ── Downstream routing ───────────────────────────────────────────────
    try:
        resolver = importlib.import_module("skill_resolver")
        route_fn = resolver.resolve_skill("route_outputs")
        if route_fn:
            print("   📤 Routing to downstream agents...")
            route_result = resolver.execute_skill(route_fn, artifact_path, 1, AGENT_NAME)
            print(f"   ✅ Routed: {route_result}")
        else:
            print("   ℹ️  route_outputs skill not available")
    except Exception as e:
        print(f"   ⚠️  Routing failed: {e}")

    ARCHIVE.mkdir(parents=True, exist_ok=True)
    shutil.move(str(path), str(ARCHIVE / path.name))
    print(f"   🗄️  Archived: {ARCHIVE / path.name}")

    save_state("idle", {"last_artifact": artifact_path})
    return artifact


def run():
    print(f"🚀 {AGENT_NAME} ({AGENT_ID}) — {datetime.now(timezone.utc).isoformat()}")
    for d in [INBOX, OUTBOX, ARCHIVE]:
        d.mkdir(parents=True, exist_ok=True)

    manifests = sorted(INBOX.glob("*.json"))
    if not manifests:
        print("   ℹ️  No manifests in inbox")
        save_state("idle")
        return

    manifest = manifests[-1]
    print(f"   Found {len(manifests)} manifest(s); processing latest: {manifest.name}")
    try:
        process_manifest(manifest)
    except Exception as e:
        print(f"   ❌ Fatal error: {e}")
        save_state(f"error: {str(e)[:80]}")
        raise

    print("   ✅ One-shot complete")


if __name__ == "__main__":
    run()
