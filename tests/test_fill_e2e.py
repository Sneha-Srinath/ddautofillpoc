"""End-to-end fills of all five demo templates against the scenario matrix (AC-3 .. AC-6)."""
import json
import time

import pytest

from core import engine, registry
from core.catalog import DataError, load_json, validate_json
from core.config import JSON_DIR
from core.filler import read_back


@pytest.fixture(scope="module")
def results():
    """Every registered template whose company has data (C013/C014 are onboarded before their data)."""
    return {t.client_id: engine.fill(t.template_id, log=False) for t in registry.list_templates()
            if t.format == "pdf" and registry.data_label(t.client_id) != "No data found"}


def by_name(res):
    return {f.name: f for f in res.fields}


def test_all_demo_templates_registered():
    ts = registry.list_templates()
    assert sorted(t.client_id for t in ts if t.format == "pdf") == [f"C{i:03d}" for i in range(1, 15)]
    assert sorted(t.template_id for t in ts if t.format != "pdf") == [
        "tpl-c001-docx", "tpl-c001-html", "tpl-c002-docx", "tpl-c002-html", "tpl-c013-docx"]
    assert all(t.company_name and t.field_count and registry.template_file(t).exists() for t in ts)


def test_clean_fill_c001(results):
    k = results["C001"].counts()
    assert k["Review"] == k["Missing"] == k["Unmapped"] == 0
    assert k["Manual"] == 2


def test_conflicts_and_approximation_c002(results):
    f = by_name(results["C002"])
    assert f["Telephone"].status == "Review" and f["Telephone"].value == "(601) 555-0142"   # DB wins
    assert f["Telephone"].source == "DB" and "Conflict" in f["Telephone"].note
    assert f["Direct Written Premium"].status == "Review" and f["Direct Written Premium"].source == "JSON"
    assert f["Policyholder Surplus"].status == "Review" and "approximate" in f["Policyholder Surplus"].note
    assert f["AM Best Rating"].value == "A-" and f["AM Best Rating"].status == "Review"
    assert f["Rating Outlook"].value == "Stable" and f["Rating Outlook"].status == "Filled"


def test_low_confidence_and_conversion_c003(results):
    f = by_name(results["C003"])
    assert f["E&O Limit per Claim"].status == "Review" and f["E&O Limit per Claim"].confidence == 0.64
    assert f["Date Agency Established"].value == "03/03/2014"
    assert f["State (Mailing)"].value == "TX"
    assert f["Principal Contact Phone"].value == "(214) 555-0142"
    assert f["Resident State"].value == "TX"


def test_single_source_and_ambiguous_date_c004(results):
    f = by_name(results["C004"])
    assert f["FEIN"].source == "DB" and f["FEIN"].status == "Filled"
    assert f["FinancialStrengthRating"].source == "JSON" and f["FinancialStrengthRating"].value == "A+"
    assert f["DateOfFormation"].status == "Review" and "ambiguous" in f["DateOfFormation"].note
    assert f["AnnualBrokerageRevenue"].value == "$12,400,000.00"
    assert f["PlacementType"].value == "Treaty and Facultative"
    # Matched only by name similarity at fill time -> filled but flagged for a person to confirm
    for name in ("YrsInBusiness", "KeyContactEmailAddr"):
        assert f[name].status == "Review" and f[name].value and "fuzzy" in f[name].note


def test_missing_and_not_guessed_c005(results):
    f = by_name(results["C005"])
    assert f["Pending Litigation"].status == "Review" and f["Pending Litigation"].value is None
    assert f["Top 10 Clients %"].status == "Missing"
    assert f["Non-Compete Agreements"].status == "Missing"
    assert results["C005"].counts()["Missing"] == 2


@pytest.mark.parametrize("cid", ["C001", "C002", "C003", "C004", "C005"])
def test_values_written_into_pdf(results, cid):
    """AC-4: text, checkbox, radio and dropdown values are in the output file."""
    res = results[cid]
    pdf = read_back(res.output_path)
    for f in res.fields:
        if f.type == "checkbox":
            assert pdf[f.name] is (f.value is True)
        elif f.value is None:
            assert pdf.get(f.name) in (None, "", " ")
        else:
            assert pdf[f.name] == str(f.value), f.name


def test_fill_under_three_seconds():
    engine.fill("tpl-c001", log=False)       # warm caches
    t0 = time.perf_counter()
    engine.fill("tpl-c005", log=False)
    assert time.perf_counter() - t0 < 3.0


def test_repeatable(results):
    again = engine.fill("tpl-c002", log=False)
    assert [(f.name, f.value, f.status) for f in again.fields] == \
           [(f.name, f.value, f.status) for f in results["C002"].fields]


def test_wrong_client_json_refused():
    """AC-6 / NFR-2: a JSON whose client_id differs from the template's client is refused."""
    doc = json.loads((JSON_DIR / "C002.json").read_text())
    with pytest.raises(DataError, match="belongs to client 'C002'"):
        validate_json(doc, "C001")


