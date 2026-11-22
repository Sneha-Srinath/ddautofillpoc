import pytest

from core import convert as C
from core.textnorm import normalize


@pytest.mark.parametrize("raw,out", [
    ("$1,250,000", "$1,250,000.00"), ("1.25M", "$1,250,000.00"), ("USD 1,250,000", "$1,250,000.00"),
    ("$8.9 million", "$8,900,000.00"), (48600000, "$48,600,000.00"), ("$3M", "$3,000,000.00"),
])
def test_currency(raw, out):
    c = C.to_currency(raw)
    assert c.ok and c.value == out and not c.flags


def test_currency_approx_is_flagged():
    c = C.to_currency("approx $96M")
    assert c.ok and c.value == "$96,000,000.00" and c.flags


@pytest.mark.parametrize("raw,out", [
    ("2024-03-03", "03/03/2024"), ("March 3, 2024", "03/03/2024"), ("03-Mar-2024", "03/03/2024"),
    ("01/15/2027", "01/15/2027"), ("June 15, 2009", "06/15/2009"),
])
def test_dates(raw, out):
    c = C.to_date(raw)
    assert c.ok and c.value == out and not c.flags


def test_ambiguous_date_flagged_not_dropped():
    c = C.to_date("04/05/2019")
    assert c.ok and c.value == "04/05/2019" and "ambiguous" in c.flags[0]


def test_year_only_is_not_a_date():
    assert not C.to_date("2009").ok


@pytest.mark.parametrize("raw", ["2145550142", "214.555.0142", "(214) 555-0142", "+1 214 555 0142"])
def test_phone(raw):
    assert C.to_phone(raw).value == "(214) 555-0142"


def test_email_lowercased_and_validated():
    assert C.to_email("AMoreno@X.example").value == "amoreno@x.example"
    assert C.to_email("not-an-email").flags


@pytest.mark.parametrize("raw,out", [("Texas", "TX"), ("tx", "TX"), ("North Carolina", "NC")])
def test_state(raw, out):
    assert C.to_state(raw, 2).value == out


@pytest.mark.parametrize("raw,out", [("Yes", True), ("Y", True), ("1", True), ("Checked", True),
                                     ("No", False), ("false", False), ("0", False)])
def test_yesno(raw, out):
    assert C.to_yesno(raw).value is out


def test_yesno_never_guessed():
    c = C.to_yesno("Under review - see disclosure schedule item 4.2")
    assert not c.ok and c.value is None and c.flags


def test_option_symbols_are_exact():
    opts = ["A++", "A+", "A", "A-", "B++"]
    assert C.to_option("A-", opts).value == "A-"
    assert C.to_option("A+", opts).value == "A+"
    assert not C.to_option("Excellent", opts).ok


def test_option_synonym_and_state_options():
    assert C.to_option("LLC", ["Limited Liability Company", "Corporation"]).value == "Limited Liability Company"
    assert C.to_option("Texas", ["OK", "TX"]).value == "TX"
    assert C.to_option("Treaty & Facultative", ["Treaty", "Treaty and Facultative"]).value == "Treaty and Facultative"


def test_text_truncation_flagged():
    c = C.convert("Delaware", "text", "text", max_length=2)
    assert c.value == "De" and c.flags


@pytest.mark.parametrize("a,b", [("Phone_Number", "phone number"), ("phoneNumber", "Phone Number:"),
                                 ("E&O Limit", "EO_Limit"), ("E-mail Address", "e mail address")])
def test_normalize(a, b):
    assert normalize(a) == normalize(b)


@pytest.mark.parametrize("a,b", [("txtCompanyName", "company name"), ("chkMFA", "mfa"), ("S1_LegalName", "legal name"),
                                 ("Sec2_City", "city"), ("Legal Name:", "legal name"), ("manager-legal-name",
                                                                                         "manager legal name"),
                                 ("city", "city"), ("numberOfStates", "number of states")])
def test_normalize_naming_styles(a, b):
    assert normalize(a) == b
