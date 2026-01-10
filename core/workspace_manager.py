import uuid
import time
from datetime import datetime


class Workspace:
    def __init__(self, workspace_id, file_path=None):
        self.id = workspace_id
        self.file_path = file_path
        self.created_at = datetime.now().isoformat()
        self.status = "pending"  # pending, processing, completed, failed
        self.progress = 0
        self.extraction_status = "ingesting"
        self.extraction_progress = 0
        self.vector_store = None
        self.raw_text = None
        self.chunks = None
        self.error = None
        self.result = None

    def update_status(self, status, progress=0, error=None):
        self.status = status
        self.progress = progress
        if error:
            self.error = error
            self.status = "failed"

    def to_dict(self):
        return {
            "id": self.id,
            "file_path": self.file_path,
            "created_at": self.created_at,
            "status": self.status,
            "progress": self.progress,
            "extraction_status": self.extraction_status,
            "extraction_progress": self.extraction_progress,
            "has_vector_store": self.vector_store is not None,
            "error": self.error,
            "result": self.result
        }


class WorkspaceManager:
    def __init__(self):
        self._workspaces = {}

    def create_workspace(self, file_path=None):
        workspace_id = str(uuid.uuid4())
        ws = Workspace(workspace_id, file_path)
        self._workspaces[workspace_id] = ws
        return ws

    def get_workspace(self, workspace_id):
        return self._workspaces.get(workspace_id)

    def get_status(self, workspace_id):
        ws = self.get_workspace(workspace_id)
        if ws:
            return ws.to_dict()
        return {"error": "Workspace not found", "workspace_id": workspace_id}

    def update_workspace(self, workspace_id, **kwargs):
        ws = self.get_workspace(workspace_id)
        if ws:
            for key, value in kwargs.items():
                if hasattr(ws, key):
                    setattr(ws, key, value)
            return True
        return False

    def list_workspaces(self):
        return [ws.to_dict() for ws in self._workspaces.values()]

    def delete_workspace(self, workspace_id):
        if workspace_id in self._workspaces:
            del self._workspaces[workspace_id]
            return True
        return False


# 🔒 SINGLE GLOBAL INSTANCE
workspace_manager = WorkspaceManager()