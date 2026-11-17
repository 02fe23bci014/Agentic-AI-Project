from typing import Any


class SafetyGovernanceValidator:
    """
    Validates the structure and consistency of safety assessment and rollback data.
    """

    REQUIRED_TOP_KEYS = ["overall_risk_score", "risk_tier", "risk_dimensions", "approval", "rollback_plan"]

    def validate(self, data: Any) -> bool:
        if not isinstance(data, dict):
            return False

        for k in self.REQUIRED_TOP_KEYS:
            if k not in data:
                return False

        score = data.get("overall_risk_score")
        if not isinstance(score, int) or score < 0 or score > 100:
            return False

        tier = data.get("risk_tier")
        if tier not in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
            return False

        dims = data.get("risk_dimensions")
        if not isinstance(dims, list) or len(dims) == 0:
            return False

        approval = data.get("approval")
        if not isinstance(approval, dict) or "status" not in approval:
            return False

        rollback = data.get("rollback_plan")
        if not isinstance(rollback, dict) or "strategy" not in rollback or "steps" not in rollback:
            return False

        return True
