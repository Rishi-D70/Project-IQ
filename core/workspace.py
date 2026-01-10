from typing import List, Optional
from datetime import datetime

class Workspace:
    def __init__(self, workspace_id: str):
        self.workspace_id = workspace_id

        # Original inputs
        self.files: List[str] = []

        # Ingestion artifacts
        self.raw_text: Optional[str] = None
        self.chunks: Optional[List[str]] = None
        self.vector_store = None
        self.canonical_contract = None

        # Background extraction state
        self.extraction_status = "not_started"
        # not_started | running | completed | failed
        self.extraction_progress = 0.0
        self.extraction_error: Optional[str] = None

        # Metadata
        self.created_at = datetime.utcnow()
