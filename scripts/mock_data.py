"""Single source of truth for all mock data (extracted JSON + SQL rows).

Every company, person, carrier, number and identifier here is FICTIONAL.
FEINs are 00-000000N, NAIC codes are 99xxx, licence numbers start with MOCK-,
phone numbers use the 555-01xx range and web/e-mail domains use .example.
"""
from __future__ import annotations


def v(value, conf: float = 0.95, ref: str | None = None) -> dict:
    """Leaf in the extraction contract: value + confidence + source reference."""
    out = {"value": value, "confidence": conf}
    if ref:
        out["source_ref"] = ref
    return out


# ---------------------------------------------------------------------------
# Client master rows (table: client)
# ---------------------------------------------------------------------------
CLIENTS = [
    {
        "client_id": "C001", "legal_name": "Harbor Point Insurance Group, LLC",
        "dba_name": "Harbor Point Programs", "fein": "00-0000001",
        "entity_type": "Limited Liability Company", "client_type": "Managing General Agent (MGA)",
        "state_of_domicile": "DE", "website": "www.harborpoint-mga.example",
        "year_established": 2009, "established_date": "2009-06-15", "employee_count": 142,
        "naic_code": None, "ownership_structure": "Private Equity Backed",
        "segment": "Commercial P&C programs", "hq_city": "Charlotte, NC",
    },
    {
        "client_id": "C002", "legal_name": "Delta Pine Mutual Insurance Company",
        "dba_name": "Delta Pine Mutual", "fein": "00-0000002",
        "entity_type": "Mutual Company", "client_type": "Regional P&C Carrier",
        "state_of_domicile": "MS", "website": "www.deltapinemutual.example",
        "year_established": 1948, "established_date": "1948-09-01", "employee_count": 388,
        "naic_code": "99021", "ownership_structure": "Mutual (Policyholder Owned)",
        "segment": "Commercial package, farmowners, inland marine", "hq_city": "Jackson, MS",
    },
    {
        "client_id": "C003", "legal_name": "Summit Ridge Specialty Brokers, Inc.",
        "dba_name": "Summit Ridge Wholesale", "fein": "00-0000003",
        "entity_type": "Corporation", "client_type": "Wholesale E&S Broker",
        "state_of_domicile": "TX", "website": "www.summitridge-wholesale.example",
        "year_established": 2014, "established_date": "2014-03-03", "employee_count": 77,
        "naic_code": None, "ownership_structure": "Privately Held",
        "segment": "E&S property, casualty and excess", "hq_city": "Dallas, TX",
    },
    {
        "client_id": "C004", "legal_name": "Bluewater Re Partners, LLC",
        "dba_name": None, "fein": "00-0000004",
        "entity_type": "Limited Liability Company", "client_type": "Reinsurance Intermediary",
        "state_of_domicile": "MA", "website": "www.bluewater-re.example",
        "year_established": 2019, "established_date": None, "employee_count": 34,
        "naic_code": None, "ownership_structure": "Privately Held",
        "segment": "Treaty and facultative placements", "hq_city": "Boston, MA",
    },
    {
        "client_id": "C005", "legal_name": "Keystone Benefits Brokerage, Inc.",
        "dba_name": "Keystone Benefits", "fein": "00-0000005",
        "entity_type": "Corporation", "client_type": "Employee Benefits Agency",
        "state_of_domicile": "PA", "website": "www.keystonebenefits.example",
        "year_established": 2003, "established_date": "2003-05-12", "employee_count": 96,
        "naic_code": None, "ownership_structure": "Privately Held",
        "segment": "Group health, life and voluntary benefits", "hq_city": "Pittsburgh, PA",
    },
]

ADDRESSES = [
    # client_id, address_type, street, city, state, zip
    ("C001", "Mailing", "4200 Morrison Boulevard, Suite 900", "Charlotte", "NC", "28211"),
    ("C001", "Physical", "4200 Morrison Boulevard, Suite 900", "Charlotte", "NC", "28211"),
    ("C002", "Mailing", "PO Box 16400", "Jackson", "MS", "39236"),
    ("C002", "Physical", "1200 Lakeland Court", "Jackson", "MS", "39216"),
    ("C003", "Mailing", "1717 Cedar Springs Road, Suite 1400", "Dallas", "TX", "75201"),
    ("C003", "Physical", "1717 Cedar Springs Road, Suite 1400", "Dallas", "TX", "75201"),
    ("C004", "Mailing", "60 Atlantic Wharf, 11th Floor", "Boston", "MA", "02110"),
    ("C004", "Physical", "60 Atlantic Wharf, 11th Floor", "Boston", "MA", "02110"),
    ("C005", "Mailing", "301 Grant Street, Suite 2600", "Pittsburgh", "PA", "15219"),
    ("C005", "Physical", "301 Grant Street, Suite 2600", "Pittsburgh", "PA", "15219"),
]

