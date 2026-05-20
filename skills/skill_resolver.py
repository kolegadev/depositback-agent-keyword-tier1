"""Skill resolver with ClawHub fallback."""
import os
import sys
import importlib.util
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parent
CLAWHUB = os.getenv("CLAWHUB_REGISTRY", "https://clawhub.ai")

SKILL_REGISTRY = {
    "noop": ("noop", "execute"),
    "moonshot": ("moonshot", "run"),
    "google_suggest": ("google_suggest", "run"),
    "datamuse_expand": ("datamuse_expand", "run"),
    "keyword_discovery": ("keyword_discovery", "run"),
    "state_expander": ("state_expander", "run"),
    "multi_source_suggest": ("multi_source_suggest", "run"),
    "google_trends": ("google_trends", "run"),
    "people_also_ask": ("people_also_ask", "run"),
    "related_searches": ("related_searches", "run"),
    "route_outputs": ("route_outputs", "run"),
}


def resolve_skill(skill_id: str):
    if skill_id not in SKILL_REGISTRY:
        file_path = SKILLS_DIR / f"{skill_id.replace('-', '_')}.py"
        if file_path.exists():
            mod_name = skill_id.replace("-", "_")
            spec = importlib.util.spec_from_file_location(mod_name, file_path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = mod
            spec.loader.exec_module(mod)
            if hasattr(mod, "run"):
                return mod.run
        print(f"  [resolver] Unknown skill: {skill_id}")
        return None

    mod_name, func_name = SKILL_REGISTRY[skill_id]
    sys.path.insert(0, str(SKILLS_DIR))
    mod = __import__(mod_name)
    return getattr(mod, func_name)


def execute_skill(fn, params: dict):
    return fn(**params)
