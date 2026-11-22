"""Web form (.html) templates: <input>, <select>, <textarea>, checkboxes and radio groups."""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup, Tag

from core.discovery import TemplateError
from core.models import DiscoveredField, ResolvedField

SKIP_TYPES = {"hidden", "submit", "button", "reset", "image", "file", "password"}


def _soup(path: str | Path) -> BeautifulSoup:
    try:
        return BeautifulSoup(Path(path).read_text(encoding="utf-8", errors="replace"), "html.parser")
    except Exception as exc:
        raise TemplateError("This file could not be read as a web form (.html).") from exc


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip().rstrip(":*").strip()


def _label(soup: BeautifulSoup, el: Tag) -> str:
    el_id = el.get("id")
    if el_id:
        lab = soup.find("label", attrs={"for": el_id})
        if lab:
            return _clean(lab.get_text(" "))
    parent = el.find_parent("label")
    if parent:
        return _clean(parent.get_text(" "))
    for attr in ("aria-label", "data-label", "placeholder", "title"):
        if el.get(attr):
            return _clean(el[attr])
    return _clean(el.get("name") or el_id or "")


def _group_label(soup: BeautifulSoup, el: Tag) -> str:
    fs = el.find_parent("fieldset")
    if fs and fs.find("legend"):
        return _clean(fs.find("legend").get_text(" "))
    return _clean(el.get("data-label") or el.get("aria-label") or el.get("name") or "")


def _fields(soup: BeautifulSoup) -> list[tuple[DiscoveredField, list[Tag]]]:
    out: dict[str, tuple[DiscoveredField, list[Tag]]] = {}
    for el in soup.find_all(["input", "select", "textarea"]):
        kind = (el.get("type") or "text").lower() if el.name == "input" else el.name
        if kind in SKIP_TYPES:
            continue
        name = el.get("name") or el.get("id")
        if not name:
            continue
        if kind == "radio":
            opt = el.get("value") or _label(soup, el)
            if name in out:
                out[name][0].options.append(opt)
                out[name][1].append(el)
            else:
                out[name] = (DiscoveredField(name=name, label=_group_label(soup, el), type="radio",
                                             options=[opt]), [el])
            continue
        if name in out:
            continue
        if kind == "checkbox":
            f = DiscoveredField(name=name, label=_label(soup, el), type="checkbox")
        elif kind == "select":
            opts = [_clean(o.get_text(" ")) for o in el.find_all("option") if _clean(o.get_text(" "))]
            f = DiscoveredField(name=name, label=_label(soup, el), type="dropdown", options=opts)
        else:
            maxlen = el.get("maxlength")
            label = _label(soup, el)
            if kind == "date" and "date" not in label.lower():
                label += " date"
            f = DiscoveredField(name=name, label=label, type="text",
                                max_length=int(maxlen) if maxlen and str(maxlen).isdigit() else None)
        out[name] = (f, [el])
    return list(out.values())


def discover(path: str | Path) -> list[DiscoveredField]:
    fields = [f for f, _ in _fields(_soup(path))]
    if not fields:
        raise TemplateError("No fillable fields found in this web form. Add form inputs such as "
                            "<input name=\"legal_name\"> with a <label>.")
    return fields


def _iso(value: str) -> str:
    try:
        return datetime.strptime(value, "%m/%d/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return value


def _apply(soup: BeautifulSoup, fields: list[ResolvedField], highlights: dict[str, str] | None = None) -> None:
    by_name = {f.name: f for f in fields}
    for f, els in _fields(soup):
        rf = by_name.get(f.name)
        value = None if rf is None else rf.value
        for el in els:
            kind = (el.get("type") or "text").lower() if el.name == "input" else el.name
            if kind == "checkbox":
                if value is True:
                    el["checked"] = "checked"
                else:
                    el.attrs.pop("checked", None)
            elif kind == "radio":
                opt = el.get("value") or _label(soup, el)
                if value is not None and opt == value:
                    el["checked"] = "checked"
                else:
                    el.attrs.pop("checked", None)
            elif kind == "select":
                for o in el.find_all("option"):
                    o.attrs.pop("selected", None)
                    if value is not None and _clean(o.get_text(" ")) == value:
                        o["selected"] = "selected"
            elif kind == "textarea":
                el.string = "" if value is None else str(value)
            else:
                text = "" if value is None else str(value)
                el["value"] = _iso(text) if kind == "date" else text
            if highlights and f.name in highlights:
                el["style"] = (el.get("style", "") + f";outline:2px solid {highlights[f.name]};"
                               "outline-offset:2px;").lstrip(";")


def fill(path: str | Path, fields: list[ResolvedField], out_path: str | Path, flatten: bool = False) -> Path:
    soup = _soup(path)
    _apply(soup, fields)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(str(soup), encoding="utf-8")
    return out


def preview_html(path: str | Path, highlights: dict[str, str] | None = None) -> str:
    """Page markup for on-screen preview: scripts removed, optional status outlines added."""
    soup = _soup(path)
    for s in soup.find_all("script"):
        s.decompose()
    if highlights:
        for f, els in _fields(soup):
            for el in els:
                if f.name in highlights:
                    el["style"] = (el.get("style", "") + f";outline:2px solid {highlights[f.name]};"
                                   "outline-offset:2px;").lstrip(";")
    return str(soup)


def read_back(path: str | Path) -> dict[str, object]:
    soup = _soup(path)
    out: dict[str, object] = {}
    for f, els in _fields(soup):
        el = els[0]
        kind = (el.get("type") or "text").lower() if el.name == "input" else el.name
        if f.type == "checkbox":
            out[f.name] = el.has_attr("checked")
        elif f.type == "radio":
            on = [e for e in els if e.has_attr("checked")]
            out[f.name] = (on[0].get("value") or _label(soup, on[0])) if on else None
        elif kind == "select":
            sel = el.find("option", selected=True)
            out[f.name] = _clean(sel.get_text(" ")) if sel else None
        elif kind == "textarea":
            out[f.name] = el.get_text() or None
        else:
            out[f.name] = el.get("value") or None
    return out