CONTACTS = [
    # client_id, role, full_name, title, phone, email
    ("C001", "Primary", "Margaret Ellison", "Chief Operating Officer", "7045550118", "m.ellison@harborpoint-mga.example"),
    ("C001", "CFO", "Daniel Reyes", "Chief Financial Officer", "7045550121", "d.reyes@harborpoint-mga.example"),
    ("C001", "Compliance", "Priya Natarajan", "VP, Compliance & Licensing", "7045550124", "p.natarajan@harborpoint-mga.example"),
    ("C001", "Claims", "Thomas Becker", "Director of Claims", "7045550127", "t.becker@harborpoint-mga.example"),
    ("C002", "Primary", "Robert Haynes", "SVP, Distribution & Partnerships", "6015550142", "rhaynes@deltapinemutual.example"),
    ("C002", "CFO", "Laura Whitfield", "Chief Financial Officer", "6015550145", "lwhitfield@deltapinemutual.example"),
    ("C002", "Compliance", "Marcus Bell", "Chief Compliance Officer", "6015550148", "mbell@deltapinemutual.example"),
    ("C003", "Primary", "Alicia Moreno", "Managing Director", "2145550142", "amoreno@summitridge-wholesale.example"),
    ("C003", "CFO", "Kevin Tran", "Controller", "2145550144", "ktran@summitridge-wholesale.example"),
    ("C003", "Compliance", "Rachel Kim", "Licensing Manager", "2145550146", "rkim@summitridge-wholesale.example"),
    ("C004", "Primary", "Nathaniel Brooks", "Principal", "6175550131", "nbrooks@bluewater-re.example"),
    ("C004", "CFO", "Sofia Marchetti", "Finance Director", "6175550133", "smarchetti@bluewater-re.example"),
    ("C005", "Primary", "Gregory Walsh", "President & Founder", "4125550163", "gwalsh@keystonebenefits.example"),
    ("C005", "CFO", "Hannah Okafor", "Director of Finance", "4125550165", "hokafor@keystonebenefits.example"),
    ("C005", "Compliance", "Ethan Price", "Compliance Officer", "4125550167", "eprice@keystonebenefits.example"),
]

LICENSES = [
    # client_id, state, license_type, license_number, expiry_date
    ("C001", "NC", "Resident", "MOCK-NC-0019284", "2027-06-30"),
    ("C001", "SC", "Non-Resident", "MOCK-SC-0044120", "2027-06-30"),
    ("C001", "GA", "Non-Resident", "MOCK-GA-0071833", "2027-12-31"),
    ("C001", "TX", "Non-Resident", "MOCK-TX-0102877", "2028-03-31"),
    ("C001", "FL", "Non-Resident", "MOCK-FL-0230094", "2027-09-30"),
    ("C002", "MS", "Resident", "MOCK-MS-COA-0007", "2027-12-31"),
    ("C002", "AL", "Non-Resident", "MOCK-AL-COA-0313", "2027-12-31"),
    ("C002", "LA", "Non-Resident", "MOCK-LA-COA-0588", "2027-12-31"),
    ("C003", "TX", "Resident", "MOCK-TX-2290471", "2027-08-31"),
    ("C003", "OK", "Non-Resident", "MOCK-OK-0912655", "2027-08-31"),
    ("C003", "LA", "Non-Resident", "MOCK-LA-0674102", "2028-01-31"),
    ("C004", "MA", "Resident", "MOCK-MA-RI-04417", "2027-10-31"),
    ("C004", "NY", "Non-Resident", "MOCK-NY-RI-11902", "2027-10-31"),
    ("C005", "PA", "Resident", "MOCK-PA-0558213", "2027-04-30"),
    ("C005", "OH", "Non-Resident", "MOCK-OH-1180344", "2027-04-30"),
    ("C005", "WV", "Non-Resident", "MOCK-WV-0093371", "2027-04-30"),
]

