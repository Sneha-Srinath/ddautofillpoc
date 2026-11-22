"""Word (.docx) template adapter: placeholder discovery and filling."""
import docx
import pytest

from core.adapters import docx_adapter as D
from core.discovery import TemplateError
from core.models import ResolvedField


def _make(tmp_path, split=False):
    doc = docx.Document()
    p = doc.add_paragraph("Name: ")
    if split:                                        # Word often splits a placeholder across runs
        p.add_run("{{Legal ")
        p.add_run("Entity Name}}")
    else:
        p.add_run("{{Legal Entity Name}}")
    t = doc.add_table(rows=1, cols=2)
    t.cell(0, 0).text = "TPA"
    t.cell(0, 1).text = "{{Uses a Third Party Administrator?}}"
    doc.add_paragraph("{{Binding Authority: Full | Limited | Referral Only}}")
    doc.sections[0].header.paragraphs[0].text = "Ref {{FEIN}}"
    doc.add_paragraph("Signature: {{Authorized Signature}}")
    path = tmp_path / "t.docx"
    doc.save(path)
    return path


def _rf(name, value, typ="text"):
    return ResolvedField(name=name, label=name, type=typ, value=value, status="Filled")


@pytest.mark.parametrize("split", [False, True])
def test_discovers_every_placeholder_and_type(tmp_path, split):
    fields = {f.name: f for f in D.discover(_make(tmp_path, split))}
    assert fields["Legal Entity Name"].type == "text"
    assert fields["Uses a Third Party Administrator?"].type == "checkbox"
    assert fields["Uses a Third Party Administrator?"].label == "Uses a Third Party Administrator"
    choice = fields["Binding Authority: Full | Limited | Referral Only"]
    assert choice.type == "radio" and choice.label == "Binding Authority"
    assert choice.options == ["Full", "Limited", "Referral Only"]
    assert "FEIN" in fields                          # found in the page header


@pytest.mark.parametrize("split", [False, True])
def test_fill_replaces_all_placeholders(tmp_path, split):
    path = _make(tmp_path, split)
    out = D.fill(path, [_rf("Legal Entity Name", "Harbor Point Insurance Group, LLC"),
                        _rf("Uses a Third Party Administrator?", True, "checkbox"),
                        _rf("Binding Authority: Full | Limited | Referral Only", "Limited", "radio"),
                        _rf("FEIN", "00-0000001"),
                        _rf("Authorized Signature", None)], tmp_path / "out.docx")
    text = D.text_of(out)
    assert "{{" not in text
    assert "Name: Harbor Point Insurance Group, LLC" in text
    assert "☒ Yes   ☐ No" in text
    assert "☐ Full   ☒ Limited   ☐ Referral Only" in text
    assert "Ref 00-0000001" in text
    assert "Signature: __________" in text


def test_blank_yes_no_is_not_guessed(tmp_path):
    out = D.fill(_make(tmp_path), [_rf("Uses a Third Party Administrator?", None, "checkbox")], tmp_path / "o.docx")
    assert "☐ Yes   ☐ No" in D.text_of(out)


def test_document_without_placeholders_is_refused(tmp_path):
    doc = docx.Document()
    doc.add_paragraph("No fields here")
    doc.save(tmp_path / "plain.docx")
    with pytest.raises(TemplateError, match="placeholder"):
        D.discover(tmp_path / "plain.docx")
