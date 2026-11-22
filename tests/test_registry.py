"""Template registry: identifiers, upload validation, delete, data lookup."""
import pymupdf
import pytest

from core import engine, registry
from core.catalog import DataError
from scripts.template_specs import TEMPLATES

DEMO_PDF = (registry.ROOT / TEMPLATES[0]["file"]).read_bytes()


@pytest.fixture
def reg(tmp_path, monkeypatch):
    monkeypatch.setattr(registry, "CFG_DIR", tmp_path / "config")
    monkeypatch.setattr(registry, "PDF_DIR", tmp_path / "pdfs")
    monkeypatch.setattr(registry, "ROOT", tmp_path)
    return tmp_path


def test_register_stores_record_and_pdf(reg):
    cfg = registry.register("Test Co", "test01", DEMO_PDF)
    assert cfg.client_id == "TEST01" and cfg.template_id == "tpl-test01"
    assert cfg.field_count == 26 and cfg.name == "MGA Due Diligence Questionnaire"
    assert registry.template_file(cfg).exists()
    assert [t.client_id for t in registry.list_templates()] == ["TEST01"]


@pytest.mark.parametrize("bad", ["TEST-01", "a", "has space", "x" * 21, "", "C@1"])
def test_identifier_must_be_alphanumeric(reg, bad):
    with pytest.raises(registry.RegistryError):
        registry.register("Test Co", bad, DEMO_PDF)
    assert registry.list_templates() == []


def test_identifier_is_unique_case_insensitively(reg):
    registry.register("Test Co", "TEST01", DEMO_PDF)
    with pytest.raises(registry.RegistryError, match="already used"):
        registry.register("Other Co", "test01", DEMO_PDF)


def test_company_name_and_pdf_required(reg):
    with pytest.raises(registry.RegistryError, match="company name"):
        registry.register("  ", "TEST01", DEMO_PDF)
    with pytest.raises(registry.RegistryError, match="Choose a file"):
        registry.register("Test Co", "TEST01", b"")


def test_pdf_without_form_fields_rejected_and_nothing_written(reg):
    doc = pymupdf.open()
    doc.new_page().insert_text((72, 72), "flat page")
    with pytest.raises(registry.RegistryError, match="form fields"):
        registry.register("Flat Co", "FLAT01", doc.tobytes())
    assert registry.list_templates() == []
    assert not list((reg / "pdfs").glob("*.pdf"))


def test_delete_removes_pdf_and_record_only(reg):
    cfg = registry.register("Harbor copy", "C001", DEMO_PDF)
    path = registry.template_file(cfg)
    registry.delete(cfg.template_id)
    assert not path.exists() and registry.list_templates() == []
    assert registry.has_data("C001") == {"json": True, "db": True}      # company data untouched


def test_data_labels():
    assert registry.data_label("C001") == "JSON + DB"
    assert registry.data_label("NODATA1") == "No data found"


def test_fill_without_data_explains(reg):
    cfg = registry.register("New Co", "NEW01", DEMO_PDF)
    with pytest.raises(DataError, match="No data found for identifier NEW01"):
        engine.fill(cfg.template_id, log=False)


def test_new_upload_for_existing_identifier_fills_from_its_data(reg):
    cfg = registry.register("Harbor Point (re-upload)", "c001", DEMO_PDF)
    res = engine.fill(cfg.template_id, log=False)
    assert res.counts()["Filled"] == 24


# ------------------------------------------------------------------ one template per format per company
DOCX_PDF = (registry.ROOT / "templates" / "C001_Program_Administrator_Annual_Review.docx")
HTML_FORM = (registry.ROOT / "templates" / "C001_Online_MGA_Onboarding_Form.html")


def test_company_can_hold_pdf_word_and_web_form(reg):
    a = registry.register("Test Co", "TEST01", DEMO_PDF, file_name="a.pdf")
    b = registry.register("Test Co", "TEST01", DOCX_PDF.read_bytes(), file_name="b.docx")
    c = registry.register("Test Co", "TEST01", HTML_FORM.read_bytes(), file_name="c.html")
    assert [t.format for t in registry.list_templates()] == ["pdf", "docx", "html"]
    assert (a.template_id, b.template_id, c.template_id) == ("tpl-test01", "tpl-test01-docx", "tpl-test01-html")
    assert registry.formats_for("test01") == ["pdf", "docx", "html"]
    assert registry.companies() == {"TEST01": "Test Co"}


def test_second_template_of_same_type_refused(reg):
    registry.register("Test Co", "TEST01", DOCX_PDF.read_bytes(), file_name="b.docx")
    with pytest.raises(registry.RegistryError, match="already has a Word template"):
        registry.register("Test Co", "TEST01", DOCX_PDF.read_bytes(), file_name="again.docx")


def test_identifier_cannot_switch_company(reg):
    registry.register("Test Co", "TEST01", DEMO_PDF, file_name="a.pdf")
    with pytest.raises(registry.RegistryError, match="already used by Test Co"):
        registry.register("Other Co", "TEST01", DOCX_PDF.read_bytes(), file_name="b.docx")


def test_unsupported_file_type_refused(reg):
    with pytest.raises(registry.RegistryError, match="PDF, Word"):
        registry.register("Test Co", "TEST01", b"hello", file_name="notes.txt")
    assert registry.list_templates() == []


def test_delete_removes_only_that_format(reg):
    registry.register("Test Co", "TEST01", DEMO_PDF, file_name="a.pdf")
    registry.register("Test Co", "TEST01", HTML_FORM.read_bytes(), file_name="c.html")
    registry.delete("tpl-test01-html")
    assert registry.formats_for("TEST01") == ["pdf"]
