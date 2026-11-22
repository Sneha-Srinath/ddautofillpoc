"""Seven more fictional companies (C006 to C012), appended to the lists in scripts.mock_data.

Same conventions: FEIN 00-000000N, NAIC 99xxx, licence numbers MOCK-, phones 555-01xx, .example domains.
Each company adds a data situation the first five do not show:
  C006 conflict on premium + a new yes/no concept      C010 database only (no extracted JSON) + Unmapped fields
  C007 JSON value missing -> database fallback          C011 fast-growing insurtech, low-confidence premium
  C008 missing answers in a captive questionnaire       C012 clean fill with section-coded field names
  C009 "N/A" yes/no and an approximate number
"""
from __future__ import annotations


def v(value, conf: float = 0.95, ref: str | None = None) -> dict:
    out = {"value": value, "confidence": conf}
    if ref:
        out["source_ref"] = ref
    return out


CLIENTS = [
    {"client_id": "C006", "legal_name": "Ironwood Specialty Underwriters, LLC", "dba_name": "Ironwood Transportation",
     "fein": "00-0000006", "entity_type": "Limited Liability Company", "client_type": "Managing General Agent (MGA)",
     "state_of_domicile": "GA", "website": "www.ironwood-su.example", "year_established": 2012,
     "established_date": "2012-04-02", "employee_count": 88, "naic_code": None,
     "ownership_structure": "Private Equity Backed", "segment": "Trucking, cargo and last-mile delivery programs",
     "hq_city": "Atlanta, GA"},
    {"client_id": "C007", "legal_name": "Lakeshore Mutual Casualty Company", "dba_name": "Lakeshore Mutual",
     "fein": "00-0000007", "entity_type": "Mutual Company", "client_type": "Regional P&C Carrier",
     "state_of_domicile": "WI", "website": "www.lakeshoremutual.example", "year_established": 1921,
     "established_date": "1921-03-15", "employee_count": 512, "naic_code": "99047",
     "ownership_structure": "Mutual (Policyholder Owned)", "segment": "Commercial lines, farm and small business",
     "hq_city": "Milwaukee, WI"},
    {"client_id": "C008", "legal_name": "Granite Peak Captive Managers, Inc.", "dba_name": "Granite Peak Captives",
     "fein": "00-0000008", "entity_type": "Corporation", "client_type": "Captive Insurance Manager",
     "state_of_domicile": "VT", "website": "www.granitepeak-captives.example", "year_established": 2006,
     "established_date": "2006-08-21", "employee_count": 41, "naic_code": None,
     "ownership_structure": "Privately Held", "segment": "Single-parent, group and cell captives",
     "hq_city": "Burlington, VT"},
    {"client_id": "C009", "legal_name": "Crestline Claims Services, Inc.", "dba_name": "Crestline TPA",
     "fein": "00-0000009", "entity_type": "Corporation", "client_type": "Third-Party Claims Administrator (TPA)",
     "state_of_domicile": "OH", "website": "www.crestline-claims.example", "year_established": 1998,
     "established_date": "1998-10-05", "employee_count": 264, "naic_code": None,
     "ownership_structure": "Privately Held", "segment": "Commercial auto, GL and workers compensation claims",
     "hq_city": "Columbus, OH"},
    {"client_id": "C010", "legal_name": "Northstar Premium Finance Company", "dba_name": "Northstar PFC",
     "fein": "00-0000010", "entity_type": "Corporation", "client_type": "Premium Finance Company",
     "state_of_domicile": "MN", "website": "www.northstar-pfc.example", "year_established": 2001,
     "established_date": "2001-02-14", "employee_count": 63, "naic_code": None,
     "ownership_structure": "Privately Held", "segment": "Commercial premium financing through agents",
     "hq_city": "Minneapolis, MN"},
    {"client_id": "C011", "legal_name": "BrightPath Digital Insurance Agency, Inc.", "dba_name": "BrightPath",
     "fein": "00-0000011", "entity_type": "Corporation", "client_type": "Insurtech MGA",
     "state_of_domicile": "DE", "website": "www.brightpath-insure.example", "year_established": 2019,
     "established_date": "2019-09-09", "employee_count": 58, "naic_code": None,
     "ownership_structure": "Private Equity Backed", "segment": "Embedded small-business BOP and cyber",
     "hq_city": "Austin, TX"},
    {"client_id": "C012", "legal_name": "Cascade Surplus Lines Brokerage, LLC", "dba_name": "Cascade Wholesale",
     "fein": "00-0000012", "entity_type": "Limited Liability Company", "client_type": "Surplus Lines Wholesaler",
     "state_of_domicile": "WA", "website": "www.cascade-sl.example", "year_established": 2010,
     "established_date": "2010-06-01", "employee_count": 49, "naic_code": None,
     "ownership_structure": "Privately Held", "segment": "E&S property, construction and habitational",
     "hq_city": "Seattle, WA"},
]

