from typing import Any


class CloudOpsValidator:
    """
    Validates structural and content integrity of generated cloud diagnosis and fix reports.
    """

    REQUIRED_TOP_KEYS = ["rca", "remediation_steps", "verification_steps"]
    REQUIRED_RCA_KEYS = ["summary", "error_category", "severity", "failing_service", "triggering_event"]

    def validate(self, data: Any) -> bool:
        if not isinstance(data, dict):
            return False

        for k in self.REQUIRED_TOP_KEYS:
            if k not in data or not data[k]:
                return False

        rca = data.get("rca")
        if not isinstance(rca, dict):
            return False

        for k in self.REQUIRED_RCA_KEYS:
            if k not in rca or not str(rca[k]).strip():
                return False

        steps = data.get("remediation_steps")
        if not isinstance(steps, list) or len(steps) == 0:
            return False

        for step in steps:
            if not isinstance(step, dict):
                return False
            if "action" not in step or "explanation" not in step:
                return False

        return True
