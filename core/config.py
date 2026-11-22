"""Paths and configuration loading."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config"
TEMPLATE_CFG_DIR = CONFIG_DIR / "templates"
DATA_DIR = ROOT / "data"
JSON_DIR = DATA_DIR / "extracted"
DB_PATH = DATA_DIR / "dd.sqlite"
OUTPUT_DIR = ROOT / "output"
REPORTS_DIR = ROOT / "reports"

load_dotenv(ROOT / ".env")


@lru_cache
def settings() -> dict:
    s = yaml.safe_load((CONFIG_DIR / "settings.yaml").read_text(encoding="utf-8"))
    env = os.getenv("LLM_ENABLED")
    if env is not None:
        s["llm"]["enabled"] = env.strip().lower() in {"1", "true", "yes", "on"}
    return s


@lru_cache
def glossary() -> dict:
    return yaml.safe_load((CONFIG_DIR / "synonyms.yaml").read_text(encoding="utf-8"))


def llm_available() -> bool:
    return bool(settings()["llm"]["enabled"] and os.getenv("ANTHROPIC_API_KEY"))


def current_user() -> str:
    return os.getenv("APP_USER", "analyst.demo")