ADDRESSES = [
    ("C006", "Mailing", "3350 Peachtree Road NE, Suite 1500", "Atlanta", "GA", "30326"),
    ("C006", "Physical", "3350 Peachtree Road NE, Suite 1500", "Atlanta", "GA", "30326"),
    ("C007", "Mailing", "PO Box 2210", "Milwaukee", "WI", "53201"),
    ("C007", "Physical", "777 East Wisconsin Avenue", "Milwaukee", "WI", "53202"),
    ("C008", "Mailing", "100 Bank Street, Suite 610", "Burlington", "VT", "05401"),
    ("C009", "Mailing", "250 West Street, Floor 4", "Columbus", "OH", "43215"),
    ("C009", "Physical", "250 West Street, Floor 4", "Columbus", "OH", "43215"),
    ("C010", "Mailing", "80 South Eighth Street, Suite 1900", "Minneapolis", "MN", "55402"),
    ("C011", "Mailing", "500 West 2nd Street, Suite 1900", "Austin", "TX", "78701"),
    ("C012", "Mailing", "1201 Third Avenue, Suite 3400", "Seattle", "WA", "98101"),
    ("C012", "Physical", "1201 Third Avenue, Suite 3400", "Seattle", "WA", "98101"),
]

CONTACTS = [
    ("C006", "Primary", "Marcus Delaney", "President", "4045550112", "mdelaney@ironwood-su.example"),
    ("C006", "CFO", "Elena Park", "Chief Financial Officer", "4045550114", "epark@ironwood-su.example"),
    ("C007", "Primary", "Karen Lindqvist", "VP, Reinsurance", "4145550151", "klindqvist@lakeshoremutual.example"),
    ("C007", "CFO", "Paul Brennan", "Treasurer", "4145550153", "pbrennan@lakeshoremutual.example"),
    ("C008", "Primary", "Owen Whitcomb", "Managing Director", "8025550176", "owhitcomb@granitepeak-captives.example"),
    ("C009", "Primary", "Dana Kowalski", "VP, Claims Operations", "6145550188", "dkowalski@crestline-claims.example"),
    ("C009", "CFO", "Raj Mehta", "Chief Financial Officer", "6145550189", "rmehta@crestline-claims.example"),
    ("C010", "Primary", "Lisa Hendrickson", "Chief Operating Officer", "6125550193", "lhendrickson@northstar-pfc.example"),
    ("C010", "CFO", "Tom Aldridge", "Chief Financial Officer", "6125550195", "taldridge@northstar-pfc.example"),
    ("C011", "Primary", "Priya Raman", "Co-Founder & CEO", "5125550161", "priya@brightpath-insure.example"),
    ("C011", "Compliance", "Jordan Blake", "Head of Compliance", "5125550163", "jblake@brightpath-insure.example"),
    ("C012", "Primary", "Megan O'Rourke", "Principal Broker", "2065550171", "morourke@cascade-sl.example"),
]

