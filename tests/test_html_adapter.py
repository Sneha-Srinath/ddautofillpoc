"""Web form (.html) template adapter."""
import pytest

from core.adapters import html_adapter as H
from core.discovery import TemplateError
from core.models import ResolvedField

FORM = """<html><body><form>
<label for="n">Legal Entity Name *</label><input id="n" name="legal_name" maxlength="80">
<label for="d">Date Established</label><input type="date" id="d" name="est">
<label for="s">Entity Type</label><select id="s" name="etype"><option></option><option>Corporation</option>
<option>Limited Liability Company</option></select>
<fieldset><legend>Binding Authority</legend>
<label><input type="radio" name="auth" value="Full"> Full</label>
<label><input type="radio" name="auth" value="Limited"> Limited</label></fieldset>
<label><input type="checkbox" name="tpa"> Uses a Third Party Administrator (TPA)</label>
<label for="l">Lines of Business</label><textarea id="l" name="lines"></textarea>
<input type="hidden" name="token" value="x"><button type="submit">Send</button>
<script>alert(1)</script>
</form></body></html>"""


@pytest.fixture
def form(tmp_path):
    p = tmp_path / "f.html"
    p.write_text(FORM, encoding="utf-8")
    return p


def _rf(name, value, typ="text"):
    return ResolvedField(name=name, label=name, type=typ, value=value, status="Filled")


def test_discovers_inputs_with_labels(form):
    f = {x.name: x for x in H.discover(form)}
    assert set(f) == {"legal_name", "est", "etype", "auth", "tpa", "lines"}     # hidden/button skipped
    assert f["legal_name"].label == "Legal Entity Name" and f["legal_name"].max_length == 80
    assert f["est"].label == "Date Established"
    assert f["etype"].type == "dropdown" and f["etype"].options == ["Corporation", "Limited Liability Company"]
    assert f["auth"].type == "radio" and f["auth"].label == "Binding Authority" and f["auth"].options == ["Full", "Limited"]
    assert f["tpa"].type == "checkbox" and f["tpa"].label == "Uses a Third Party Administrator (TPA)"


def test_fill_and_read_back(form, tmp_path):
    out = H.fill(form, [_rf("legal_name", "Harbor Point"), _rf("est", "06/15/2009"),
                        _rf("etype", "Limited Liability Company", "dropdown"), _rf("auth", "Limited", "radio"),
                        _rf("tpa", True, "checkbox"), _rf("lines", "Habitational, Contractors")], tmp_path / "o.html")
    rb = H.read_back(out)
    assert rb == {"legal_name": "Harbor Point", "est": "2009-06-15", "etype": "Limited Liability Company",
                  "auth": "Limited", "tpa": True, "lines": "Habitational, Contractors"}


def test_unchecked_and_blank(form, tmp_path):
    rb = H.read_back(H.fill(form, [_rf("tpa", False, "checkbox"), _rf("auth", None, "radio")], tmp_path / "o.html"))
    assert rb["tpa"] is False and rb["auth"] is None


def test_preview_strips_scripts_and_adds_outlines(form):
    page = H.preview_html(form, {"legal_name": "#1F6B45"})
    assert "<script" not in page and "outline:2px solid #1F6B45" in page


def test_page_without_inputs_is_refused(tmp_path):
    p = tmp_path / "plain.html"
    p.write_text("<html><body><p>Hello</p></body></html>")
    with pytest.raises(TemplateError, match="form inputs"):
        H.discover(p)
