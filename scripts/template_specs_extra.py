"""Seven more demo templates (C006 to C012), each with its own field-naming convention."""

T = "text"; D = "date"; CB = "checkbox"; RB = "radio"; DD = "dropdown"; SIG = "signature"

AM_BEST = ["A++", "A+", "A", "A-", "B++", "B+", "B", "NR"]
ENTITY_TYPES = ["Limited Liability Company", "Corporation", "Partnership", "Mutual Company",
                "Reciprocal Exchange"]
STATES_WEST = ["AZ", "CA", "CO", "ID", "MT", "NV", "OR", "UT", "WA", "WY"]
LINES_HANDLED = ["Commercial Auto", "General Liability", "Workers Compensation", "Property", "Multi-line"]
OWNERSHIP_TYPES = ["Privately Held", "Private Equity Backed", "ESOP", "Publicly Traded"]


def f(name, label, typ=T, span=6, options=None, maxlen=None):
    return (name, label, typ, span, options or [], maxlen)


TEMPLATES = [
    {   # dotted names: applicant.legal_name
        "template_id": "tpl-c006", "client_id": "C006",
        "name": "Transportation Program Due Diligence Questionnaire",
        "file": "templates/C006_Transportation_Program_Due_Diligence_Questionnaire.pdf",
        "issuer": "Meridian Assurance Group", "form_no": "MAG-TRN-DDQ  Rev. 07/2026",
        "intro": "For program administrators writing trucking, cargo or delivery business on Meridian paper. "
                 "Attach loss runs and the current fleet safety manual.",
        "color": (0.137, 0.208, 0.290), "accent": (0.851, 0.392, 0.180), "style": "rail",
        "sections": [
            ("Applicant", [
                f("applicant.legal_name", "Applicant Legal Name", T, 8),
                f("applicant.fein", "FEIN", T, 4),
                f("applicant.entity_type", "Entity Type", DD, 5, ENTITY_TYPES),
                f("applicant.date_formed", "Date Formed", D, 4),
                f("applicant.domicile", "State of Domicile", T, 3, maxlen=2),
            ]),
            ("Mailing Address", [
                f("mailing.street", "Mailing Street", T, 12),
                f("mailing.city", "Mailing City", T, 6),
                f("mailing.state", "Mailing State", T, 2, maxlen=2),
                f("mailing.zip", "Mailing ZIP", T, 4, maxlen=10),
            ]),
            ("Program Contact", [
                f("contact.name", "Contact Name", T, 6),
                f("contact.title", "Contact Title", T, 6),
                f("contact.phone", "Contact Phone", T, 5),
                f("contact.email", "Contact Email", T, 7),
            ]),
            ("Program Profile", [
                f("program.gwp", "Gross Written Premium", T, 6),
                f("program.loss_ratio_3yr", "Three Year Loss Ratio", T, 6),
                f("program.lines", "Lines of Business", T, 12),
                f("program.authority", "Binding Authority", RB, 12, ["Full", "Limited", "Referral Only"]),
                f("controls.telematics", "Telematics Required for Insureds", CB, 6),
                f("controls.tpa", "Uses a Third Party Administrator (TPA)", CB, 6),
                f("controls.regulatory", "Regulatory Action in Last 5 Years", CB, 6),
                f("controls.cyber", "Cyber Coverage in Force", CB, 6),
            ]),
            ("Attestation", [f("attest.signature", "Authorized Signature", SIG, 12)]),
        ],
    },
    {   # ALL CAPS snake case: CEDENT_NAME
        "template_id": "tpl-c007", "client_id": "C007",
        "name": "Reinsurance Cedent Information Form",
        "file": "templates/C007_Reinsurance_Cedent_Information_Form.pdf",
        "issuer": "Harrow Mutual Re", "form_no": "HMR-CED-01  2027 Renewal",
        "intro": "Cedent information for the 1/1 treaty renewal. Statutory figures from the latest annual "
                 "statement; catastrophe figures from the current reinsurance program.",
        "color": (0.208, 0.263, 0.357), "accent": (0.420, 0.655, 0.769), "style": "band",
        "sections": [
            ("Cedent", [
                f("CEDENT_NAME", "Cedent Name", T, 8),
                f("NAIC_CODE", "NAIC Company Code", T, 4),
                f("DATE_INCORPORATED", "Date Incorporated", D, 4),
                f("STATE_OF_DOMICILE", "State of Domicile", T, 3, maxlen=2),
                f("AM_BEST_RATING", "AM Best Rating", DD, 5, AM_BEST),
            ]),
            ("Home Office", [
                f("STREET", "Street Address", T, 12),
                f("CITY", "City", T, 6),
                f("STATE", "State", T, 2, maxlen=2),
                f("ZIP", "Zip Code", T, 4, maxlen=10),
            ]),
            ("Reinsurance Contact", [
                f("CONTACT_NAME", "Contact Name", T, 6),
                f("CONTACT_TITLE", "Contact Title", T, 6),
                f("CONTACT_PHONE", "Contact Phone", T, 5),
                f("CONTACT_EMAIL", "Contact Email", T, 7),
            ]),
            ("Financial and Catastrophe Profile", [
                f("DIRECT_WRITTEN_PREMIUM", "Direct Written Premium", T, 6),
                f("POLICYHOLDER_SURPLUS", "Policyholder Surplus", T, 6),
                f("COMBINED_RATIO", "Combined Ratio", T, 4),
                f("CAT_RETENTION", "Catastrophe Retention per Occurrence", T, 8),
                f("RATING_OUTLOOK", "Rating Outlook", RB, 12, ["Positive", "Stable", "Negative"]),
                f("USES_CAT_MODELING", "Uses Catastrophe Modeling", CB, 6),
                f("REINSURANCE_IN_PLACE", "Reinsurance Program in Place", CB, 6),
            ]),
            ("Certification", [f("OFFICER_SIGNATURE", "Officer Signature", SIG, 12)]),
        ],
    },
    {   # kebab case: manager-legal-name
        "template_id": "tpl-c008", "client_id": "C008",
        "name": "Captive Manager Qualification Questionnaire",
        "file": "templates/C008_Captive_Manager_Qualification_Questionnaire.pdf",
        "issuer": "Green Mountain Fronting Co.", "form_no": "GMF-CMQ  Ed. 2026",
        "intro": "Qualification review for captive managers servicing fronted programs. One questionnaire per "
                 "management firm.",
        "color": (0.153, 0.341, 0.267), "accent": (0.784, 0.659, 0.341), "style": "boxed",
        "sections": [
            ("1. Firm", [
                f("manager-legal-name", "Manager Legal Name", T, 8),
                f("fein", "FEIN", T, 4),
                f("date-founded", "Date Founded", D, 4),
                f("ownership-structure", "Ownership Structure", DD, 8, OWNERSHIP_TYPES),
            ]),
            ("2. Office", [
                f("office-street", "Street Address", T, 12),
                f("office-city", "City", T, 6),
                f("office-state", "State", T, 2, maxlen=2),
                f("office-zip", "Zip Code", T, 4, maxlen=10),
            ]),
            ("3. Principal", [
                f("principal-name", "Principal Contact Name", T, 6),
                f("principal-title", "Principal Contact Title", T, 6),
                f("principal-phone", "Principal Contact Phone", T, 5),
                f("principal-email", "Principal Contact Email", T, 7),
            ]),
            ("4. Practice", [
                f("captives-under-management", "Captives Under Management", T, 4),
                f("premium-under-management", "Premium Under Management", T, 4),
                f("annual-revenue", "Annual Revenue", T, 4),
                f("domiciles-served", "Domiciles Served", T, 8),
                f("eo-limit", "E&O Limit", T, 4),
                f("manager-type", "Manager Type", RB, 12, ["Independent", "Broker-affiliated", "Insurer-affiliated"]),
                f("independent-audit", "Annual Independent Audit", CB, 4),
                f("regulatory-action", "Regulatory Action in Last 5 Years", CB, 4),
                f("cyber-coverage", "Cyber Coverage in Force", CB, 4),
            ]),
            ("5. Sign-off", [f("authorized-signature", "Authorized Signature", SIG, 12)]),
        ],
    },
    {   # Title Case with colon: "Legal Name:"
        "template_id": "tpl-c009", "client_id": "C009",
        "name": "TPA Claims Audit Pre-Visit Questionnaire",
        "file": "templates/C009_TPA_Claims_Audit_Pre_Visit_Questionnaire.pdf",
        "issuer": "Granite Shield Casualty Co.", "form_no": "GSC-TPA-PV  Rev. 09/2026",
        "intro": "Complete before the on-site claims audit. Figures cover the last twelve months unless noted.",
        "color": (0.290, 0.180, 0.420), "accent": (0.737, 0.616, 0.851), "style": "rail",
        "sections": [
            ("Administrator", [
                f("Legal Name:", "Legal Name", T, 8),
                f("FEIN:", "FEIN", T, 4),
                f("Date Established:", "Date Established", D, 4),
                f("Annual Revenue:", "Annual Revenue", T, 4),
                f("E&O Limit:", "E&O Limit", T, 4),
            ]),
            ("Address", [
                f("Address:", "Address", T, 12),
                f("City:", "City", T, 6),
                f("State:", "State", T, 2, maxlen=2),
                f("ZIP:", "ZIP", T, 4, maxlen=10),
            ]),
            ("Claims Contact", [
                f("Claims Contact:", "Claims Contact", T, 6),
                f("Title:", "Title", T, 6),
                f("Phone:", "Phone", T, 5),
                f("Email:", "Email", T, 7),
            ]),
            ("Claims Operations", [
                f("Claims Handled Annually:", "Claims Handled Annually", T, 4),
                f("Average Days to Close:", "Average Days to Close", T, 4),
                f("Licensed Adjusters:", "Licensed Adjusters", T, 4),
                f("Claims System:", "Claims System", T, 6),
                f("Primary Line Handled:", "Primary Line Handled", DD, 6, LINES_HANDLED),
                f("Service Model:", "Service Model", RB, 12, ["Full Service", "Claims Only", "Program-dedicated"]),
                f("Litigation Management Guidelines:", "Uses Litigation Management Guidelines", CB, 4),
                f("Pending Litigation:", "Pending Litigation", CB, 4),
                f("Cyber Coverage:", "Cyber Coverage", CB, 4),
            ]),
            ("Auditor Use", [f("Auditor Signature:", "Auditor Signature", SIG, 12)]),
        ],
    },
    {   # camelCase: legalEntityName (database-only company)
        "template_id": "tpl-c010", "client_id": "C010",
        "name": "Premium Finance Partner Application",
        "file": "templates/C010_Premium_Finance_Partner_Application.pdf",
        "issuer": "Northgate Specialty Insurance Co.", "form_no": "NSI-PFA-03  (2026)",
        "intro": "Application to be approved as a premium finance partner for Northgate policies.",
        "color": (0.098, 0.306, 0.471), "accent": (0.937, 0.733, 0.271), "style": "band",
        "sections": [
            ("Company", [
                f("legalEntityName", "Legal Entity Name", T, 8),
                f("federalTaxId", "Federal Tax ID", T, 4),
                f("dateOfIncorporation", "Date of Incorporation", D, 4),
                f("stateOfIncorporation", "State of Incorporation", T, 4, maxlen=2),
                f("ownershipStructure", "Ownership Structure", DD, 4, OWNERSHIP_TYPES),
            ]),
            ("Address", [
                f("streetAddress", "Street Address", T, 12),
                f("city", "City", T, 6),
                f("state", "State", T, 2, maxlen=2),
                f("zipCode", "Zip Code", T, 4, maxlen=10),
            ]),
            ("Primary Contact", [
                f("primaryContactName", "Primary Contact Name", T, 6),
                f("primaryContactTitle", "Primary Contact Title", T, 6),
                f("primaryContactPhone", "Primary Contact Phone", T, 5),
                f("primaryContactEmail", "Primary Contact Email", T, 7),
            ]),
            ("Lending Profile", [
                f("annualRevenue", "Annual Revenue", T, 4),
                f("ebitda", "EBITDA", T, 4),
                f("employeeCount", "Employee Count", T, 4),
                f("loansOutstanding", "Loans Outstanding", T, 6),
                f("defaultRate", "Default Rate", T, 6),
                f("entityType", "Entity Type", RB, 12, ["Corporation", "Limited Liability Company", "Partnership"]),
                f("automatedCollections", "Uses Automated Collections", CB, 6),
                f("stateRegulatorConsent", "State Regulator Consent on File", CB, 6),
            ]),
            ("Signature", [f("applicantSignature", "Applicant Signature", SIG, 12)]),
        ],
    },
    {   # Hungarian prefixes: txtCompanyName, chkMFA
        "template_id": "tpl-c011", "client_id": "C011",
        "name": "Insurtech Distribution Partner Review",
        "file": "templates/C011_Insurtech_Distribution_Partner_Review.pdf",
        "issuer": "Sentinel Cyber Assurance Co.", "form_no": "SCA-IDPR  v2.3",
        "intro": "Annual review of digital distribution partners with delegated authority, including "
                 "information security controls.",
        "color": (0.051, 0.176, 0.251), "accent": (0.208, 0.741, 0.639), "style": "boxed",
        "sections": [
            ("Partner", [
                f("txtCompanyName", "Company Name", T, 8),
                f("txtFEIN", "FEIN", T, 4),
                f("ddlEntityType", "Entity Type", DD, 6, ENTITY_TYPES),
                f("txtWebsite", "Website", T, 6),
            ]),
            ("Headquarters", [
                f("txtStreet", "Street", T, 12),
                f("txtCity", "City", T, 6),
                f("txtState", "State", T, 2, maxlen=2),
                f("txtZip", "Zip", T, 4, maxlen=10),
            ]),
            ("Partner Contact", [
                f("txtContactName", "Contact Name", T, 6),
                f("txtContactTitle", "Contact Title", T, 6),
                f("txtContactPhone", "Contact Phone", T, 5),
                f("txtContactEmail", "Contact Email", T, 7),
            ]),
            ("Production and Security", [
                f("curWrittenPremium", "Written Premium", T, 4),
                f("curRevenue", "Revenue", T, 4),
                f("numPoliciesInForce", "Policies in Force", T, 4),
                f("rdoBindingAuthority", "Binding Authority", RB, 12, ["Full", "Limited", "Referral Only"]),
                f("chkSOC2", "SOC 2 Type II Report Available", CB, 6),
                f("chkMFA", "MFA Enforced for All Users", CB, 6),
                f("chkCyber", "Cyber Coverage in Force", CB, 6),
                f("chkRegAction", "Regulatory Action in Last 5 Years", CB, 6),
            ]),
            ("Partner Certification", [f("txtSignature", "Authorized Signature", SIG, 12)]),
        ],
    },
    {   # section-coded names: S1_LegalName
        "template_id": "tpl-c012", "client_id": "C012",
        "name": "Surplus Lines Market Access Questionnaire",
        "file": "templates/C012_Surplus_Lines_Market_Access_Questionnaire.pdf",
        "issuer": "Lonestar Surplus Lines Co.", "form_no": "LSL-MAQ  2026-2027",
        "intro": "Market access questionnaire for wholesale brokers placing business with Lonestar. "
                 "Answer every section; attach the resident surplus lines license.",
        "color": (0.400, 0.157, 0.110), "accent": (0.886, 0.643, 0.388), "style": "band",
        "sections": [
            ("Section 1: Broker", [
                f("S1_LegalName", "Legal Name", T, 8),
                f("S1_FEIN", "FEIN", T, 4),
                f("S1_DateEstablished", "Date Established", D, 4),
                f("S1_Website", "Website", T, 8),
            ]),
            ("Section 2: Address", [
                f("S2_Street", "Street Address", T, 12),
                f("S2_City", "City", T, 6),
                f("S2_State", "State", T, 2, maxlen=2),
                f("S2_Zip", "Zip Code", T, 4, maxlen=10),
            ]),
            ("Section 3: Contact", [
                f("S3_ContactName", "Contact Name", T, 6),
                f("S3_ContactTitle", "Contact Title", T, 6),
                f("S3_ContactPhone", "Contact Phone", T, 5),
                f("S3_ContactEmail", "Contact Email", T, 7),
            ]),
            ("Section 4: Licensing and Production", [
                f("S4_ResidentState", "Resident State", DD, 3, STATES_WEST),
                f("S4_SLLicenseNumber", "Surplus Lines License Number", T, 5),
                f("S4_LicenseExpiration", "License Expiration Date", D, 4),
                f("S4_StatesLicensed", "Number of States Licensed", T, 4),
                f("S4_PremiumPlaced", "Premium Placed", T, 4),
                f("S4_EOLimit", "E&O Limit", T, 4),
                f("S4_MarketAccess", "Market Access", RB, 12, ["Admitted", "Non-admitted", "Both"]),
                f("S4_PriorRevocation", "Any Prior License Revocation", CB, 6),
                f("S4_CyberCoverage", "Cyber Coverage in Force", CB, 6),
            ]),
            ("Section 5: Attestation", [f("S5_Signature", "Authorized Signature", SIG, 12)]),
        ],
    },
]