FINANCIALS = [
    # client_id, fiscal_year, gross_written_premium, revenue, ebitda, net_income,
    # am_best_rating, policyholder_surplus, combined_ratio
    ("C001", 2023, 39_800_000, 9_200_000, 2_900_000, 1_900_000, None, None, None),
    ("C001", 2024, 44_100_000, 10_300_000, 3_400_000, 2_300_000, None, None, None),
    ("C001", 2025, 48_600_000, 11_500_000, 3_900_000, 2_700_000, None, None, None),
    ("C002", 2023, 191_000_000, 198_400_000, None, 6_100_000, "A-", 88_000_000, 101.4),
    ("C002", 2024, 203_500_000, 211_900_000, None, 7_800_000, "A-", 92_000_000, 99.6),
    ("C002", 2025, 212_000_000, 221_300_000, None, 8_900_000, "A-", 96_000_000, 98.7),
    ("C003", 2023, 286_000_000, 24_100_000, 5_200_000, 3_600_000, None, None, None),
    ("C003", 2024, 318_000_000, 26_900_000, 6_100_000, 4_200_000, None, None, None),
    ("C003", 2025, 342_000_000, 29_400_000, 6_800_000, 4_700_000, None, None, None),
    ("C004", 2023, 210_000_000, 9_600_000, 2_400_000, 1_700_000, None, None, None),
    ("C004", 2024, 246_000_000, 11_100_000, 2_900_000, 2_000_000, None, None, None),
    ("C004", 2025, 271_000_000, 12_400_000, 3_300_000, 2_400_000, None, None, None),
    ("C005", 2023, None, 15_200_000, 3_200_000, 2_200_000, None, None, None),
    ("C005", 2024, None, 16_900_000, 3_700_000, 2_600_000, None, None, None),
    ("C005", 2025, None, 18_400_000, 4_100_000, 2_900_000, None, None, None),
]

INSURANCE = [
    # client_id, coverage_type, carrier, limit_amount, expiry_date
    ("C001", "E&O", "Ironclad Professional Indemnity Co.", 10_000_000, "2027-04-01"),
    ("C001", "Cyber", "Sentinel Cyber Assurance Co.", 5_000_000, "2027-04-01"),
    ("C001", "D&O", "Keel Executive Risk Insurance Co.", 5_000_000, "2027-04-01"),
    ("C001", "Crime", "Granite Shield Casualty Co.", 2_000_000, "2027-04-01"),
    ("C002", "E&O", "Ironclad Professional Indemnity Co.", 15_000_000, "2027-01-01"),
    ("C002", "Cyber", "Sentinel Cyber Assurance Co.", 10_000_000, "2027-01-01"),
    ("C002", "D&O", "Keel Executive Risk Insurance Co.", 10_000_000, "2027-01-01"),
    ("C003", "E&O", "Bastion E&O Underwriters", 5_000_000, "2027-01-15"),
    ("C003", "Cyber", "Sentinel Cyber Assurance Co.", 3_000_000, "2027-01-15"),
    ("C003", "Fidelity Bond", "Granite Shield Casualty Co.", 1_000_000, "2027-01-15"),
    ("C004", "E&O", "Bastion E&O Underwriters", 3_000_000, "2027-07-01"),
    ("C004", "Cyber", "Sentinel Cyber Assurance Co.", 2_000_000, "2027-07-01"),
    ("C005", "E&O", "Ironclad Professional Indemnity Co.", 5_000_000, "2027-03-01"),
    ("C005", "Cyber", "Sentinel Cyber Assurance Co.", 2_000_000, "2027-03-01"),
    ("C005", "Crime", "Keel Executive Risk Insurance Co.", 1_000_000, "2027-03-01"),
]

# DD-specific tables (Data page + Mock Data Report)
PROGRAMS = [
    # client_id, program_name, line_of_business, carrier, binding_authority, gwp, loss_ratio_3yr
    ("C001", "Harbor Habitational Advantage", "Habitational (apartments, condominiums)", "Granite Shield Casualty Co.", "Full", 14_200_000, 51.8),
    ("C001", "TradeGuard Artisan Contractors", "Contractors General Liability", "Northgate Specialty Insurance Co.", "Full", 9_600_000, 48.9),
    ("C001", "TableSide Restaurant Package", "Hospitality Package / BOP", "Granite Shield Casualty Co.", "Full", 7_400_000, 57.3),
    ("C001", "RouteSafe Light Fleet", "Commercial Auto (light fleet)", "Meridian Assurance Group", "Limited", 6_900_000, 68.4),
    ("C001", "VaultStor Self-Storage", "Self-Storage Property & GL", "Northgate Specialty Insurance Co.", "Full", 5_800_000, 41.2),
    ("C001", "Harbor Excess & Umbrella", "Commercial Umbrella / Excess", "Meridian Assurance Group", "Referral", 4_700_000, 49.6),
    ("C002", "Main Street Commercial Package", "Commercial Package", "Delta Pine Mutual (direct)", "Full", 98_000_000, 61.2),
    ("C002", "Delta Farm & Ranch", "Farmowners", "Delta Pine Mutual (direct)", "Full", 64_000_000, 66.8),
    ("C002", "Gulf Inland Marine", "Inland Marine", "Delta Pine Mutual (direct)", "Full", 27_000_000, 44.5),
    ("C002", "Pine Belt Commercial Auto", "Commercial Auto", "Delta Pine Mutual (direct)", "Full", 23_000_000, 71.9),
    ("C003", "E&S Property Practice", "E&S Commercial Property", "Multiple E&S markets", "Limited", 162_000_000, 47.3),
    ("C003", "Casualty Practice", "E&S General Liability", "Multiple E&S markets", "Limited", 118_000_000, 55.1),
    ("C003", "Excess Casualty Desk", "Excess / Umbrella", "Multiple E&S markets", "Referral", 62_000_000, 52.6),
    ("C004", "Regional Carrier Treaty", "Property Cat XOL & Quota Share", "Reinsurance panel", "Referral", 181_000_000, 58.0),
    ("C004", "Facultative Casualty", "Facultative Casualty", "Reinsurance panel", "Referral", 90_000_000, 62.4),
    ("C005", "Group Health", "Group Medical / Rx", "Multiple carriers", "None", None, None),
    ("C005", "Life & Disability", "Group Life / LTD / STD", "Multiple carriers", "None", None, None),
    ("C005", "Voluntary Benefits", "Voluntary / Worksite", "Multiple carriers", "None", None, None),
]