def test_json_without_client_id_refused(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text(json.dumps({"client_name": "x", "extracted_at": "now", "entity": {}}))
    with pytest.raises(DataError, match="contract"):
        load_json("C001", p)


def test_user_edit_marks_source_user():
    res = engine.fill("tpl-c003", overrides={"E&O Limit per Claim": "5000000"}, log=False)
    f = by_name(res)["E&O Limit per Claim"]
    assert f.source == "User" and f.value == "$5,000,000.00" and f.status == "Filled"
    assert read_back(res.output_path)["E&O Limit per Claim"] == "$5,000,000.00"


def test_flatten_removes_form_fields():
    res = engine.fill("tpl-c001", flatten=True, log=False)
    assert read_back(res.output_path) == {}


# ------------------------------------------------------------------ companies C006 to C012
EXPECTED = {   # client_id -> (Filled, Review, Missing, Unmapped, Manual)
    "C006": (20, 1, 0, 0, 1), "C007": (19, 1, 0, 0, 1), "C008": (20, 0, 1, 0, 1), "C009": (20, 2, 0, 0, 1),
    "C010": (19, 0, 0, 2, 1), "C011": (19, 1, 0, 0, 1), "C012": (21, 0, 0, 0, 1),
}


@pytest.mark.parametrize("cid", sorted(EXPECTED))
def test_new_company_status_counts(cid):
    res = engine.fill(f"tpl-{cid.lower()}", log=False)
    k = res.counts()
    assert (k["Filled"], k["Review"], k["Missing"], k["Unmapped"], k["Manual"]) == EXPECTED[cid]


def test_new_company_scenarios():
    c006 = by_name(engine.fill("tpl-c006", log=False))
    assert c006["program.gwp"].status == "Review" and "Conflict" in c006["program.gwp"].note
    assert c006["controls.telematics"].value is True
    c007 = by_name(engine.fill("tpl-c007", log=False))
    assert c007["POLICYHOLDER_SURPLUS"].source == "DB" and c007["POLICYHOLDER_SURPLUS"].value == "$184,000,000.00"
    assert c007["CAT_RETENTION"].confidence == 0.69
    c009 = by_name(engine.fill("tpl-c009", log=False))
    assert c009["Pending Litigation:"].value is None and c009["Pending Litigation:"].status == "Review"
    c010 = by_name(engine.fill("tpl-c010", log=False))
    assert all(f.source in ("DB", "-") for f in c010.values())
    assert c010["loansOutstanding"].value == "$361,000,000.00" and c010["defaultRate"].value == "1.6%"
    c012 = by_name(engine.fill("tpl-c012", log=False))
    assert c012["S4_ResidentState"].value == "WA" and c012["S4_SLLicenseNumber"].value == "MOCK-WA-SL-118204"


def test_data_labels_for_new_companies():
    assert registry.data_label("C010") == "DB only"
    assert registry.data_label("C012") == "JSON + DB"


# ------------------------------------------------------------------ onboarded before data (C013, C014)
@pytest.mark.parametrize("cid", ["C013", "C014"])
def test_template_without_data_says_no_data(cid):
    t = registry.for_client(cid)
    assert t is not None and registry.template_file(t).exists() and t.field_count > 0
    assert registry.data_label(cid) == "No data found"
    with pytest.raises(DataError, match=f"No data found for identifier {cid}"):
        engine.fill(t.template_id, log=False)


# ------------------------------------------------------------------ Word and web form templates
from core.adapters import docx_adapter, html_adapter  # noqa: E402

FORMAT_EXPECTED = {   # template_id -> (Filled, Review, Missing, Unmapped, Manual)
    "tpl-c001-docx": (22, 0, 0, 0, 2), "tpl-c002-docx": (16, 4, 0, 0, 1),
    "tpl-c001-html": (23, 0, 0, 0, 1), "tpl-c002-html": (14, 4, 0, 0, 1),
}


@pytest.mark.parametrize("tid", sorted(FORMAT_EXPECTED))
def test_word_and_web_form_status_counts(tid):
    k = engine.fill(tid, log=False).counts()
    assert (k["Filled"], k["Review"], k["Missing"], k["Unmapped"], k["Manual"]) == FORMAT_EXPECTED[tid]


def test_word_output_is_filled_and_clean():
    res = engine.fill("tpl-c001-docx", log=False)
    assert res.output_name.endswith(".docx")
    text = docx_adapter.text_of(res.output_path)
    assert "{{" not in text and "Harbor Point Insurance Group, LLC" in text and "☒ Full" in text


def test_web_form_output_values():
    res = engine.fill("tpl-c001-html", log=False)
    rb = html_adapter.read_back(res.output_path)
    assert rb["legal_entity_name"] == "Harbor Point Insurance Group, LLC"
    assert rb["established"] == "2009-06-15" and rb["binding_authority"] == "Full" and rb["uses_tpa"] is True


def test_word_template_without_data_says_no_data():
    with pytest.raises(DataError, match="No data found for identifier C013"):
        engine.fill("tpl-c013-docx", log=False)


@pytest.mark.slow
def test_word_renders_to_pdf_when_word_is_installed():
    from core.adapters import word_render
    if not word_render.word_available():
        pytest.skip("Microsoft Word not available")
    pdf = word_render.to_pdf(engine.fill("tpl-c002-docx", log=False).output_path)
    import pymupdf
    assert "Delta Pine Mutual" in pymupdf.open(pdf)[0].get_text()
