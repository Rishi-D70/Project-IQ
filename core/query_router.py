import re
from typing import List, Dict, Any

FIELD_ALIASES = {
    # PARTIES & ENTITIES
    "parties.client": [
        "client", "customer", "buyer", "purchaser", "recipient",
        "second party", "party b", "lessee", "hirer", "tenant",
        "licensee", "franchisee", "distributor", "reseller",
        "end user", "consumer", "subscriber", "member",
        "investor", "shareholder", "stakeholder"
    ],

    "parties.service_provider": [
        "service provider", "vendor", "supplier", "seller",
        "consultant", "contractor", "licensor", "lessor",
        "party a", "first party", "service provider",
        "provider", "freelancer", "agency", "firm",
        "company", "corporation", "business", "enterprise",
        "manufacturer", "producer", "distributor", "retailer",
        "franchisor", "employer", "principal", "owner",
        "landlord", "lender", "creditor"
    ],

    "parties.guarantor": [
        "guarantor", "surety", "co-signer", "co-obligor",
        "indemnitor", "sponsor", "backer"
    ],

    "parties.witness": [
        "witness", "notary", "attesting officer", "observer"
    ],

    # DATES
    "effective_date": [
        "effective date", "start date", "commencement date",
        "execution date", "beginning", "inception", "initiation",
        "commencement", "effective from", "as of", "dated"
    ],

    "expiration_date": [
        "expiration date", "end date", "termination date",
        "completion date", "conclusion", "expiry", "maturity",
        "due date", "deadline", "final date"
    ],

    "renewal_date": [
        "renewal date", "extension date", "continuation date",
        "renewal period", "extension period"
    ],

    "notice_date": [
        "notice date", "notification date", "informing date",
        "advance notice date"
    ],

    # FINANCIAL TERMS
    "payment_amount": [
        "payment", "amount", "total amount", "contract value",
        "consideration", "fees", "price", "charges",
        "compensation", "remuneration", "salary", "wages",
        "commission", "bonus", "royalty", "rent", "lease payment",
        "premium", "deposit", "security deposit", "retainer",
        "advance", "installment", "milestone payment",
        "lump sum", "total cost", "contract price", "sum",
        "value", "worth", "payment terms", "payment schedule",
        "billing", "invoicing"
    ],

    "currency": [
        "currency", "monetary unit", "denomination",
        "currency of payment", "payment currency"
    ],

    "tax": [
        "tax", "taxes", "taxation", "vat", "gst", "sales tax",
        "service tax", "withholding tax", "tax liability",
        "tax obligation", "tax rate", "tax percentage"
    ],

    # TERM & DURATION
    "term_period": [
        "term", "term period", "duration", "tenure",
        "validity", "contract period", "lease period",
        "agreement period", "engagement period", "service period",
        "subscription period", "license period", "franchise period",
        "employment period", "probation period", "trial period",
        "initial term", "primary term", "base term",
        "renewal term", "extended term", "additional term"
    ],

    # TERMINATION
    "termination_notice_days": [
        "termination", "notice period", "termination notice",
        "exit", "cancellation", "termination clause",
        "notice", "advance notice", "prior notice",
        "termination for cause", "termination for convenience",
        "breach termination", "default termination",
        "mutual termination", "termination penalty",
        "termination fee", "early termination", "exit clause"
    ],

    # SERVICES & DELIVERABLES
    "services": [
        "services", "scope of work", "work description",
        "deliverables", "obligations", "responsibilities",
        "duties", "tasks", "functions", "activities",
        "work", "job", "assignment", "project",
        "scope", "description of services", "service description",
        "work scope", "statement of work", "sow",
        "deliverable", "milestone", "output", "result",
        "product", "goods", "materials", "equipment",
        "software", "application", "system"
    ],

    "service_level_agreement": [
        "sla", "service level", "performance standard",
        "quality standard", "performance metric", "kpi",
        "key performance indicator", "service standard",
        "quality requirement", "performance requirement"
    ],

    # LEGAL & COMPLIANCE
    "governing_law": [
        "governing law", "applicable law", "jurisdiction",
        "legal jurisdiction", "law", "controlling law",
        "proper law", "chosen law", "forum", "venue",
        "legal venue", "court", "legal system",
        "state law", "federal law", "country law"
    ],

    "dispute_resolution": [
        "dispute", "dispute resolution", "arbitration",
        "mediation", "conciliation", "litigation",
        "court proceeding", "legal action", "lawsuit",
        "claim", "grievance", "conflict", "disagreement"
    ],

    "confidentiality": [
        "confidentiality", "non-disclosure", "nda",
        "privacy", "secrecy", "proprietary information",
        "trade secret", "confidential information",
        "protected information", "sensitive information"
    ],

    "intellectual_property": [
        "intellectual property", "ip", "copyright",
        "patent", "trademark", "trade secret",
        "proprietary rights", "ownership", "rights",
        "license", "permission", "authorization"
    ],

    "indemnification": [
        "indemnification", "indemnity", "hold harmless",
        "liability", "responsibility", "obligation",
        "damages", "loss", "claim", "compensation"
    ],

    "warranty": [
        "warranty", "guarantee", "assurance", "promise",
        "representation", "undertaking", "commitment",
        "certification", "warrant", "guaranty"
    ],

    "insurance": [
        "insurance", "coverage", "policy", "insurer",
        "insured", "liability insurance", "professional indemnity",
        "general liability", "workers compensation",
        "insurance requirement", "minimum coverage"
    ],

    "force_majeure": [
        "force majeure", "act of god", "unforeseen circumstances",
        "uncontrollable events", "natural disaster",
        "emergency", "crisis", "pandemic", "epidemic"
    ],

    # BUSINESS TERMS
    "payment_terms": [
        "payment terms", "payment schedule", "billing cycle",
        "payment method", "payment due", "invoice",
        "billing", "remittance", "payment frequency",
        "net payment", "advance payment", "progress payment",
        "final payment", "retention", "withholding"
    ],

    "delivery_terms": [
        "delivery", "delivery terms", "shipment",
        "transportation", "logistics", "incoterms",
        "fob", "cif", "ex-works", "delivery date",
        "ship date", "receipt", "acceptance"
    ],

    "acceptance_criteria": [
        "acceptance", "acceptance criteria", "approval",
        "sign-off", "verification", "validation",
        "testing", "inspection", "quality check",
        "quality assurance", "qa", "qc"
    ],

    # CONTACT INFORMATION
    "contact_information": [
        "contact", "contact information", "address",
        "phone", "email", "fax", "website",
        "registered address", "principal place of business",
        "corporate address", "mailing address",
        "billing address", "shipping address",
        "contact person", "representative", "agent"
    ],

    # MISCELLANEOUS
    "signatories": [
        "signatory", "signer", "authorized representative",
        "authorized signatory", "executive", "officer",
        "director", "partner", "principal"
    ],

    "amendments": [
        "amendment", "modification", "change",
        "revision", "addendum", "supplement",
        "annex", "attachment", "exhibit",
        "schedule", "appendix", "rider"
    ],

    "assignment": [
        "assignment", "transfer", "delegation",
        "subcontracting", "outsourcing", "novation"
    ],

    "severability": [
        "severability", "separability", "invalidity",
        "unenforceability", "illegality"
    ],

    "entire_agreement": [
        "entire agreement", "whole agreement",
        "complete agreement", "full agreement",
        "integration clause", "merger clause"
    ],

    "counterparts": [
        "counterpart", "duplicate", "copy",
        "original", "executed copy", "signed copy"
    ],

    "notices": [
        "notice", "notification", "communication",
        "correspondence", "written notice", "formal notice",
        "legal notice", "service of process"
    ],

    # CONTRACT-SPECIFIC
    "agreement_type": [
        "agreement type", "contract type", "document type",
        "master agreement", "service agreement", "lease agreement",
        "license agreement", "employment agreement",
        "consulting agreement", "non-disclosure agreement",
        "purchase agreement", "sales agreement",
        "distribution agreement", "franchise agreement",
        "partnership agreement", "joint venture agreement"
    ],

    "contract_id": [
        "contract id", "agreement number", "document number",
        "reference number", "file number", "case number",
        "contract reference", "agreement reference"
    ],

    "version": [
        "version", "edition", "revision", "draft",
        "issue", "release", "update"
    ],

    "status": [
        "status", "state", "condition", "phase",
        "stage", "progress", "completion status"
    ],

    # REAL ESTATE SPECIFIC
    "property_address": [
        "property", "address", "premises", "location",
        "site", "building", "facility", "real estate",
        "land", "plot", "lot", "parcel"
    ],

    "square_footage": [
        "square footage", "area", "size", "dimension",
        "floor area", "usable area", "rentable area"
    ],

    # EMPLOYMENT SPECIFIC
    "job_title": [
        "job title", "position", "role", "designation",
        "title", "occupation", "post"
    ],

    "reporting_to": [
        "reporting to", "supervisor", "manager",
        "boss", "superior", "line manager"
    ],

    "benefits": [
        "benefits", "perks", "allowances", "incentives",
        "bonus", "commission", "stock options",
        "health insurance", "retirement", "pension",
        "vacation", "leave", "holiday"
    ],

    # LEASE SPECIFIC
    "security_deposit": [
        "security deposit", "damage deposit", "bond",
        "guarantee deposit", "advance deposit"
    ],

    "maintenance_responsibility": [
        "maintenance", "repair", "upkeep", "care",
        "maintenance responsibility", "repair obligation"
    ],

    "utilities": [
        "utilities", "services", "electricity", "water",
        "gas", "internet", "telephone", "cable"
    ]
}