LICENSES = [
    ("C006", "GA", "Resident", "MOCK-GA-0381144", "2027-11-30"),
    ("C006", "TN", "Non-Resident", "MOCK-TN-0920051", "2027-11-30"),
    ("C006", "FL", "Non-Resident", "MOCK-FL-0412278", "2028-02-28"),
    ("C007", "WI", "Resident", "MOCK-WI-COA-0019", "2027-12-31"),
    ("C007", "MN", "Non-Resident", "MOCK-MN-COA-0230", "2027-12-31"),
    ("C008", "VT", "Resident", "MOCK-VT-CM-00412", "2027-06-30"),
    ("C009", "OH", "Resident", "MOCK-OH-TPA-0088", "2027-09-30"),
    ("C010", "MN", "Resident", "MOCK-MN-PF-01177", "2027-12-31"),
    ("C010", "WI", "Non-Resident", "MOCK-WI-PF-00563", "2027-12-31"),
    ("C011", "TX", "Resident", "MOCK-TX-3301928", "2027-09-30"),
    ("C012", "WA", "Resident", "MOCK-WA-SL-118204", "2027-05-31"),
    ("C012", "OR", "Non-Resident", "MOCK-OR-SL-097731", "2027-05-31"),
]

FINANCIALS = [
    ("C006", 2023, 61_200_000, 14_100_000, 3_800_000, 2_600_000, None, None, None),
    ("C006", 2024, 66_800_000, 15_600_000, 4_300_000, 3_000_000, None, None, None),
    ("C006", 2025, 72_400_000, 17_000_000, 4_900_000, 3_400_000, None, None, None),
    ("C007", 2023, 288_000_000, 330_000_000, None, 9_400_000, "A", 166_000_000, 100.8),
    ("C007", 2024, 301_000_000, 342_000_000, None, 11_200_000, "A", 175_000_000, 99.1),
    ("C007", 2025, 316_000_000, 357_000_000, None, 12_800_000, "A", 184_000_000, 97.9),
    ("C008", 2023, 410_000_000, 7_900_000, 1_900_000, 1_300_000, None, None, None),
    ("C008", 2024, 445_000_000, 8_600_000, 2_100_000, 1_500_000, None, None, None),
    ("C008", 2025, 482_000_000, 9_300_000, 2_400_000, 1_700_000, None, None, None),
    ("C009", 2023, None, 38_600_000, 5_900_000, 3_900_000, None, None, None),
    ("C009", 2024, None, 41_200_000, 6_400_000, 4_300_000, None, None, None),
    ("C009", 2025, None, 44_900_000, 7_100_000, 4_800_000, None, None, None),
    ("C010", 2023, None, 21_400_000, 6_100_000, 4_200_000, None, None, None),
    ("C010", 2024, None, 22_900_000, 6_700_000, 4_600_000, None, None, None),
    ("C010", 2025, None, 24_600_000, 7_200_000, 5_000_000, None, None, None),
    ("C011", 2023, 18_200_000, 4_000_000, -2_100_000, -2_900_000, None, None, None),
    ("C011", 2024, 29_600_000, 6_800_000, -800_000, -1_500_000, None, None, None),
    ("C011", 2025, 44_100_000, 10_100_000, 900_000, 300_000, None, None, None),
    ("C012", 2023, 132_000_000, 13_900_000, 3_100_000, 2_200_000, None, None, None),
    ("C012", 2024, 147_000_000, 15_200_000, 3_500_000, 2_500_000, None, None, None),
    ("C012", 2025, 165_000_000, 17_100_000, 4_000_000, 2_900_000, None, None, None),
]

LENDING = [
    # client_id, fiscal_year, loans_outstanding, default_rate, contracts_financed
    ("C010", 2023, 312_000_000, 1.9, 18_400),
    ("C010", 2024, 338_000_000, 1.7, 19_650),
    ("C010", 2025, 361_000_000, 1.6, 20_900),
]