# ---------------------------------------------------------------------------
# Two companies onboarded BEFORE their data: template registered, no JSON and no
# database rows yet. Fill form must say "No data found" instead of guessing.
# ---------------------------------------------------------------------------
CARGO_TYPES = ["Hull & Machinery", "Marine Cargo", "Inland Marine", "Marine Liability", "Multi-line Marine"]
CROP_STATES = ["IA", "IL", "IN", "KS", "MN", "MO", "NE", "ND", "SD", "WI"]

NO_DATA_TEMPLATES = [
    {   # PascalCase names
        "template_id": "tpl-c013", "client_id": "C013", "company_name": "Harborline Marine Underwriters, LLC",
        "name": "Marine Program Onboarding Questionnaire",
        "file": "templates/C013_Marine_Program_Onboarding_Questionnaire.pdf",
        "issuer": "Keel Marine Insurance Co.", "form_no": "KMI-MPO  Ed. 11/2026",
        "intro": "Onboarding questionnaire for marine program administrators. Vessel schedules and cargo "
                 "loss history are requested separately.",
        "color": (0.039, 0.239, 0.384), "accent": (0.212, 0.612, 0.718), "style": "band",
        "sections": [
            ("Applicant", [
                f("ApplicantLegalName", "Applicant Legal Name", T, 8),
                f("FEIN", "FEIN", T, 4),
                f("DateEstablished", "Date Established", D, 4),
                f("StateOfDomicile", "State of Domicile", T, 3, maxlen=2),
                f("EntityType", "Entity Type", DD, 5, ENTITY_TYPES),
            ]),
            ("Mailing Address", [
                f("MailingStreet", "Mailing Street", T, 12),
                f("MailingCity", "Mailing City", T, 6),
                f("MailingState", "Mailing State", T, 2, maxlen=2),
                f("MailingZip", "Mailing ZIP", T, 4, maxlen=10),
            ]),
            ("Primary Contact", [
                f("PrimaryContactName", "Primary Contact Name", T, 6),
                f("PrimaryContactTitle", "Primary Contact Title", T, 6),
                f("PrimaryContactPhone", "Primary Contact Phone", T, 5),
                f("PrimaryContactEmail", "Primary Contact Email", T, 7),
            ]),
            ("Marine Program", [
                f("GrossWrittenPremium", "Gross Written Premium", T, 6),
                f("PrimaryMarineLine", "Primary Marine Line", DD, 6, CARGO_TYPES),
                f("BindingAuthority", "Binding Authority", RB, 12, ["Full", "Limited", "Referral Only"]),
                f("UsesTPA", "Uses a Third Party Administrator (TPA)", CB, 6),
                f("RegulatoryAction", "Regulatory Action in Last 5 Years", CB, 6),
                f("CyberCoverage", "Cyber Coverage in Force", CB, 6),
            ]),
            ("Attestation", [f("AuthorizedSignature", "Authorized Signature", SIG, 12)]),
        ],
    },
    {   # Sentence-case labels as names
        "template_id": "tpl-c014", "client_id": "C014", "company_name": "Prairie Ag Risk Services, Inc.",
        "name": "Crop and Agribusiness Agency Appointment Form",
        "file": "templates/C014_Crop_and_Agribusiness_Agency_Appointment_Form.pdf",
        "issuer": "Heartland Farm Mutual", "form_no": "HFM-AGA-02  2027 Crop Year",
        "intro": "Agency appointment for crop and agribusiness producers. Complete before the 2027 sales "
                 "closing date.",
        "color": (0.290, 0.369, 0.153), "accent": (0.871, 0.690, 0.231), "style": "boxed",
        "sections": [
            ("1. Agency", [
                f("Agency legal name", "Agency Legal Name", T, 8),
                f("Federal employer ID", "FEIN", T, 4),
                f("Date founded", "Date Founded", D, 4),
                f("Agency website", "Website", T, 8),
            ]),
            ("2. Address", [
                f("Street address", "Street Address", T, 12),
                f("City", "City", T, 6),
                f("State", "State", T, 2, maxlen=2),
                f("Zip code", "Zip Code", T, 4, maxlen=10),
            ]),
            ("3. Principal", [
                f("Principal name", "Principal Contact Name", T, 6),
                f("Principal title", "Principal Contact Title", T, 6),
                f("Principal phone", "Principal Contact Phone", T, 5),
                f("Principal email", "Principal Contact Email", T, 7),
            ]),
            ("4. Licensing and Book", [
                f("Resident state", "Resident State", DD, 3, CROP_STATES),
                f("Resident license number", "Resident License Number", T, 5),
                f("Annual revenue", "Annual Revenue", T, 4),
                f("Appointment type", "Appointment Type Requested", RB, 12,
                  ["Direct Appointment", "Sub-producer", "Managing General Agency"]),
                f("Prior license revocation", "Any Prior License Revocation", CB, 6),
                f("Cyber coverage", "Cyber Coverage in Force", CB, 6),
            ]),
            ("5. Attestation", [f("Producer signature", "Producer Attestation Signature", SIG, 12)]),
        ],
    },
]