LOSS_RUNS = [
    # client_id, year, earned_premium, incurred_losses, claim_count, large_losses_over_250k
    ("C001", 2023, 37_100_000, 20_600_000, 1184, 6),
    ("C001", 2024, 41_900_000, 22_900_000, 1262, 7),
    ("C001", 2025, 46_200_000, 24_100_000, 1301, 5),
    ("C002", 2023, 186_000_000, 121_300_000, 6420, 19),
    ("C002", 2024, 198_000_000, 122_800_000, 6610, 17),
    ("C002", 2025, 207_000_000, 124_600_000, 6705, 15),
    ("C003", 2023, 271_000_000, 141_900_000, 2210, 22),
    ("C003", 2024, 302_000_000, 154_000_000, 2385, 24),
    ("C003", 2025, 330_000_000, 166_300_000, 2502, 21),
    ("C004", 2023, 198_000_000, 121_000_000, 140, 31),
    ("C004", 2024, 233_000_000, 138_600_000, 162, 28),
    ("C004", 2025, 259_000_000, 152_800_000, 171, 26),
]

CARRIER_RELATIONSHIPS = [
    # client_id, carrier, am_best, relationship_since, pct_of_premium, contract_expiry
    ("C001", "Granite Shield Casualty Co.", "A", 2012, 44.4, "2028-12-31"),
    ("C001", "Northgate Specialty Insurance Co.", "A+", 2015, 31.7, "2027-12-31"),
    ("C001", "Meridian Assurance Group", "A-", 2018, 23.9, "2027-06-30"),
    ("C002", "Atlas Peak Reinsurance Ltd. (quota share)", "A+", 2006, 40.0, "2027-01-01"),
    ("C002", "Coastline Re SE (cat XOL)", "A", 2011, 35.0, "2027-06-01"),
    ("C002", "Harrow Mutual Re (per-risk)", "A-", 2017, 25.0, "2027-01-01"),
    ("C003", "Northgate Specialty Insurance Co.", "A+", 2015, 28.5, "2027-12-31"),
    ("C003", "Ironbridge Excess & Surplus Co.", "A", 2016, 24.0, "2027-06-30"),
    ("C003", "Lonestar Surplus Lines Co.", "A-", 2019, 18.2, "2027-03-31"),
    ("C003", "Other E&S markets (14)", "A- or better", 2014, 29.3, None),
    ("C004", "Atlas Peak Reinsurance Ltd.", "A+", 2019, 37.0, "2027-01-01"),
    ("C004", "Coastline Re SE", "A", 2020, 33.0, "2027-01-01"),
    ("C004", "Harrow Mutual Re", "A-", 2021, 30.0, "2027-01-01"),
    ("C005", "Allegheny Health Plan (fictional)", "A", 2004, 41.0, "2027-12-31"),
    ("C005", "Three Rivers Life & Disability (fictional)", "A", 2008, 22.0, "2027-12-31"),
    ("C005", "Commonwealth Dental & Vision (fictional)", "A-", 2012, 14.0, "2027-12-31"),
    ("C005", "Other carriers (9)", "Various", 2003, 23.0, None),
]

OWNERSHIP = [
    # client_id, owner, pct_held, pe_backed
    ("C001", "Ridgeline Capital Partners Fund III, L.P.", 52.0, 1),
    ("C001", "Ellison Family Trust", 38.0, 0),
    ("C001", "Management incentive pool", 10.0, 0),
    ("C002", "Policyholders (mutual)", 100.0, 0),
    ("C003", "Alicia Moreno", 55.0, 0),
    ("C003", "Founding partners (3)", 45.0, 0),
    ("C004", "Nathaniel Brooks", 60.0, 0),
    ("C004", "Sofia Marchetti", 20.0, 0),
    ("C004", "Employee partners", 20.0, 0),
    ("C005", "Gregory Walsh", 82.0, 0),
    ("C005", "Key employee shareholders (4)", 18.0, 0),
]