# Additional specialized field groups for common queries
QUERY_PATTERNS = {
    "financial_summary": [
        "payment", "amount", "total", "value", "price", "fee",
        "cost", "charge", "payment terms", "payment schedule"
    ],

    "parties_involved": [
        "client", "customer", "vendor", "supplier", "service provider",
        "parties", "who is involved", "counterparties"
    ],

    "key_dates": [
        "date", "effective", "expiration", "start", "end",
        "commencement", "termination", "renewal"
    ],

    "legal_terms": [
        "governing law", "jurisdiction", "confidentiality",
        "indemnification", "warranty", "liability", "dispute"
    ],

    "services_scope": [
        "services", "scope", "work", "deliverables", "obligations",
        "responsibilities", "duties", "tasks"
    ]
}


def resolve_requested_fields(question: str) -> List[str]:
    """
    Resolve which contract fields are being requested in a question.

    Args:
        question: The user's question about the contract

    Returns:
        List of canonical field names to extract from the contract
    """
    question = question.lower().strip()
    matched_fields = []

    # Check for broad categories first
    if any(keyword in question for keyword in ["all", "everything", "complete", "full", "entire"]):
        if "detail" in question or "information" in question or "summary" in question:
            # Return all fields for complete summary
            return list(FIELD_ALIASES.keys())

    # Check for specific financial summary request
    if any(keyword in question for keyword in ["financial", "payment", "amount", "cost", "price"]):
        if any(keyword in question for keyword in ["summary", "overview", "details", "information"]):
            matched_fields.extend([
                "payment_amount", "currency", "tax", "payment_terms"
            ])

    # Check for parties summary request
    if any(keyword in question for keyword in ["party", "parties", "who", "involved"]):
        if any(keyword in question for keyword in ["summary", "overview", "details", "information"]):
            matched_fields.extend([
                "parties.client", "parties.service_provider",
                "contact_information", "signatories"
            ])

    # Check for dates summary request
    if any(keyword in question for keyword in ["date", "timeline", "schedule"]):
        if any(keyword in question for keyword in ["summary", "overview", "details", "information"]):
            matched_fields.extend([
                "effective_date", "expiration_date", "renewal_date",
                "term_period"
            ])

    # Check each canonical field
    for canonical_field, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            # Use word boundaries to match whole words only
            pattern = rf"\b{re.escape(alias)}\b"
            if re.search(pattern, question):
                if canonical_field not in matched_fields:
                    matched_fields.append(canonical_field)
                break

    # If no specific fields matched, try to infer from question type
    if not matched_fields:
        matched_fields = infer_fields_from_question(question)

    # Remove duplicates while preserving order
    seen = set()
    unique_fields = []
    for field in matched_fields:
        if field not in seen:
            seen.add(field)
            unique_fields.append(field)

    return unique_fields