INSURANCE = [
    ("C006", "E&O", "Ironclad Professional Indemnity Co.", 10_000_000, "2027-02-01"),
    ("C006", "Cyber", "Sentinel Cyber Assurance Co.", 5_000_000, "2027-02-01"),
    ("C007", "E&O", "Keel Executive Risk Insurance Co.", 20_000_000, "2027-01-01"),
    ("C007", "Cyber", "Sentinel Cyber Assurance Co.", 15_000_000, "2027-01-01"),
    ("C008", "E&O", "Bastion E&O Underwriters", 5_000_000, "2027-08-01"),
    ("C008", "Cyber", "Sentinel Cyber Assurance Co.", 3_000_000, "2027-08-01"),
    ("C009", "E&O", "Ironclad Professional Indemnity Co.", 15_000_000, "2027-05-01"),
    ("C009", "Cyber", "Sentinel Cyber Assurance Co.", 10_000_000, "2027-05-01"),
    ("C010", "E&O", "Keel Executive Risk Insurance Co.", 5_000_000, "2027-03-15"),
    ("C011", "E&O", "Bastion E&O Underwriters", 5_000_000, "2027-09-01"),
    ("C011", "Cyber", "Sentinel Cyber Assurance Co.", 5_000_000, "2027-09-01"),
    ("C012", "E&O", "Ironclad Professional Indemnity Co.", 5_000_000, "2027-06-01"),
    ("C012", "Cyber", "Sentinel Cyber Assurance Co.", 2_000_000, "2027-06-01"),
]

PROGRAMS = [
    ("C006", "Ironwood Long Haul", "Commercial Auto (for-hire trucking)", "Meridian Assurance Group", "Full", 38_500_000, 66.2),
    ("C006", "Ironwood Cargo & Warehouse", "Motor Truck Cargo / Warehouse Legal", "Northgate Specialty Insurance Co.", "Full", 19_700_000, 48.1),
    ("C006", "Last Mile Delivery", "Commercial Auto (last-mile)", "Meridian Assurance Group", "Limited", 14_200_000, 71.5),
    ("C007", "Main Street Business Owners", "Businessowners", "Lakeshore Mutual (direct)", "Full", 142_000_000, 58.4),
    ("C007", "Dairyland Farm", "Farmowners", "Lakeshore Mutual (direct)", "Full", 104_000_000, 63.9),
    ("C007", "Great Lakes Contractors", "Contractors Package", "Lakeshore Mutual (direct)", "Full", 70_000_000, 55.2),
    ("C008", "Single-Parent Captives", "Captive management", "Fronting carriers (various)", "None", 296_000_000, None),
    ("C008", "Group & Cell Captives", "Captive management", "Fronting carriers (various)", "None", 186_000_000, None),
    ("C009", "Commercial Auto Claims", "Claims administration", "Multiple carriers", "None", None, None),
    ("C009", "Workers Compensation Claims", "Claims administration", "Multiple carriers", "None", None, None),
    ("C010", "Agency Premium Finance", "Commercial premium finance", "n/a", "None", None, None),
    ("C011", "Embedded BOP", "Businessowners (embedded)", "Sentinel Cyber Assurance Co.", "Full", 31_400_000, 52.7),
    ("C011", "Small Business Cyber", "Cyber Liability", "Sentinel Cyber Assurance Co.", "Limited", 12_700_000, 38.9),
    ("C012", "Pacific Property", "E&S Commercial Property", "Multiple E&S markets", "Limited", 92_000_000, 46.8),
    ("C012", "Northwest Construction", "E&S Construction GL", "Multiple E&S markets", "Referral", 73_000_000, 57.4),
]

LOSS_RUNS = [
    ("C006", 2023, 57_000_000, 38_200_000, 2140, 14),
    ("C006", 2024, 62_500_000, 41_000_000, 2290, 16),
    ("C006", 2025, 68_100_000, 43_900_000, 2405, 13),
    ("C007", 2023, 281_000_000, 171_400_000, 9820, 27),
    ("C007", 2024, 294_000_000, 172_900_000, 9910, 24),
    ("C007", 2025, 309_000_000, 177_300_000, 10_040, 22),
    ("C011", 2023, 14_900_000, 7_200_000, 610, 2),
    ("C011", 2024, 24_800_000, 11_900_000, 1_020, 3),
    ("C011", 2025, 38_600_000, 18_100_000, 1_540, 4),
    ("C012", 2023, 121_000_000, 60_900_000, 880, 9),
    ("C012", 2024, 139_000_000, 70_300_000, 960, 11),
    ("C012", 2025, 156_000_000, 79_100_000, 1_030, 10),
]