DD_ASSESSMENTS = [
    # client_id, financial_strength, underwriting_controls, claims_handling, compliance,
    # cyber_it, overall_risk_rating, analyst, assessed_on, summary
    ("C001", 4.4, 4.6, 4.2, 4.7, 4.1, "Low", "J. Carter", "2026-11-14",
     "Profitable, well-diversified program MGA. Carrier audits clean; capacity concentration is moderate."),
    ("C002", 3.9, 4.0, 3.8, 4.3, 3.6, "Moderate", "J. Carter", "2026-11-14",
     "Stable regional mutual. Farm and auto lines run hot; catastrophe exposure is well reinsured."),
    ("C003", 4.1, 3.9, 4.0, 4.2, 3.9, "Moderate", "S. Patel", "2026-11-15",
     "Fast-growing wholesale broker. E&O limit confirmation pending; licensing current in 38 states."),
    ("C004", 3.8, 4.0, 3.7, 4.4, 3.5, "Moderate", "S. Patel", "2026-11-15",
     "Young intermediary with strong panel security. Formation records need confirmation."),
    ("C005", 3.7, 3.5, 3.6, 3.4, 3.8, "Elevated", "M. Alvarez", "2026-11-16",
     "Attractive benefits book with carrier concentration risk and an unresolved litigation item."),
]


# ---------------------------------------------------------------------------
# Extracted JSON: one document per client, deliberately different key names
# ---------------------------------------------------------------------------
EXTRACTED = {}

_r1 = "HPIG_Audited_Financials_FY2025.pdf"
EXTRACTED["C001"] = {
    "client_id": "C001",
    "client_name": "Harbor Point Insurance Group, LLC",
    "extracted_at": "2026-11-18T14:05:00Z",
    "source_documents": [_r1, "HPIG_Granite_Shield_Program_Agreement_2024.pdf",
                         "HPIG_Carrier_Audit_Letter_2026.pdf", "HPIG_Loss_Runs_2023-2025.xlsx",
                         "HPIG_SOC2_Type_II_2026.pdf", "HPIG_EO_Declarations_2026.pdf"],
    "entity": {
        "legal_name": v("Harbor Point Insurance Group, LLC", 0.98, f"{_r1}#p1"),
        "dba_name": v("Harbor Point Programs", 0.93, f"{_r1}#p1"),
        "fein": v("00-0000001", 0.96, f"{_r1}#p2"),
        "entity_type": v("LLC", 0.94, f"{_r1}#p2"),
        "date_established": v("June 15, 2009", 0.92, f"{_r1}#p2"),
        "state_of_domicile": v("Delaware", 0.95, f"{_r1}#p2"),
        "website": v("www.harborpoint-mga.example", 0.90),
    },
    "mailing_address": {
        "street": v("4200 Morrison Boulevard, Suite 900", 0.97, f"{_r1}#p1"),
        "city": v("Charlotte", 0.98, f"{_r1}#p1"),
        "state": v("North Carolina", 0.97, f"{_r1}#p1"),
        "zip": v("28211", 0.97, f"{_r1}#p1"),
    },
    "primary_contact": {
        "name": v("Margaret Ellison", 0.96, "HPIG_Granite_Shield_Program_Agreement_2024.pdf#p14"),
        "title": v("Chief Operating Officer", 0.94),
        "phone": v("704-555-0118", 0.95),
        "email": v("M.Ellison@HarborPoint-MGA.example", 0.95),
    },
    "operations": {
        "gross_written_premium": v("$48.6M", 0.93, f"{_r1}#p6"),
        "lines_of_business": v("Habitational, Artisan Contractors GL, Restaurant Package, "
                               "Light Fleet Auto, Self-Storage, Excess/Umbrella", 0.90),
        "active_programs": v("6", 0.95, "HPIG_Granite_Shield_Program_Agreement_2024.pdf#p3"),
        "three_year_loss_ratio": v("54.0%", 0.91, "HPIG_Loss_Runs_2023-2025.xlsx#Summary"),
        "binding_authority": v("Full", 0.89, "HPIG_Granite_Shield_Program_Agreement_2024.pdf#p5"),
        "uses_third_party_administrator": v("Yes", 0.90, "HPIG_Carrier_Audit_Letter_2026.pdf#p2"),
    },
    "underwriting": {
        "carrier_audit_score": v("94/100", 0.92, "HPIG_Carrier_Audit_Letter_2026.pdf#p1"),
        "referral_threshold": v("TIV above $25M or any risk outside program guidelines", 0.86),
        "underwriters_on_staff": v("38", 0.88),
    },
    "claims": {
        "tpa_name": v("Crestline Claims Services (fictional)", 0.90),
        "average_days_to_close": v("41", 0.87, "HPIG_Carrier_Audit_Letter_2026.pdf#p3"),
    },
    "compliance": {
        "regulatory_actions_last_5_years": v("No", 0.93, "HPIG_Carrier_Audit_Letter_2026.pdf#p4"),
        "pending_litigation": v("No", 0.91),
        "ofac_screening": v("Yes", 0.94),
    },
    "insurance": {
        "errors_omissions_limit": v("$10,000,000", 0.95, "HPIG_EO_Declarations_2026.pdf#p1"),
        "cyber_insurance_in_force": v("Yes", 0.92, "HPIG_SOC2_Type_II_2026.pdf#p22"),
    },
    "cyber_it": {
        "mfa_enforced": v("Yes", 0.93, "HPIG_SOC2_Type_II_2026.pdf#p9"),
        "soc2_type_ii": v("Yes", 0.97, "HPIG_SOC2_Type_II_2026.pdf#p1"),
    },
    "risk_findings": [
        {"area": "Capacity concentration", "rating": "Medium",
         "finding": "Granite Shield provides 44% of premium capacity", "confidence": 0.88},
        {"area": "Commercial auto", "rating": "Medium",
         "finding": "RouteSafe Light Fleet 3-yr loss ratio 68.4%, above 65% target", "confidence": 0.86},
        {"area": "Controls", "rating": "Low",
         "finding": "Clean carrier audit (94/100); SOC 2 Type II with no exceptions", "confidence": 0.93},
    ],
}

