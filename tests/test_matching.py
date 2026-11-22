import pymupdf
import pytest

from core.catalog import build_catalog
from core.discovery import TemplateError, discover
from core.matcher import auto_match, mappable_coverage
from scripts.template_specs import TEMPLATES


@pytest.mark.parametrize("spec", TEMPLATES, ids=lambda s: s["client_id"])
def test_automatch_coverage_without_llm(spec):
    """AC-2: at least 90% of mappable fields matched with tiers 1-3 only."""
    props = auto_match(discover(spec["file"]), build_catalog(spec["client_id"]), use_llm=False)
    got, total = mappable_coverage(props)
    assert got / total >= 0.90
    assert all(p.method in ("exact", "synonym", "fuzzy", "rule", "-") for p in props)


@pytest.mark.parametrize("spec", TEMPLATES, ids=lambda s: s["client_id"])
def test_every_template_has_required_field_mix(spec):
    fields = discover(spec["file"])
    types = [f.type for f in fields]
    assert types.count("checkbox") >= 2 and "radio" in types and "dropdown" in types
    props = auto_match(fields, build_catalog(spec["client_id"]))
    assert any(p.manual for p in props)


def test_master_data_prefers_db_and_document_facts_prefer_json():
    spec = TEMPLATES[0]
    props = {p.field.name: p for p in auto_match(discover(spec["file"]), build_catalog("C001"))}
    assert props["Applicant_Legal_Name"].sources[0].startswith("db.client.")
    assert props["Primary_Contact_Phone"].sources[0].startswith("db.client_contact[role=Primary]")
    assert props["Gross_Written_Premium"].sources[0].startswith("json.")


def test_same_concept_matches_across_naming_styles():
    names = {"C001": "Applicant_Legal_Name", "C002": "Insured Name", "C003": "Name of Agency",
             "C004": "EntityName", "C005": "Company", "C006": "applicant.legal_name", "C007": "CEDENT_NAME",
             "C008": "manager-legal-name", "C009": "Legal Name:", "C010": "legalEntityName",
             "C011": "txtCompanyName", "C012": "S1_LegalName"}
    for spec in TEMPLATES:
        props = {p.field.name: p for p in auto_match(discover(spec["file"]), build_catalog(spec["client_id"]))}
        assert props[names[spec["client_id"]]].concept == "legal_name"


def test_discovery_rejects_pdf_without_fields(tmp_path):
    p = tmp_path / "flat.pdf"
    doc = pymupdf.open()
    doc.new_page().insert_text((72, 72), "A flat page with no form fields")
    doc.save(p)
    with pytest.raises(TemplateError):
        discover(p)


def test_discovery_reads_radio_and_dropdown_options():
    fields = {f.name: f for f in discover(TEMPLATES[0]["file"])}
    assert fields["Binding_Authority"].options == ["Full", "Limited", "Referral Only"]
    assert "Limited Liability Company" in fields["Entity_Type"].options
    assert fields["Mailing_State"].max_length == 2