CARRIER_RELATIONSHIPS = [
    ("C006", "Meridian Assurance Group", "A-", 2013, 72.8, "2027-12-31"),
    ("C006", "Northgate Specialty Insurance Co.", "A+", 2016, 27.2, "2028-06-30"),
    ("C007", "Harrow Mutual Re (quota share)", "A-", 2002, 45.0, "2027-01-01"),
    ("C007", "Coastline Re SE (cat XOL)", "A", 2008, 35.0, "2027-06-01"),
    ("C007", "Atlas Peak Reinsurance Ltd. (per-risk)", "A+", 2015, 20.0, "2027-01-01"),
    ("C008", "Green Mountain Fronting Co. (fictional)", "A", 2008, 55.0, "2027-12-31"),
    ("C008", "Keel Executive Risk Insurance Co.", "A-", 2014, 45.0, "2027-12-31"),
    ("C009", "Granite Shield Casualty Co.", "A", 2009, 38.0, "2027-12-31"),
    ("C009", "Meridian Assurance Group", "A-", 2012, 34.0, "2027-12-31"),
    ("C009", "Northgate Specialty Insurance Co.", "A+", 2017, 28.0, "2027-12-31"),
    ("C011", "Sentinel Cyber Assurance Co.", "A", 2020, 100.0, "2028-09-30"),
    ("C012", "Ironbridge Excess & Surplus Co.", "A", 2011, 41.0, "2027-12-31"),
    ("C012", "Lonestar Surplus Lines Co.", "A-", 2014, 33.0, "2027-12-31"),
    ("C012", "Other E&S markets (9)", "A- or better", 2010, 26.0, None),
]

OWNERSHIP = [
    ("C006", "Blue Harbor Equity Partners II, L.P.", 60.0, 1),
    ("C006", "Founding partners", 40.0, 0),
    ("C007", "Policyholders (mutual)", 100.0, 0),
    ("C008", "Owen Whitcomb", 70.0, 0),
    ("C008", "Senior managers (3)", 30.0, 0),
    ("C009", "Kowalski Holdings, LLC", 64.0, 0),
    ("C009", "Employee stock plan", 36.0, 0),
    ("C010", "Hendrickson Family Trust", 75.0, 0),
    ("C010", "Management", 25.0, 0),
    ("C011", "Riverbend Growth Fund IV, L.P.", 48.0, 1),
    ("C011", "Founders", 39.0, 0),
    ("C011", "Employee option pool", 13.0, 0),
    ("C012", "Megan O'Rourke", 58.0, 0),
    ("C012", "Partner brokers (4)", 42.0, 0),
]

DD_ASSESSMENTS = [
    ("C006", 3.9, 3.8, 3.6, 4.1, 3.7, "Moderate", "J. Carter", "2026-11-20",
     "Auto-heavy transportation MGA. Loss trend improving, but long-haul book carries large-verdict exposure."),
    ("C007", 4.2, 4.1, 4.0, 4.4, 3.9, "Low", "S. Patel", "2026-11-20",
     "Century-old regional mutual with strong surplus and a well-structured reinsurance program."),
    ("C008", 4.0, 4.2, 3.9, 4.5, 3.8, "Low", "M. Alvarez", "2026-11-20",
     "Experienced captive manager with clean regulator exams; key-person dependency on the founder."),
    ("C009", 3.8, 3.7, 4.2, 4.0, 3.6, "Moderate", "J. Carter", "2026-11-21",
     "Established TPA with good closing ratios; open litigation status needs confirmation."),
    ("C010", 3.9, 3.6, 3.5, 4.0, 3.4, "Moderate", "S. Patel", "2026-11-21",
     "Profitable premium finance lender with low defaults; no extracted documents received yet."),
    ("C011", 3.2, 3.4, 3.3, 3.7, 4.4, "Elevated", "M. Alvarez", "2026-11-21",
     "Fast-growing insurtech, just reached profitability; strong security posture, thin operating history."),
    ("C012", 4.1, 3.9, 4.0, 4.3, 3.8, "Low", "J. Carter", "2026-11-21",
     "Steady surplus lines wholesaler with diversified markets and current licensing."),
]


# ------------------------------------------------------------------ extracted JSON (C010 has none)
EXTRACTED = {}