_r2 = "DPM_Annual_Statement_2025.pdf"
EXTRACTED["C002"] = {
    "client_id": "C002",
    "client_name": "Delta Pine Mutual Insurance Company",
    "extracted_at": "2026-11-18T14:12:00Z",
    "source_documents": [_r2, "DPM_AM_Best_Rating_Report_2026.pdf", "DPM_Reinsurance_Summary_2026.pdf",
                         "DPM_Partner_Onboarding_Letter.pdf"],
    "company_profile": {
        "registered_name": v("Delta Pine Mutual Insurance Company", 0.97, f"{_r2}#p1"),
        "doing_business_as": v("Delta Pine Mutual", 0.90),
        "naic_company_code": v("99021", 0.94, f"{_r2}#p1"),
        "date_of_incorporation": v("September 1, 1948", 0.90, f"{_r2}#p1"),
        "state_of_domicile": v("Mississippi", 0.96, f"{_r2}#p1"),
    },
    "headquarters_address": {
        "street": v("PO Box 16400", 0.93),
        "city": v("Jackson", 0.97),
        "state": v("Mississippi", 0.97),
        "zip_code": v("39236", 0.95),
    },
    "partnership_contact": {
        "full_name": v("Robert Haynes", 0.95, "DPM_Partner_Onboarding_Letter.pdf#p1"),
        "title": v("SVP, Distribution & Partnerships", 0.92),
        # CONFLICT: differs from the DB phone (DB is master data, so the DB value wins)
        "telephone": v("(601) 555-0147", 0.88, "DPM_Partner_Onboarding_Letter.pdf#p2"),
        "email": v("rhaynes@deltapinemutual.example", 0.94),
    },
    "statutory_financials": {
        # CONFLICT: JSON $214.5M vs DB 212,000,000 (document fact, JSON first)
        "direct_written_premium": v("$214.5M", 0.87, f"{_r2}#p4"),
        # APPROXIMATE: "approx" -> Review
        "policyholder_surplus": v("approx $96M", 0.85, f"{_r2}#p3"),
        "net_income": v("$8.9 million", 0.92, f"{_r2}#p5"),
        "combined_ratio": v("98.7%", 0.90, f"{_r2}#p5"),
    },
    "rating": {
        # NOT AN OPTION: "Excellent" is a category, not a rating -> fall back to DB "A-" + Review
        "financial_strength_rating": v("Excellent", 0.84, "DPM_AM_Best_Rating_Report_2026.pdf#p1"),
        "rating_outlook": v("Stable", 0.91, "DPM_AM_Best_Rating_Report_2026.pdf#p1"),
    },
    "reinsurance": {
        "reinsurance_program_in_place": v("Yes", 0.95, "DPM_Reinsurance_Summary_2026.pdf#p1"),
        "uses_catastrophe_modeling": v("Yes", 0.89, "DPM_Reinsurance_Summary_2026.pdf#p4"),
        "cat_retention": v("$7,500,000 per occurrence", 0.88),
    },
    "risk_findings": [
        {"area": "Farmowners results", "rating": "Medium",
         "finding": "Farm & Ranch 3-yr loss ratio 66.8%", "confidence": 0.86},
        {"area": "Catastrophe", "rating": "Low",
         "finding": "Cat XOL protects to a 1-in-250 PML", "confidence": 0.83},
    ],
}

