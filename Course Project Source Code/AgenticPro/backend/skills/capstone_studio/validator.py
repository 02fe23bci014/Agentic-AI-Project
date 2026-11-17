from typing import Any
from backend.models.capstone import CapstoneProjectArtifact


class CapstoneValidator:
    """Validator for Capstone Project Studio artifacts."""

    def validate(self, data: dict[str, Any]) -> bool:
        if not isinstance(data, dict):
            return False

        required_keys = [
            "team_name",
            "project_title",
            "domain",
            "mission_statement",
            "team_members",
            "stages",
            "deliverables",
            "test_run",
        ]
        if not all(k in data for k in required_keys):
            return False

        if not isinstance(data.get("team_members"), list) or len(data["team_members"]) == 0:
            return False

        if not isinstance(data.get("stages"), list) or len(data["stages"]) == 0:
            return False

        try:
            CapstoneProjectArtifact(**data)
            return True
        except Exception:
            return False