_r6 = "IWSU_Reviewed_Financials_2025.pdf"
EXTRACTED["C006"] = {
    "client_id": "C006", "client_name": "Ironwood Specialty Underwriters, LLC",
    "extracted_at": "2026-11-20T09:10:00Z",
    "source_documents": [_r6, "IWSU_Meridian_Program_Agreement.pdf", "IWSU_Fleet_Safety_Manual.pdf",
                         "IWSU_Loss_Runs_2023-2025.xlsx"],
    "applicant": {
        "legal_name": v("Ironwood Specialty Underwriters, LLC", 0.97, f"{_r6}#p1"),
        "fein": v("00-0000006", 0.95, f"{_r6}#p1"),
        "entity_type": v("LLC", 0.93),
        "date_formed": v("April 2, 2012", 0.92, f"{_r6}#p2"),
        "state_of_domicile": v("Georgia", 0.95),
    },
    "mailing": {
        "street": v("3350 Peachtree Road NE, Suite 1500", 0.96),
        "city": v("Atlanta", 0.98), "state": v("Georgia", 0.97), "zip": v("30326", 0.97),
    },
    "contact": {
        "name": v("Marcus Delaney", 0.96), "title": v("President", 0.94),
        "phone": v("404-555-0112", 0.95), "email": v("mdelaney@ironwood-su.example", 0.95),
    },
    "program": {
        # CONFLICT: document says $72.9M, database 72,400,000 -> Review, document value kept
        "gross_written_premium": v("$72.9M", 0.88, f"{_r6}#p5"),
        "lines_of_business": v("For-hire trucking, motor truck cargo, warehouse legal, last-mile delivery", 0.9),
        "binding_authority": v("Full", 0.9, "IWSU_Meridian_Program_Agreement.pdf#p4"),
        "three_year_loss_ratio": v("62.1%", 0.89, "IWSU_Loss_Runs_2023-2025.xlsx#Summary"),
        "telematics_required": v("Yes", 0.91, "IWSU_Fleet_Safety_Manual.pdf#p2"),
    },
    "controls": {
        "uses_tpa": v("Yes", 0.9), "regulatory_action": v("No", 0.92), "cyber_coverage": v("Yes", 0.93),
    },
    "risk_findings": [
        {"area": "Large verdicts", "rating": "High", "finding": "Long-haul trucking exposed to nuclear verdicts",
         "confidence": 0.84},
    ],
}

_r7 = "LMCC_Annual_Statement_2025.pdf"
EXTRACTED["C007"] = {
    "client_id": "C007", "client_name": "Lakeshore Mutual Casualty Company",
    "extracted_at": "2026-11-20T09:25:00Z",
    "source_documents": [_r7, "LMCC_AM_Best_Report_2026.pdf", "LMCC_Reinsurance_Program_2026.pdf"],
    "cedent": {
        "cedent_name": v("Lakeshore Mutual Casualty Company", 0.98, f"{_r7}#p1"),
        "naic_code": v("99047", 0.95, f"{_r7}#p1"),
        "date_incorporated": v("March 15, 1921", 0.9, f"{_r7}#p1"),
        "state_of_domicile": v("Wisconsin", 0.96),
    },
    "home_office": {
        "street": v("PO Box 2210", 0.94), "city": v("Milwaukee", 0.98),
        "state": v("WI", 0.98), "zip": v("53201", 0.96),
    },
    "reinsurance_contact": {
        "name": v("Karen Lindqvist", 0.95), "title": v("VP, Reinsurance", 0.94),
        "phone": v("414.555.0151", 0.94), "email": v("klindqvist@lakeshoremutual.example", 0.95),
    },
    "statutory": {
        "direct_written_premium": v("$316,000,000", 0.93, f"{_r7}#p4"),
        # MISSING IN DOCUMENT: surplus page not extracted -> database value is used
        "policyholder_surplus": v(None, 0.0),
        "combined_ratio": v("97.9%", 0.92, f"{_r7}#p5"),
    },
    "rating": {
        "am_best_rating": v("A", 0.96, "LMCC_AM_Best_Report_2026.pdf#p1"),
        "rating_outlook": v("Positive", 0.9, "LMCC_AM_Best_Report_2026.pdf#p1"),
    },
    "reinsurance": {
        # LOW CONFIDENCE: 0.69 -> Review
        "cat_retention": v("$10,000,000", 0.69, "LMCC_Reinsurance_Program_2026.pdf#p3"),
        "uses_catastrophe_modeling": v("Yes", 0.93),
        "reinsurance_in_place": v("Yes", 0.97),
    },
}