_r3 = "SRSB_Agency_Profile_2026.pdf"
EXTRACTED["C003"] = {
    "client_id": "C003",
    "client_name": "Summit Ridge Specialty Brokers, Inc.",
    "extracted_at": "2026-11-18T14:20:00Z",
    "source_documents": [_r3, "SRSB_TX_License_Certificate.pdf", "SRSB_EO_Certificate_2026.pdf",
                         "SRSB_Reviewed_Financials_2025.pdf"],
    "agency": {
        "agency_name": v("Summit Ridge Specialty Brokers, Inc.", 0.97, f"{_r3}#p1"),
        "trade_name": v("Summit Ridge Wholesale", 0.91),
        "fein": v("00-0000003", 0.95, f"{_r3}#p1"),
        "date_established": v("March 3, 2014", 0.93, f"{_r3}#p1"),   # FORMAT: -> 03/03/2014
        "website": v("www.summitridge-wholesale.example", 0.90),
    },
    "mailing": {
        "address": v("1717 Cedar Springs Road, Suite 1400", 0.95),
        "city": v("Dallas", 0.97),
        "state": v("Texas", 0.97),                                      # FORMAT: -> TX
        "zip": v("75201", 0.96),
    },
    "principal": {
        "name": v("Alicia Moreno", 0.96),
        "title": v("Managing Director", 0.94),
        "phone": v("214.555.0142", 0.93),                               # FORMAT: -> (214) 555-0142
        "email": v("AMoreno@summitridge-wholesale.example", 0.94),
    },
    "licensing": {
        "resident_state": v("Texas", 0.96, "SRSB_TX_License_Certificate.pdf#p1"),
        "resident_license_number": v("MOCK-TX-2290471", 0.95, "SRSB_TX_License_Certificate.pdf#p1"),
        "license_expiration_date": v("2027-08-31", 0.94),
        "number_of_states_licensed": v("38", 0.90, f"{_r3}#p3"),
        "prior_license_revocation": v("No", 0.92),
    },
    "errors_and_omissions": {
        "carrier": v("Bastion E&O Underwriters", 0.90, "SRSB_EO_Certificate_2026.pdf#p1"),
        # LOW CONFIDENCE: 0.64 -> Review
        "limit_per_claim": v("$5,000,000", 0.64, "SRSB_EO_Certificate_2026.pdf#p1"),
        "expiration_date": v("01/15/2027", 0.91),
    },
    "appointment": {
        "appointment_type_requested": v("Surplus Lines Only", 0.88),
        "binds_coverage_on_behalf_of_carriers": v("Yes", 0.87),
    },
    "production": {
        "premium_placed_2025": v("$342M", 0.90, "SRSB_Reviewed_Financials_2025.pdf#p2"),
        "commission_revenue_2025": v("$29.4M", 0.90, "SRSB_Reviewed_Financials_2025.pdf#p2"),
    },
}

_r4 = "BWRP_Counterparty_Questionnaire.pdf"
EXTRACTED["C004"] = {
    "client_id": "C004",
    "client_name": "Bluewater Re Partners, LLC",
    "extracted_at": "2026-11-18T14:31:00Z",
    "source_documents": [_r4, "BWRP_Operating_Agreement.pdf", "BWRP_Panel_Security_Report_2026.pdf",
                         "BWRP_Sanctions_Policy.pdf"],
    "counterparty": {
        "entity_name": v("Bluewater Re Partners, LLC", 0.97, f"{_r4}#p1"),
        # AMBIGUOUS DATE: April 5 or May 4? -> Review, never guessed silently
        "formation_date": v("04/05/2019", 0.90, "BWRP_Operating_Agreement.pdf#p1"),
        "years_in_business": v("7", 0.92),
        # NOTE: no FEIN in the documents -> comes from the DB only
    },
    "office": {
        "street_address": v("60 Atlantic Wharf, 11th Floor", 0.95),
        "city": v("Boston", 0.98),
        "state_code": v("MA", 0.98),
        "postal_code": v("02110", 0.96),
    },
    "key_contact": {
        "name": v("Nathaniel Brooks", 0.96),
        "title": v("Principal", 0.93),
        "phone": v("617-555-0131", 0.94),
        "email": v("nbrooks@bluewater-re.example", 0.95),
    },
    "security": {
        # JSON ONLY: no rating column for this client in the DB
        "financial_strength_rating": v("A+", 0.90, "BWRP_Panel_Security_Report_2026.pdf#p2"),
    },
    "business": {
        "annual_brokerage_revenue": v("$12.4M", 0.91),                   # FORMAT: -> $12,400,000.00
        "placement_type": v("Treaty & Facultative", 0.89),
        "errors_omissions_limit": v("$3M", 0.90),
    },
    "controls": {
        "collateral_required": v("Yes", 0.88),
        "sanctions_screening_performed": v("Yes", 0.95, "BWRP_Sanctions_Policy.pdf#p2"),
        "cyber_coverage_in_force": v("Yes", 0.90),
    },
}

