"""US value conversion rules (requirements 5.4). Never guess: unclear -> not ok or flagged."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

import dateparser
from rapidfuzz import fuzz

from core.config import glossary, settings
from core.textnorm import normalize

US_STATES = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA",
    "colorado": "CO", "connecticut": "CT", "delaware": "DE", "district of columbia": "DC",
    "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID", "illinois": "IL",
    "indiana": "IN", "iowa": "IA", "kansas": "KS", "kentucky": "KY", "louisiana": "LA",
    "maine": "ME", "maryland": "MD", "massachusetts": "MA", "michigan": "MI", "minnesota": "MN",
    "mississippi": "MS", "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY",
    "north carolina": "NC", "north dakota": "ND", "ohio": "OH", "oklahoma": "OK", "oregon": "OR",
    "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC", "south dakota": "SD",
    "tennessee": "TN", "texas": "TX", "utah": "UT", "vermont": "VT", "virginia": "VA",
    "washington": "WA", "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY",
}
STATE_CODES = set(US_STATES.values())

YES = {"yes", "y", "true", "1", "checked", "x", "on", "in force", "in place"}
NO = {"no", "n", "false", "0", "unchecked", "off", "none", "not applicable"}
APPROX = re.compile(r"\b(approx(imately)?|about|around|circa|est(imated)?|roughly)\b|~", re.I)
MULT = {"k": 1e3, "thousand": 1e3, "m": 1e6, "mm": 1e6, "mn": 1e6, "million": 1e6,
        "b": 1e9, "bn": 1e9, "billion": 1e9}


@dataclass
class Conv:
    value: Any = None          # typed value written to the PDF (str / bool)
    display: str = ""
    ok: bool = False           # False -> nothing usable (blank)
    flags: list[str] = field(default_factory=list)


def is_blank(raw: Any) -> bool:
    return raw is None or (isinstance(raw, str) and not raw.strip())


# ---------------------------------------------------------------- scalars
def to_text(raw: Any, max_length: int | None = None) -> Conv:
    s = re.sub(r"\s+", " ", str(raw)).strip()
    if max_length and len(s) > max_length:
        return Conv(s[:max_length], s[:max_length], True, [f"truncated to {max_length} characters"])
    return Conv(s, s, True)


def parse_amount(raw: Any) -> tuple[Decimal | None, list[str]]:
    flags: list[str] = []
    if isinstance(raw, (int, float, Decimal)) and not isinstance(raw, bool):
        return Decimal(str(raw)), flags
    s = str(raw)
    if APPROX.search(s):
        flags.append(f'approximate value "{s}"')
        s = APPROX.sub(" ", s)
    s = s.lower().replace("usd", " ").replace("$", " ").replace(",", "")
    m = re.search(r"(-?\d+(?:\.\d+)?)\s*(thousand|million|billion|mm|mn|bn|k|m|b)?\b", s)
    if not m:
        return None, flags
    try:
        num = Decimal(m.group(1))
    except InvalidOperation:
        return None, flags
    if m.group(2):
        num *= Decimal(str(MULT[m.group(2)]))
    rest = (s[: m.start()] + s[m.end():]).strip(" .")
    if re.search(r"[a-z]{3,}", rest):
        flags.append(f'value has extra text: "{str(raw).strip()}"')
    return num, flags


def to_currency(raw: Any) -> Conv:
    num, flags = parse_amount(raw)
    if num is None:
        return Conv(flags=[f'not a currency amount: "{raw}"'])
    d = f"${num:,.2f}"
    return Conv(d, d, True, flags)


def to_number(raw: Any) -> Conv:
    num, flags = parse_amount(raw)
    if num is None:
        return Conv(flags=[f'not a number: "{raw}"'])
    d = f"{int(num):,}" if num == num.to_integral_value() else f"{num:,}"
    return Conv(d, d, True, flags)


def to_percent(raw: Any) -> Conv:
    s = str(raw).replace("%", "")
    num, flags = parse_amount(s)
    if num is None:
        return Conv(flags=[f'not a percentage: "{raw}"'])
    d = f"{num:.1f}%"
    return Conv(d, d, True, flags)


def to_date(raw: Any) -> Conv:
    fmt = settings().get("date_output_format", "%m/%d/%Y")
    if isinstance(raw, (date, datetime)):
        return Conv(raw.strftime(fmt), raw.strftime(fmt), True)
    s = str(raw).strip()
    if re.fullmatch(r"\d{4}", s):
        return Conv(flags=[f'only a year was found: "{s}"'])
    m = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", s)
    if m:
        dt = date(int(m[1]), int(m[2]), int(m[3]))
        return Conv(dt.strftime(fmt), dt.strftime(fmt), True)
    m = re.fullmatch(r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})", s)
    flags = []
    if m:
        a, b = int(m[1]), int(m[2])
        if a <= 12 and b <= 12 and a != b:
            flags.append(f'ambiguous day/month in "{s}" (read as MM/DD)')
    dt = None
    for pattern in ("%m/%d/%Y", "%m-%d-%Y", "%m/%d/%y", "%B %d, %Y", "%b %d, %Y", "%d-%b-%Y",
                    "%d %B %Y", "%d %b %Y", "%B %d %Y"):
        try:
            dt = datetime.strptime(s, pattern)
            break
        except ValueError:
            continue
    if dt is None:
        dt = dateparser.parse(s, languages=["en"], settings={
            "DATE_ORDER": "MDY", "PREFER_DAY_OF_MONTH": "first", "REQUIRE_PARTS": ["year"]})
    if not dt:
        return Conv(flags=[f'not a date: "{s}"'])
    return Conv(dt.strftime(fmt), dt.strftime(fmt), True, flags)


def to_phone(raw: Any) -> Conv:
    s = str(raw).strip()
    digits = re.sub(r"\D", "", s)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) == 10:
        d = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        return Conv(d, d, True)
    return Conv(s, s, True, [f'non-US phone format kept as given: "{s}"'])


def to_email(raw: Any) -> Conv:
    s = str(raw).strip().lower()
    if re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", s):
        return Conv(s, s, True)
    return Conv(s, s, True, [f'invalid e-mail "{s}"'])


def to_state(raw: Any, max_length: int | None = None) -> Conv:
    s = str(raw).strip()
    if s.upper() in STATE_CODES:
        return Conv(s.upper(), s.upper(), True)
    code = US_STATES.get(normalize(s))
    if code:
        return Conv(code, code, True)
    if max_length and max_length <= 2:
        return Conv(flags=[f'not a US state: "{s}"'])
    return to_text(s, max_length)


def to_zip(raw: Any) -> Conv:
    s = str(raw).strip()
    if isinstance(raw, (int, float)):
        s = f"{int(raw):05d}"
    if re.fullmatch(r"\d{5}(-\d{4})?", s):
        return Conv(s, s, True)
    if re.fullmatch(r"\d{9}", s):
        return Conv(f"{s[:5]}-{s[5:]}", f"{s[:5]}-{s[5:]}", True)
    return Conv(s, s, True, [f'unusual ZIP code "{s}"'])


def to_yesno(raw: Any) -> Conv:
    if isinstance(raw, bool):
        return Conv(raw, "Yes" if raw else "No", True)
    s = normalize(str(raw))
    if s in YES:
        return Conv(True, "Yes", True)
    if s in NO:
        return Conv(False, "No", True)
    return Conv(flags=[f'not a clear yes/no: "{str(raw).strip()}" - left blank, not guessed'])


def to_option(raw: Any, options: list[str]) -> Conv:
    opts = [o for o in options if o.strip()]
    s = str(raw).strip()
    for o in opts:                       # exact, symbols included ("A-" is not "A++")
        if o.strip().casefold() == s.casefold():
            return Conv(o, o, True)
    n = normalize(s)
    norm_hits = [o for o in opts if normalize(o) == n]
    if len(norm_hits) == 1 and re.search(r"[a-z0-9]", n):
        return Conv(norm_hits[0], norm_hits[0], True)
    syn = {normalize(k): v for k, v in (glossary().get("option_synonyms") or {}).items()}
    if n in syn and syn[n] in opts:
        return Conv(syn[n], syn[n], True)
    if opts and all(o.upper() in STATE_CODES for o in opts):
        st = to_state(s, 2)
        if st.ok and st.value in opts:
            return Conv(st.value, st.value, True)
    best, score = None, 0.0
    for o in opts:
        sc = fuzz.token_sort_ratio(n, normalize(o))
        if sc > score:
            best, score = o, sc
    if best and score >= settings()["fuzzy_threshold"]:
        return Conv(best, best, True, [f'fuzzy option match "{s}" -> "{best}" ({score:.0f})'])
    return Conv(flags=[f'"{s}" does not match any option ({", ".join(opts)})'])


# ---------------------------------------------------------------- dispatch
def convert(raw: Any, ftype: str, fmt: str = "text", options: list[str] | None = None,
            max_length: int | None = None) -> Conv:
    if is_blank(raw):
        return Conv()
    if ftype == "checkbox":
        return to_yesno(raw)
    if ftype in ("radio", "dropdown"):
        return to_option(raw, options or [])
    fn = {
        "currency": lambda r: to_currency(r),
        "number": lambda r: to_number(r),
        "percent": lambda r: to_percent(r),
        "date": lambda r: to_date(r),
        "phone": lambda r: to_phone(r),
        "email": lambda r: to_email(r),
        "state": lambda r: to_state(r, max_length),
        "zip": lambda r: to_zip(r),
        "yesno": lambda r: to_yesno(r),
    }.get(fmt)
    out = fn(raw) if fn else to_text(raw, max_length)
    if out.ok and isinstance(out.value, str) and max_length and len(out.value) > max_length:
        out.flags.append(f"truncated to {max_length} characters")
        out.value = out.display = out.value[:max_length]
    if fmt == "yesno" and out.ok:      # yes/no concept on a text field
        out.value = out.display
    return out