_r8 = "GPCM_Firm_Profile_2026.pdf"
EXTRACTED["C008"] = {
    "client_id": "C008", "client_name": "Granite Peak Captive Managers, Inc.",
    "extracted_at": "2026-11-20T09:40:00Z",
    "source_documents": [_r8, "GPCM_VT_Regulator_Exam_Letter.pdf", "GPCM_Audited_Financials_2025.pdf"],
    "firm": {
        "firm_name": v("Granite Peak Captive Managers, Inc.", 0.97, f"{_r8}#p1"),
        "fein": v("00-0000008", 0.95),
        "date_founded": v("08/21/2006", 0.93, f"{_r8}#p1"),
        "ownership_structure": v("Privately Held", 0.9),
    },
    "office": {
        "street": v("100 Bank Street, Suite 610", 0.96), "city": v("Burlington", 0.98),
        "state": v("Vermont", 0.97), "zip": v("05401", 0.96),
    },
    "principal": {
        "name": v("Owen Whitcomb", 0.96), "title": v("Managing Director", 0.94),
        "phone": v("(802) 555-0176", 0.95), "email": v("owhitcomb@granitepeak-captives.example", 0.95),
    },
    "practice": {
        "captives_under_management": v("37", 0.92, f"{_r8}#p3"),
        "premium_under_management": v("$482M", 0.9, f"{_r8}#p3"),
        # MISSING: question asked, no answer in the documents
        "domiciles_served": v(None, 0.0),
        "manager_type": v("Independent", 0.91),
        "annual_independent_audit": v("Yes", 0.93, "GPCM_Audited_Financials_2025.pdf#p1"),
    },
    "financials": {"annual_revenue": v("$9.3M", 0.92, "GPCM_Audited_Financials_2025.pdf#p4")},
    "insurance": {"eo_limit": v("$5,000,000", 0.93), "cyber_coverage": v("Yes", 0.9)},
    "compliance": {"regulatory_action": v("No", 0.94, "GPCM_VT_Regulator_Exam_Letter.pdf#p2")},
}

_r9 = "CCS_TPA_Profile_2026.pdf"
EXTRACTED["C009"] = {
    "client_id": "C009", "client_name": "Crestline Claims Services, Inc.",
    "extracted_at": "2026-11-20T10:05:00Z",
    "source_documents": [_r9, "CCS_Claims_Audit_2025.pdf", "CCS_Financial_Statements_2025.pdf"],
    "company": {
        "legal_name": v("Crestline Claims Services, Inc.", 0.97, f"{_r9}#p1"),
        "fein": v("00-0000009", 0.94),
        "date_established": v("October 5, 1998", 0.93),
    },
    "address": {
        "street": v("250 West Street, Floor 4", 0.96), "city": v("Columbus", 0.98),
        "state": v("Ohio", 0.97), "zip": v("43215", 0.97),
    },
    "claims_contact": {
        "name": v("Dana Kowalski", 0.96), "title": v("VP, Claims Operations", 0.94),
        "phone": v("614-555-0188", 0.95), "email": v("dkowalski@crestline-claims.example", 0.95),
    },
    "operations": {
        "annual_revenue": v("$44.9 million", 0.92, "CCS_Financial_Statements_2025.pdf#p3"),
        "claims_handled_annually": v("31,800", 0.9, f"{_r9}#p2"),
        # APPROXIMATE -> Review
        "average_days_to_close": v("approx 38", 0.86, "CCS_Claims_Audit_2025.pdf#p6"),
        "licensed_adjusters": v("142", 0.91),
        "claims_system": v("ClaimPoint 7 (fictional)", 0.88),
        "litigation_management_guidelines": v("Yes", 0.9),
        "service_model": v("Full Service", 0.9),
        "primary_line_handled": v("Workers Compensation", 0.89),
    },
    "legal": {
        # AMBIGUOUS YES/NO: "N/A" -> not guessed
        "pending_litigation": v("N/A", 0.74, "CCS_Claims_Audit_2025.pdf#p9"),
        "eo_limit": v("$15,000,000", 0.94), "cyber_coverage": v("Yes", 0.92),
    },
}