def infer_fields_from_question(question: str) -> List[str]:
    """
    Infer relevant fields from the question when no direct matches are found.
    """
    question_lower = question.lower()
    inferred_fields = []

    # Common question patterns and their likely field matches
    patterns = [
        # Who questions
        (r"who\s+(is|are|will|shall)", ["parties.client", "parties.service_provider", "signatories"]),
        (r"who\s+(pays|pays for|is responsible for)", ["payment_amount", "payment_terms"]),

        # What questions
        (r"what\s+(is|are)\s+the\s+(payment|fee|cost|price|amount)", ["payment_amount", "currency", "payment_terms"]),
        (r"what\s+(is|are)\s+the\s+(term|duration|period)", ["term_period", "effective_date", "expiration_date"]),
        (r"what\s+(is|are)\s+the\s+(service|work|deliverable)", ["services", "service_level_agreement"]),
        (r"what\s+(is|are)\s+the\s+(legal|law|jurisdiction)", ["governing_law", "dispute_resolution"]),

        # When questions
        (r"when\s+(does|will|shall)", ["effective_date", "expiration_date", "renewal_date"]),
        (r"when\s+(is|are)\s+(payment|fee|amount)\s+(due|payable)", ["payment_terms"]),
        (r"when\s+(can|cannot|may)\s+(terminate|cancel|end)", ["termination_notice_days"]),

        # How questions
        (r"how\s+(much|many)\s+(does|will|shall)\s+(it\s+)?cost", ["payment_amount"]),
        (r"how\s+(long|much time)\s+(does|will|shall)", ["term_period"]),
        (r"how\s+(to|do I|can I)\s+(terminate|cancel|end)", ["termination_notice_days"]),

        # Table/summary requests
        (r"(give|show|list|provide)\s+me\s+(the|all)\s+(detail|information|summary)",
         ["parties.client", "parties.service_provider", "payment_amount", "effective_date",
          "term_period", "services", "governing_law"]),

        # Contract overview requests
        (r"(summarize|overview|brief|highlight)\s+(the|this)\s+(contract|agreement)",
         ["parties.client", "parties.service_provider", "payment_amount", "effective_date",
          "term_period", "services", "governing_law"]),
    ]

    for pattern, fields in patterns:
        if re.search(pattern, question_lower):
            inferred_fields.extend(fields)

    # If still no matches, return common default fields
    if not inferred_fields:
        # Default to key contract fields for general questions
        inferred_fields = [
            "parties.client", "parties.service_provider",
            "payment_amount", "effective_date", "term_period"
        ]

    return list(set(inferred_fields))  # Remove duplicates


