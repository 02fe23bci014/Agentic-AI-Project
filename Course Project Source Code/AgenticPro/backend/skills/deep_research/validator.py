from typing import Any


class ResearchValidator:
    """
    Validates the structure, integrity, and quality of generated research briefings and evidence tables.
    """

    REQUIRED_TOP_LEVEL_KEYS = [
        "topic",
        "executive_summary",
        "key_findings",
        "technical_analysis",
        "evidence_table",
    ]

    REQUIRED_EVIDENCE_KEYS = [
        "source",
        "claim",
        "evidence_quote",
    ]

    def validate(self, data: Any) -> bool:
        """Validate research briefing data."""
        if not isinstance(data, dict):
            return False

        for key in self.REQUIRED_TOP_LEVEL_KEYS:
            if key not in data or not data[key]:
                return False

        if not isinstance(data["key_findings"], list) or len(data["key_findings"]) == 0:
            return False

        if not isinstance(data["evidence_table"], list) or len(data["evidence_table"]) == 0:
            return False

        # Validate each row in the evidence table
        for item in data["evidence_table"]:
            if not isinstance(item, dict):
                return False
            for k in self.REQUIRED_EVIDENCE_KEYS:
                if k not in item or not str(item[k]).strip():
                    return False

        return True