_r11 = "BPDI_Investor_Update_Q3_2026.pdf"
EXTRACTED["C011"] = {
    "client_id": "C011", "client_name": "BrightPath Digital Insurance Agency, Inc.",
    "extracted_at": "2026-11-20T10:30:00Z",
    "source_documents": [_r11, "BPDI_SOC2_Type_II_2026.pdf", "BPDI_Sentinel_MGA_Agreement.pdf"],
    "company": {
        "company_name": v("BrightPath Digital Insurance Agency, Inc.", 0.97, f"{_r11}#p1"),
        "fein": v("00-0000011", 0.93), "entity_type": v("Corporation", 0.95),
    },
    "hq": {
        "street": v("500 West 2nd Street, Suite 1900", 0.95), "city": v("Austin", 0.98),
        "state": v("Texas", 0.97), "zip": v("78701", 0.97),
    },
    "contact": {
        "name": v("Priya Raman", 0.97), "title": v("Co-Founder & CEO", 0.95),
        "phone": v("512 555 0161", 0.94), "email": v("Priya@BrightPath-Insure.example", 0.95),
    },
    "metrics": {
        # LOW CONFIDENCE: figure read from a chart -> Review
        "written_premium": v("$44.1M", 0.72, f"{_r11}#p4"),
        "revenue": v("$10.1M", 0.9, f"{_r11}#p4"),
        "active_policy_count": v("27,450", 0.91, f"{_r11}#p5"),
        "binding_authority": v("Full", 0.9, "BPDI_Sentinel_MGA_Agreement.pdf#p6"),
    },
    "security": {
        "soc2_type_ii_report": v("Yes", 0.97, "BPDI_SOC2_Type_II_2026.pdf#p1"),
        "mfa_enforced": v("Yes", 0.95, "BPDI_SOC2_Type_II_2026.pdf#p11"),
        "cyber_coverage_in_force": v("Yes", 0.93),
    },
    "compliance": {"regulatory_action": v("No", 0.9)},
}

_r12 = "CSLB_Firm_Profile_2026.pdf"
EXTRACTED["C012"] = {
    "client_id": "C012", "client_name": "Cascade Surplus Lines Brokerage, LLC",
    "extracted_at": "2026-11-20T10:55:00Z",
    "source_documents": [_r12, "CSLB_WA_SL_License.pdf", "CSLB_EO_Declarations_2026.pdf"],
    "firm": {
        "legal_name": v("Cascade Surplus Lines Brokerage, LLC", 0.98, f"{_r12}#p1"),
        "fein": v("00-0000012", 0.95), "date_established": v("2010-06-01", 0.95),
        "website": v("www.cascade-sl.example", 0.92),
    },
    "address": {
        "street": v("1201 Third Avenue, Suite 3400", 0.96), "city": v("Seattle", 0.98),
        "state": v("WA", 0.98), "zip": v("98101", 0.97),
    },
    "contact": {
        "name": v("Megan O'Rourke", 0.96), "title": v("Principal Broker", 0.95),
        "phone": v("206-555-0171", 0.95), "email": v("morourke@cascade-sl.example", 0.96),
    },
    "licensing": {
        "surplus_lines_license_number": v("MOCK-WA-SL-118204", 0.96, "CSLB_WA_SL_License.pdf#p1"),
        "license_expiration_date": v("May 31, 2027", 0.94),
        "number_of_states_licensed": v("11", 0.9),
        "resident_state": v("Washington", 0.96),
        "prior_license_revocation": v("No", 0.93),
        "market_access": v("Non-admitted", 0.9),
    },
    "production": {"premium_placed": v("$165M", 0.92, f"{_r12}#p2")},
    "insurance": {"eo_limit": v("$5,000,000", 0.95, "CSLB_EO_Declarations_2026.pdf#p1"),
                  "cyber_coverage": v("Yes", 0.92)},
}