_r5 = "KBB_Confidential_Information_Memorandum.pdf"
EXTRACTED["C005"] = {
    "client_id": "C005",
    "client_name": "Keystone Benefits Brokerage, Inc.",
    "extracted_at": "2026-11-18T14:44:00Z",
    "source_documents": [_r5, "KBB_TTM_Financials_Sep2026.xlsx", "KBB_Book_of_Business_Summary.pdf",
                         "KBB_Legal_Disclosure_Schedule.pdf"],
    "target_company": {
        "company_name": v("Keystone Benefits Brokerage, Inc.", 0.97, f"{_r5}#p1"),
        "dba": v("Keystone Benefits", 0.92),
        "fein": v("00-0000005", 0.94),
        "founded": v("2003-05-12", 0.95, f"{_r5}#p2"),
        "state_of_incorporation": v("Pennsylvania", 0.95),
        "employees": v("96", 0.92),
    },
    "address": {
        "street": v("301 Grant Street, Suite 2600", 0.96),
        "city": v("Pittsburgh", 0.98),
        "state": v("PA", 0.98),
        "zip": v("15219", 0.97),
    },
    "contact": {
        "name": v("Gregory Walsh", 0.97),
        "title": v("President & Founder", 0.95),
        "phone": v("412-555-0163", 0.95),
        "email": v("gwalsh@keystonebenefits.example", 0.96),
    },
    "ownership": {
        "structure": v("Privately Held", 0.90, f"{_r5}#p4"),
    },
    "financial_summary": {
        "revenue_ttm": v("$18.4M", 0.93, "KBB_TTM_Financials_Sep2026.xlsx#PnL"),
        "ebitda_ttm": v("$4.1M", 0.86, "KBB_TTM_Financials_Sep2026.xlsx#PnL"),
    },
    "book": {
        "group_clients": v("1,140", 0.91, "KBB_Book_of_Business_Summary.pdf#p1"),
        "top_carrier_concentration_pct": v("41%", 0.90, "KBB_Book_of_Business_Summary.pdf#p2"),
        "client_retention_rate": v("93.5%", 0.89, "KBB_Book_of_Business_Summary.pdf#p2"),
        # MISSING: question exists in the CIM, extraction found no answer
        "top_10_client_concentration_pct": v(None, 0.0),
    },
    "legal": {
        # AMBIGUOUS YES/NO: "under review" -> not guessed, flagged
        "pending_litigation": v("Under review - see disclosure schedule item 4.2", 0.71,
                                "KBB_Legal_Disclosure_Schedule.pdf#p3"),
        "eo_claims_last_5_years": v("No", 0.88, "KBB_Legal_Disclosure_Schedule.pdf#p2"),
    },
    "contracts": {
        # MISSING
        "non_compete_agreements": v(None, 0.0),
    },
    "insurance": {
        "cyber_coverage": v("Yes", 0.92),
    },
    "deal": {
        "preferred_transaction_structure": v("Asset Purchase", 0.87, f"{_r5}#p9"),
    },
}


# ---------------------------------------------------------------------------
# Seven more companies (C006 to C012) live in mock_data_extra.py
# ---------------------------------------------------------------------------
from scripts import mock_data_extra as _extra  # noqa: E402

CLIENTS += _extra.CLIENTS
ADDRESSES += _extra.ADDRESSES
CONTACTS += _extra.CONTACTS
LICENSES += _extra.LICENSES
FINANCIALS += _extra.FINANCIALS
INSURANCE += _extra.INSURANCE
PROGRAMS += _extra.PROGRAMS
LOSS_RUNS += _extra.LOSS_RUNS
CARRIER_RELATIONSHIPS += _extra.CARRIER_RELATIONSHIPS
OWNERSHIP += _extra.OWNERSHIP
DD_ASSESSMENTS += _extra.DD_ASSESSMENTS
LENDING = list(_extra.LENDING)
EXTRACTED.update(_extra.EXTRACTED)
