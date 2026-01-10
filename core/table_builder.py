import json
from typing import Dict, List, Any, Optional, Union


def build_table(contract: Dict[str, Any], allowed_fields: List[str]) -> Dict[str, Any]:
    """
    Build a clean, professional table from contract data.

    Args:
        contract: The contract dictionary
        allowed_fields: List of field paths to extract

    Returns:
        Dictionary with type, columns, and rows for table display
    """
    rows = []

    # Enhanced field name mapping for better display
    field_display_names = {
        # Parties
        'parties.client': 'Client',
        'parties.service_provider': 'Service Provider',
        'parties.vendor': 'Vendor',
        'parties.supplier': 'Supplier',
        'parties.buyer': 'Buyer',
        'parties.seller': 'Seller',
        'parties.lessor': 'Lessor',
        'parties.lessee': 'Lessee',
        'parties.licensor': 'Licensor',
        'parties.licensee': 'Licensee',
        'parties.employer': 'Employer',
        'parties.employee': 'Employee',
        'parties.contractor': 'Contractor',
        'parties.subcontractor': 'Subcontractor',

        # Dates
        'effective_date': 'Effective Date',
        'execution_date': 'Execution Date',
        'commencement_date': 'Commencement Date',
        'expiration_date': 'Expiration Date',
        'termination_date': 'Termination Date',
        'renewal_date': 'Renewal Date',
        'notice_date': 'Notice Date',

        # Financial
        'payment_amount': 'Total Amount',
        'total_amount': 'Total Amount',
        'contract_value': 'Contract Value',
        'consideration': 'Consideration',
        'price': 'Price',
        'fee': 'Fee',
        'rate': 'Rate',
        'payment_terms': 'Payment Terms',
        'payment_schedule': 'Payment Schedule',
        'payment_method': 'Payment Method',
        'currency': 'Currency',
        'tax': 'Tax',
        'tax_rate': 'Tax Rate',
        'deposit': 'Deposit',
        'advance_payment': 'Advance Payment',
        'retention': 'Retention',

        # Term & Duration
        'term_period': 'Term Period',
        'contract_term': 'Contract Term',
        'initial_term': 'Initial Term',
        'renewal_term': 'Renewal Term',
        'duration': 'Duration',
        'start_date': 'Start Date',
        'end_date': 'End Date',

        # Termination
        'termination_clause': 'Termination Clause',
        'termination_notice_period': 'Termination Notice Period',
        'termination_notice_days': 'Termination Notice (Days)',
        'termination_for_cause': 'Termination for Cause',
        'termination_for_convenience': 'Termination for Convenience',
        'termination_penalty': 'Termination Penalty',

        # Services & Deliverables
        'services_provided': 'Services Provided',
        'scope_of_work': 'Scope of Work',
        'deliverables': 'Deliverables',
        'milestones': 'Milestones',
        'specifications': 'Specifications',
        'requirements': 'Requirements',

        # Legal & Compliance
        'governing_law': 'Governing Law',
        'jurisdiction': 'Jurisdiction',
        'venue': 'Venue',
        'arbitration': 'Arbitration',
        'dispute_resolution': 'Dispute Resolution',
        'confidentiality': 'Confidentiality',
        'non_disclosure': 'Non-Disclosure',
        'non_compete': 'Non-Compete',
        'intellectual_property': 'Intellectual Property',
        'indemnification': 'Indemnification',
        'liability': 'Liability',
        'warranties': 'Warranties',
        'representations': 'Representations',
        'insurance': 'Insurance',
        'force_majeure': 'Force Majeure',
        'assignment': 'Assignment',
        'amendment': 'Amendment',
        'severability': 'Severability',
        'entire_agreement': 'Entire Agreement',
        'counterparts': 'Counterparts',
        'notices': 'Notices',

        # Business Terms
        'sla': 'Service Level Agreement',
        'performance_metrics': 'Performance Metrics',
        'quality_standards': 'Quality Standards',
        'acceptance_criteria': 'Acceptance Criteria',
        'inspection': 'Inspection',
        'audit_rights': 'Audit Rights',
        'change_order': 'Change Order',
        'variation': 'Variation',

        # Contact Information
        'contact_person': 'Contact Person',
        'contact_email': 'Contact Email',
        'contact_phone': 'Contact Phone',
        'address': 'Address',
        'registered_address': 'Registered Address',

        # Miscellaneous
        'agreement_type': 'Agreement Type',
        'contract_id': 'Contract ID',
        'reference_number': 'Reference Number',
        'version': 'Version',
        'status': 'Status',
        'signatories': 'Signatories',
        'witnesses': 'Witnesses',
        'exhibits': 'Exhibits',
        'appendices': 'Appendices',
        'attachments': 'Attachments',
    }

    for field_path in allowed_fields:
        # Navigate through the nested dictionary
        value = contract
        path_parts = field_path.split('.')

        for part in path_parts:
            if not isinstance(value, dict):
                value = None
                break
            value = value.get(part)

        if value is not None:
            # Convert value to string if it's not already
            if isinstance(value, (list, dict)):
                if isinstance(value, list) and len(value) == 1:
                    value = value[0]
                else:
                    value = str(value)

            # Get display name for the field
            display_name = field_display_names.get(field_path)
            if not display_name:
                # Generate a clean display name from the field path
                display_name = field_path
                # Remove 'parties.' prefix if present
                if display_name.startswith('parties.'):
                    display_name = display_name[8:]
                # Replace underscores with spaces and title case
                display_name = display_name.replace('_', ' ').title()
                # Clean up common patterns
                display_name = display_name.replace('Sla', 'SLA')
                display_name = display_name.replace('Ip', 'IP')
                display_name = display_name.replace('Nd', 'ND')
                display_name = display_name.replace('Non ', 'Non-')

            rows.append([display_name, str(value)])

    # Sort rows alphabetically by field name for better readability
    rows.sort(key=lambda x: x[0])

    return {
        "type": "table",
        "columns": ["Field", "Value"],
        "rows": rows
    }


def format_table_for_response(table_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format table data for API response.

    Args:
        table_data: The table data from build_table()

    Returns:
        Properly formatted response dictionary
    """
    return {
        "type": "table",
        "columns": table_data.get("columns", ["Field", "Value"]),
        "rows": table_data.get("rows", [])
    }


# Example usage in Django view:
"""
from django.http import JsonResponse

def query_contract_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            workspace_id = data.get('workspace_id')
            question = data.get('question')
            mode = data.get('mode', 'answer')

            # Get contract data (you'll implement this based on your storage)
            contract_data = get_contract_data(workspace_id)

            # Determine which fields to extract based on the question
            allowed_fields = extract_relevant_fields(question, contract_data)

            if mode == 'table' or 'table' in question.lower() or 'tabular' in question.lower():
                # Build table response
                table_data = build_table(contract_data, allowed_fields)
                response_data = format_table_for_response(table_data)
            else:
                # Build text response
                response_data = {
                    "type": "text",
                    "data": generate_text_response(contract_data, question)
                }

            # Return proper JSON response
            return JsonResponse(response_data, json_dumps_params={'ensure_ascii': False})

        except Exception as e:
            return JsonResponse({
                "type": "error",
                "message": f"Error processing request: {str(e)}"
            }, status=500)
"""