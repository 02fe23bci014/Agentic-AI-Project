from typing import Any
from backend.models.discipline import DisciplineWorkletArtifact


class DisciplineValidator:
    """Validator for discipline-specific engineering worklet artifacts."""

    def validate(self, data: dict[str, Any]) -> bool:
        """Validate structure and essential engineering fields."""
        if not isinstance(data, dict):
            return False

        required_keys = [
            "discipline",
            "worklet_type",
            "title",
            "parameters",
            "derivation_steps",
            "kpis",
            "compliance_checks",
            "executable_code",
        ]
        if not all(k in data for k in required_keys):
            return False

        if data["discipline"] not in ("ME", "CE", "EE"):
            return False

        if not isinstance(data.get("parameters"), list) or len(data["parameters"]) == 0:
            return False

        if not isinstance(data.get("derivation_steps"), list) or len(data["derivation_steps"]) == 0:
            return False

        try:
            # Pydantic validation
            DisciplineWorkletArtifact(**data)
            return True
        except Exception:
            return False
