"""Name normalization: Phone_Number = phone number = phoneNumber = 'Phone Number:'."""
from __future__ import annotations

import re

_CAMEL = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
# Form-builder control prefixes (only when followed by an upper-case letter, so "city" or "number" are safe)
_PREFIX = re.compile(r"^(txt|chk|ddl|rdo|cur|num|dt|cbo|lst|fld)(?=[A-Z])")
# Section or question codes at the start of a field name: S1_, Q12_, Sec3_
_SECTION = re.compile(r"^(?:[SQ]|Sec)\d+[A-Za-z]?_", re.IGNORECASE)


def normalize(text: str) -> str:
    if not text:
        return ""
    t = text.replace("#20", " ").strip()
    t = _PREFIX.sub("", t)          # txtCompanyName -> CompanyName, chkMFA -> MFA
    t = _SECTION.sub("", t)         # S1_LegalName -> LegalName, Q12_FEIN -> FEIN
    t = _CAMEL.sub(" ", t)
    t = t.lower()
    t = re.sub(r"\be\s*&\s*o\b", "eo", t)          # E&O -> eo
    t = re.sub(r"\be\s*-\s*mail\b", "e mail", t)
    t = t.replace("&", " and ").replace("%", " pct ")
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()
