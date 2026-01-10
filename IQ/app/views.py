from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import os
import tempfile
import sys
import json

# Add the path to core module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Try to import core modules
try:
    from core.backend import ingest as core_ingest, query as core_query, get_workspace_status

    print("✓ Core backend imported successfully")
except ImportError as e:
    print(f"✗ Could not import core.backend: {e}")
    core_ingest = None
    core_query = None
    get_workspace_status = None


def chat_page(request):
    return render(request, "chat.html")


@csrf_exempt
def ingest(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    files = request.FILES.getlist("files")
    if not files:
        return JsonResponse({"error": "No files"}, status=400)

    try:
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        saved_files = []

        print(f"INFO: Processing {len(files)} files")

        # Save uploaded files
        for uploaded_file in files:
            safe_filename = uploaded_file.name.replace(" ", "_").replace("/", "_")
            file_path = os.path.join(temp_dir, safe_filename)

            with open(file_path, "wb+") as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            saved_files.append(file_path)
            print(f"INFO: Saved {uploaded_file.name} to {file_path}")

        # Process with core backend
        if core_ingest:
            try:
                result = core_ingest(saved_files)

                if result.get("status") == "failed":
                    return JsonResponse({
                        "error": result.get("error", "Ingestion failed"),
                        "workspace_id": result.get("workspace_id")
                    }, status=500)

                return JsonResponse({
                    "message": "Document ingestion started",
                    "workspace_id": result.get("workspace_id"),
                    "status": result.get("status", "started"),
                    "files": [os.path.basename(f) for f in saved_files],
                    "note": "Processing in background. Use /api/status/ to check progress."
                })
            except Exception as e:
                return JsonResponse({
                    "error": f"Core ingestion error: {str(e)}"
                }, status=500)
        else:
            # Fallback if core backend not available
            return JsonResponse({
                "message": "Files saved but core processing not available",
                "saved_files": [os.path.basename(f) for f in saved_files],
                "count": len(files),
                "note": "Core modules not imported properly"
            })

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR in ingest: {error_details}")
        return JsonResponse({
            "error": str(e),
            "details": "Check server logs for more information"
        }, status=500)


@csrf_exempt
def check_status(request, workspace_id):
    """Check status of an ingestion job"""
    try:
        if not get_workspace_status:
            return JsonResponse({
                "error": "Workspace status function not available",
                "workspace_id": workspace_id
            }, status=500)

        status = get_workspace_status(workspace_id)

        return JsonResponse(status)

    except Exception as e:
        import traceback
        return JsonResponse({
            "workspace_id": workspace_id,
            "error": str(e),
            "traceback": traceback.format_exc()
        }, status=500)


@csrf_exempt
def query_api(request):
    """Handle query requests - with detailed debugging"""
    if request.method != "POST":
        return JsonResponse({
            "type": "error",
            "message": "POST only"
        }, status=405)

    print("\n" + "=" * 80)
    print("QUERY API CALLED")
    print("=" * 80)

    try:
        # Parse request data
        try:
            data = json.loads(request.body)
            print(f"✓ Request data parsed: {data}")
        except json.JSONDecodeError as e:
            print(f"✗ JSON decode error: {e}")
            print(f"Raw body: {request.body}")
            return JsonResponse({
                "type": "error",
                "message": "Invalid JSON format"
            }, status=400)

        # Extract parameters
        workspace_id = data.get("workspace_id")
        question = data.get("question", "").strip()
        mode = data.get("mode", "answer")

        print(f"✓ Parameters:")
        print(f"  Workspace ID: {workspace_id}")
        print(f"  Question: {question}")
        print(f"  Mode: {mode}")

        # Validate parameters
        if not workspace_id:
            print("✗ Missing workspace_id")
            return JsonResponse({
                "type": "error",
                "message": "Workspace ID is required"
            })

        if not question:
            print("✗ Empty question")
            return JsonResponse({
                "type": "error",
                "message": "Question is required"
            })

        # Check if core_query is available
        if not core_query:
            print("✗ core_query function not available")
            return JsonResponse({
                "type": "error",
                "message": "Query functionality not available"
            }, status=500)

        print(f"✓ Calling core_query function...")

        # Call the core query function
        result = core_query(workspace_id, question, mode)

        print(f"✓ core_query returned: {type(result)}")
        print(f"Result content: {result}")

        # Format response properly
        if isinstance(result, dict):
            print(f"✓ Result is dict, keys: {list(result.keys())}")

            # Handle different response types
            response_type = result.get("type")

            if response_type == "error":
                print(f"✗ Error result: {result.get('message')}")
                return JsonResponse(result)
            elif response_type == "text":
                print(f"✓ Text result, length: {len(result.get('data', ''))}")
                return JsonResponse(result)
            elif response_type == "table":  # ← THIS IS THE FIX!
                print(f"✓ Table result, columns: {result.get('columns', [])}, rows: {len(result.get('rows', []))}")
                return JsonResponse(result)
            elif "answer" in result:
                print(f"✓ Old format detected, converting...")
                # Convert old format to new format
                return JsonResponse({
                    "type": "text",
                    "data": result.get("answer", "")
                })
            elif "data" in result:
                print(f"✓ Data result, length: {len(result.get('data', ''))}")
                return JsonResponse({
                    "type": "text",
                    "data": result.get("data", "")
                })
            else:
                # If no type but looks like a table
                if "columns" in result and "rows" in result:
                    print(f"✓ Implicit table result (has columns & rows)")
                    return JsonResponse({
                        "type": "table",
                        "columns": result["columns"],
                        "rows": result["rows"]
                    })
                else:
                    print(f"⚠️ Unknown dict format, returning as text")
                    return JsonResponse({
                        "type": "text",
                        "data": str(result)
                    })

        # Handle string results
        elif isinstance(result, str):
            print(f"✓ String result, length: {len(result)}")
            return JsonResponse({
                "type": "text",
                "data": result
            })

        # Fallback for unexpected format
        print(f"⚠️ Unexpected result format: {type(result)}")
        return JsonResponse({
            "type": "text",
            "data": str(result)
        })

    except Exception as e:
        print(f"✗ Exception in query_api: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            "type": "error",
            "message": f"Server error: {str(e)}"
        }, status=500)


@csrf_exempt
def list_workspaces(request):
    """List all workspaces - simplified version"""
    try:
        # Since we don't have a list function, return empty for now
        return JsonResponse({
            "workspaces": [],
            "count": 0,
            "note": "Workspace listing not implemented"
        })
    except Exception as e:
        return JsonResponse({
            "error": str(e)
        }, status=500)


from django.http import JsonResponse
from core.table_builder import build_table, format_table_for_response

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