"""Optional semantic matching tier (FR-10 tier 4), Anthropic Claude.

Only field names/labels and data PATH NAMES are sent - never client values or documents (NFR-7).
Used at template setup only, never at fill time (FR-15). Off by default (NFR-8).
"""
from __future__ import annotations

import json
import logging

from core.config import llm_available, settings

log = logging.getLogger(__name__)

SYSTEM = (
    "You map fields on US commercial insurance due diligence forms to data paths. "
    "For each form field choose the single best path from the provided list, or null when no "
    "path clearly means the same thing. Never invent paths. Prefer null over a weak guess."
)

SCHEMA = {
    "type": "object",
    "properties": {
        "matches": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "field": {"type": "string"},
                    "path": {"type": ["string", "null"]},
                    "confidence": {"type": "number"},
                },
                "required": ["field", "path", "confidence"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["matches"],
    "additionalProperties": False,
}


def semantic_match(fields: list[dict], paths: list[str]) -> dict[str, tuple[str, float]]:
    """fields: [{name, label, type}] -> {field_name: (path, confidence)}; {} when unavailable."""
    if not fields or not llm_available():
        return {}
    try:
        import anthropic
    except ImportError:
        return {}
    cfg = settings()["llm"]
    prompt = (
        "Form fields:\n" + json.dumps(fields, indent=1) +
        "\n\nAvailable data paths (json.* = extracted from documents, db.* = database):\n" +
        "\n".join(paths)
    )
    try:
        client = anthropic.Anthropic()
        resp = client.beta.messages.create(
            model=cfg.get("model", "claude-opus-5-5"),
            max_tokens=cfg.get("max_tokens", 4000),
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            system=SYSTEM,
            output_config={"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}},
            messages=[{"role": "user", "content": prompt}],
        )
        if resp.stop_reason == "refusal":
            return {}
        text = next((b.text for b in resp.content if b.type == "text"), "{}")
        data = json.loads(text)
    except Exception as exc:  # LLM tier is best-effort; tiers 1-3 still work (FR-14)
        log.warning("semantic matching unavailable: %s", exc)
        return {}
    valid = set(paths)
    return {m["field"]: (m["path"], float(m.get("confidence", 0.7)))
            for m in data.get("matches", []) if m.get("path") in valid}
