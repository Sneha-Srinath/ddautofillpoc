"""Layout specs for the five demo fillable-PDF templates.

Each template uses a different naming style for similar data so the demo shows
auto-matching across naming conventions. Issuers are fictional.

Field tuple: (pdf_field_name, tooltip/label, type, span_of_12, options, maxlen)
type: text | date | checkbox | radio | dropdown | signature
"""

T = "text"; D = "date"; CB = "checkbox"; RB = "radio"; DD = "dropdown"; SIG = "signature"

AM_BEST = ["A++", "A+", "A", "A-", "B++", "B+", "B", "NR"]
ENTITY_TYPES = ["Limited Liability Company", "Corporation", "Partnership", "Mutual Company",
                "Reciprocal Exchange"]
US_STATES_SHORT = ["AL", "AZ", "CA", "CO", "FL", "GA", "LA", "MS", "NC", "NM", "NY", "OK", "PA", "TX"]


def f(name, label, typ=T, span=6, options=None, maxlen=None):
    return (name, label, typ, span, options or [], maxlen)


TEMPLATES = [
    {
        "template_id": "tpl-harborpoint-mga-ddq",
        "client_id": "C001",
        "name": "MGA Due Diligence Questionnaire",
        "file": "templates/C001_MGA_Due_Diligence_Questionnaire.pdf",
        "issuer": "Granite Shield Casualty Co.",
        "form_no": "GSC-MGA-DDQ  Rev. 03/2026",
        "intro": "To be completed by any Managing General Agent requesting or renewing delegated "
                 "underwriting and binding authority. All answers are subject to verification.",
        "color": (0.106, 0.212, 0.365), "accent": (0.788, 0.635, 0.247), "style": "band",
        "sections": [
            ("A. Applicant Information", [
                f("Applicant_Legal_Name", "Applicant Legal Name", T, 8),
                f("FEIN", "FEIN", T, 4),
                f("DBA_Trade_Name", "DBA / Trade Name", T, 6),
                f("Entity_Type", "Entity Type", DD, 6, ENTITY_TYPES),
                f("Date_Established", "Date Established", D, 4),
                f("State_of_Domicile", "State of Domicile", T, 3, maxlen=2),
                f("Website", "Website", T, 5),
            ]),
            ("B. Mailing Address", [
                f("Mailing_Street", "Mailing Street", T, 12),
                f("Mailing_City", "Mailing City", T, 6),
                f("Mailing_State", "Mailing State", T, 2, maxlen=2),
                f("Mailing_ZIP", "Mailing ZIP", T, 4, maxlen=10),
            ]),
            ("C. Primary Contact", [
                f("Primary_Contact_Name", "Primary Contact Name", T, 6),
                f("Primary_Contact_Title", "Primary Contact Title", T, 6),
                f("Primary_Contact_Phone", "Primary Contact Phone", T, 5),
                f("Primary_Contact_Email", "Primary Contact Email", T, 7),
            ]),
            ("D. Program Operations", [
                f("Gross_Written_Premium", "Gross Written Premium (last fiscal year)", T, 6),
                f("Program_Count", "Number of Active Programs", T, 3),
                f("Three_Year_Loss_Ratio", "Three Year Loss Ratio", T, 3),
                f("Lines_of_Business", "Lines of Business Written", T, 12),
                f("EO_Limit", "E&O Limit", T, 6),
                f("Binding_Authority", "Binding Authority", RB, 12, ["Full", "Limited", "Referral Only"]),
                f("Uses_TPA_Yes", "Uses a Third Party Administrator (TPA)", CB, 6),
                f("Regulatory_Action_Yes", "Regulatory Action in Last 5 Years", CB, 6),
                f("Cyber_Coverage_Yes", "Cyber Coverage in Force", CB, 6),
            ]),
            ("E. Attestation", [
                f("Authorized_Signature", "Authorized Signature", SIG, 8),
                f("Date_Signed", "Date Signed", SIG, 4),
            ]),
        ],
    },
    {
        "template_id": "tpl-deltapine-carrier-dd",
        "client_id": "C002",
        "name": "Carrier Partner Due Diligence Form",
        "file": "templates/C002_Carrier_Partner_Due_Diligence_Form.pdf",
        "issuer": "Northgate Specialty Insurance Co.",
        "form_no": "NSI-CP-114  (11/2025)",
        "intro": "Carrier partner onboarding review. Provide statutory figures from the most recent "
                 "annual statement and the current AM Best rating.",
        "color": (0.118, 0.337, 0.192), "accent": (0.553, 0.714, 0.388), "style": "rail",
        "sections": [
            ("Company Profile", [
                f("Insured Name", "Insured Name", T, 8),
                f("NAIC Company Code", "NAIC Company Code", T, 4),
                f("Doing Business As", "Doing Business As", T, 6),
                f("Date of Incorporation", "Date of Incorporation", D, 3),
                f("State of Domicile", "State of Domicile", T, 3, maxlen=2),
            ]),
            ("Home Office", [
                f("Street Address", "Street Address", T, 12),
                f("City", "City", T, 6),
                f("State", "State", T, 2, maxlen=2),
                f("Zip Code", "Zip Code", T, 4, maxlen=10),
            ]),
            ("Partnership Contact", [
                f("Contact Person", "Contact Person", T, 6),
                f("Contact Title", "Contact Title", T, 6),
                f("Telephone", "Telephone", T, 5),
                f("E-mail Address", "E-mail Address", T, 7),
            ]),
            ("Financial Strength", [
                f("Direct Written Premium", "Direct Written Premium", T, 6),
                f("Policyholder Surplus", "Policyholder Surplus", T, 6),
                f("Net Income", "Net Income", T, 6),
                f("Combined Ratio", "Combined Ratio", T, 6),
                f("AM Best Rating", "AM Best Rating", DD, 4, AM_BEST),
                f("Rating Outlook", "Rating Outlook", RB, 8, ["Positive", "Stable", "Negative"]),
                f("Reinsurance Program in Place", "Reinsurance Program in Place", CB, 6),
                f("Uses Catastrophe Modeling", "Uses Catastrophe Modeling", CB, 6),
            ]),
            ("Certification", [
                f("Officer Signature", "Officer Signature", SIG, 12),
            ]),
        ],
    },
    {
        "template_id": "tpl-summitridge-appointment",
        "client_id": "C003",
        "name": "Agency Appointment & Licensing Form",
        "file": "templates/C003_Agency_Appointment_Licensing_Form.pdf",
        "issuer": "Ironbridge Excess & Surplus Co.",
        "form_no": "IES-APPT-07  Ed. 2026",
        "intro": "Complete all sections to request a wholesale appointment. Attach a copy of the "
                 "resident license and current E&O declarations.",
        "color": (0.478, 0.122, 0.169), "accent": (0.851, 0.659, 0.459), "style": "boxed",
        "sections": [
            ("1. Agency Details", [
                f("Name of Agency", "Name of Agency", T, 8),
                f("Federal Employer ID Number (FEIN)", "Federal Employer ID Number (FEIN)", T, 4),
                f("Trade Name (if any)", "Trade Name (if any)", T, 6),
                f("Date Agency Established", "Date Agency Established", D, 3),
                f("Agency Website", "Agency Website", T, 3),
            ]),
            ("2. Mailing Address", [
                f("Mailing Address", "Mailing Address", T, 12),
                f("City (Mailing)", "City (Mailing)", T, 6),
                f("State (Mailing)", "State (Mailing)", T, 2, maxlen=2),
                f("ZIP (Mailing)", "ZIP (Mailing)", T, 4, maxlen=10),
            ]),
            ("3. Principal Contact", [
                f("Principal Contact Name", "Principal Contact Name", T, 6),
                f("Principal Contact Title", "Principal Contact Title", T, 6),
                f("Principal Contact Phone", "Principal Contact Phone", T, 5),
                f("Principal Contact Email", "Principal Contact Email", T, 7),
            ]),
            ("4. Licensing", [
                f("Resident State", "Resident State", DD, 3, US_STATES_SHORT),
                f("Resident License Number", "Resident License Number", T, 4),
                f("License Expiration Date", "License Expiration Date", D, 3),
                f("Number of States Licensed", "Number of States Licensed", T, 2),
                f("Any Prior License Revocation", "Any Prior License Revocation", CB, 6),
                f("Binds Coverage on Behalf of Carriers", "Binds Coverage on Behalf of Carriers", CB, 6),
            ]),
            ("5. Errors & Omissions", [
                f("E&O Carrier", "E&O Carrier", T, 6),
                f("E&O Limit per Claim", "E&O Limit per Claim", T, 3),
                f("E&O Expiration Date", "E&O Expiration Date", D, 3),
                f("Appointment Type Requested", "Appointment Type Requested", RB, 12,
                  ["Direct Appointment", "Sub-producer", "Surplus Lines Only"]),
            ]),
            ("6. Producer Attestation", [
                f("Producer Attestation Signature", "Producer Attestation Signature", SIG, 12),
            ]),
        ],
    },
    {
        "template_id": "tpl-bluewater-counterparty",
        "client_id": "C004",
        "name": "Reinsurance Counterparty Due Diligence Checklist",
        "file": "templates/C004_Reinsurance_Counterparty_Due_Diligence_Checklist.pdf",
        "issuer": "Atlas Peak Reinsurance Ltd.",
        "form_no": "APR-CDD-02  v4.1",
        "intro": "Counterparty know-your-intermediary checklist. Required before any treaty or "
                 "facultative placement is bound through the intermediary.",
        "color": (0.059, 0.361, 0.431), "accent": (0.427, 0.773, 0.769), "style": "band",
        "sections": [
            ("Counterparty", [
                f("EntityName", "Entity Name", T, 8),
                f("FEIN", "FEIN", T, 4),
                f("DateOfFormation", "Date of Formation", D, 4),
                f("YrsInBusiness", "Yrs in Business", T, 3),
                f("FinancialStrengthRating", "Financial Strength Rating", DD, 5, AM_BEST),
            ]),
            ("Office Address", [
                f("StreetAddress", "Street Address", T, 12),
                f("City", "City", T, 6),
                f("StateCode", "State Code", T, 2, maxlen=2),
                f("PostalCode", "Postal Code", T, 4, maxlen=10),
            ]),
            ("Key Contact", [
                f("KeyContactName", "Key Contact Name", T, 6),
                f("KeyContactTitle", "Key Contact Title", T, 6),
                f("KeyContactPhone", "Key Contact Phone", T, 5),
                f("KeyContactEmailAddr", "Key Contact Email Addr", T, 7),
            ]),
            ("Business & Controls", [
                f("AnnualBrokerageRevenue", "Annual Brokerage Revenue", T, 6),
                f("ErrorsOmissionsLimit", "Errors & Omissions Limit", T, 6),
                f("PlacementType", "Placement Type", RB, 12, ["Treaty", "Facultative", "Treaty and Facultative"]),
                f("CollateralRequired", "Collateral Required", CB, 4),
                f("SanctionsScreeningPerformed", "Sanctions Screening Performed", CB, 4),
                f("CyberCoverageInForce", "Cyber Coverage in Force", CB, 4),
            ]),
            ("Sign-off", [
                f("AuthorizedOfficerSignature", "Authorized Officer Signature", SIG, 12),
            ]),
        ],
    },
    {
        "template_id": "tpl-keystone-acquisition-irl",
        "client_id": "C005",
        "name": "Acquisition Due Diligence Information Request",
        "file": "templates/C005_Acquisition_Due_Diligence_Information_Request.pdf",
        "issuer": "Cobalt Harbor Capital Partners",
        "form_no": "CHC-IRL-2026  Confidential",
        "intro": "Information request list for the proposed acquisition of an insurance "
                 "distribution business. Figures are trailing twelve months unless noted.",
        "color": (0.180, 0.227, 0.529), "accent": (0.957, 0.635, 0.380), "style": "rail",
        "sections": [
            ("Company", [
                f("Company", "Company", T, 8),
                f("FEIN", "FEIN", T, 4),
                f("DBA", "DBA", T, 5),
                f("Founded", "Founded", D, 3),
                f("State of Inc.", "State of Inc.", T, 4, maxlen=2),
                f("Ownership", "Ownership", DD, 6, ["Privately Held", "Private Equity Backed", "ESOP",
                                                      "Publicly Traded"]),
                f("Employees", "Employees", T, 6),
            ]),
            ("Address", [
                f("Address", "Address", T, 12),
                f("City", "City", T, 6),
                f("State", "State", T, 2, maxlen=2),
                f("ZIP", "ZIP", T, 4, maxlen=10),
            ]),
            ("Contact", [
                f("Contact", "Contact", T, 6),
                f("Title", "Title", T, 6),
                f("Phone", "Phone", T, 5),
                f("Email", "Email", T, 7),
            ]),
            ("Financials & Book", [
                f("Revenue", "Revenue", T, 4),
                f("EBITDA", "EBITDA", T, 4),
                f("Group Clients", "Group Clients", T, 4),
                f("Top Carrier %", "Top Carrier %", T, 4),
                f("Top 10 Clients %", "Top 10 Clients %", T, 4),
                f("Retention Rate", "Retention Rate", T, 4),
                f("Deal Structure", "Deal Structure", RB, 12, ["Asset Purchase", "Stock Purchase", "Merger"]),
            ]),
            ("Legal & Risk", [
                f("Pending Litigation", "Pending Litigation", CB, 6),
                f("E&O Claims (5 yrs)", "E&O Claims (5 yrs)", CB, 6),
                f("Cyber Coverage", "Cyber Coverage", CB, 6),
                f("Non-Compete Agreements", "Non-Compete Agreements", CB, 6),
            ]),
            ("Seller Certification", [
                f("Seller Signature", "Seller Signature", SIG, 12),
            ]),
        ],
    },
]


from scripts.template_specs_extra import NO_DATA_TEMPLATES, TEMPLATES as _MORE  # noqa: E402

TEMPLATES += _MORE
# Onboarded before their data exists (kept separate so data-driven tests and the report skip them)
ALL_TEMPLATES = TEMPLATES + NO_DATA_TEMPLATES