def enhance_question_understanding(question: str) -> Dict[str, Any]:
    """
    Enhanced function to understand the user's question better.
    Returns metadata about what the user is asking for.
    """
    question_lower = question.lower()

    result = {
        "original_question": question,
        "is_table_request": False,
        "is_summary_request": False,
        "field_categories": [],
        "specific_fields": []
    }

    # Check if user wants table format
    table_keywords = ["table", "tabular", "in a table", "as a table",
                      "table format", "grid", "spreadsheet", "matrix"]
    result["is_table_request"] = any(keyword in question_lower for keyword in table_keywords)

    # Check if user wants a summary
    summary_keywords = ["summarize", "summary", "overview", "brief",
                        "highlight", "key points", "main points"]
    result["is_summary_request"] = any(keyword in question_lower for keyword in summary_keywords)

    # Determine field categories
    if any(keyword in question_lower for keyword in ["payment", "amount", "cost", "price", "fee"]):
        result["field_categories"].append("financial")

    if any(keyword in question_lower for keyword in ["party", "who", "client", "vendor", "supplier"]):
        result["field_categories"].append("parties")

    if any(keyword in question_lower for keyword in ["date", "when", "start", "end", "term", "duration"]):
        result["field_categories"].append("dates")

    if any(keyword in question_lower for keyword in ["service", "work", "deliverable", "scope", "obligation"]):
        result["field_categories"].append("services")

    if any(keyword in question_lower for keyword in ["law", "legal", "jurisdiction", "confidential", "warranty"]):
        result["field_categories"].append("legal")

    # Get specific fields
    result["specific_fields"] = resolve_requested_fields(question)

    return result


# Example usage in Django view:
"""
from django.http import JsonResponse
from .table_builder import build_table, format_table_for_response

def query_contract_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            workspace_id = data.get('workspace_id')
            question = data.get('question')
            mode = data.get('mode', 'answer')

            # Get contract data from your database/storage
            contract_data = get_contract_data(workspace_id)

            # Enhanced question understanding
            question_analysis = enhance_question_understanding(question)

            # Get fields to extract
            allowed_fields = question_analysis["specific_fields"]

            # If no specific fields found but it's a summary request, use default fields
            if not allowed_fields and question_analysis["is_summary_request"]:
                allowed_fields = ["parties.client", "parties.service_provider", 
                                 "payment_amount", "effective_date", "term_period", 
                                 "services", "governing_law"]

            # Determine response type
            if mode == 'table' or question_analysis["is_table_request"]:
                # Build table response
                table_data = build_table(contract_data, allowed_fields)
                response_data = format_table_for_response(table_data)
            else:
                # Build text response
                response_data = {
                    "type": "text",
                    "data": generate_text_response(contract_data, allowed_fields, question)
                }

            # Return proper JSON response
            return JsonResponse(response_data, json_dumps_params={'ensure_ascii': False})

        except Exception as e:
            return JsonResponse({
                "type": "error",
                "message": f"Error processing request: {str(e)}"
            }, status=500)
"""