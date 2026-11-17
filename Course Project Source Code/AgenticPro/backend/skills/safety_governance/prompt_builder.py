class SafetyGovernancePromptBuilder:
    """
    Builds structured safety assessment, risk evaluation, and rollback planning prompts.
    """

    def build(
        self,
        action_title: str,
        target_system: str,
        proposed_payload: str,
        initiator: str = "agent",
        declared_purpose: str = "",
    ) -> str:
        return f"""You are a Principal AI Safety & Cloud Governance Officer.
Assess the risk, safety compliance, human approval requirements, and rollback plan for the following proposed action:

ACTION TITLE: {action_title}
TARGET SYSTEM: {target_system}
INITIATOR: {initiator}
PURPOSE: {declared_purpose}

PROPOSED PAYLOAD / CODE / COMMAND:
\"\"\"
{proposed_payload}
\"\"\"

Respond with a valid JSON object matching this schema:
{{
  "overall_risk_score": 75,
  "risk_tier": "HIGH",
  "risk_dimensions": [
    {{
      "name": "Security & Vulnerability",
      "score": 80,
      "tier": "HIGH",
      "rationale": "Direct privilege modification identified."
    }},
    {{
      "name": "Operational Stability",
      "score": 70,
      "tier": "HIGH",
      "rationale": "High traffic service restart."
    }},
    {{
      "name": "Data Privacy & Compliance",
      "score": 40,
      "tier": "MEDIUM",
      "rationale": "No customer PII exposed."
    }}
  ],
  "approval": {{
    "status": "PENDING_REVIEW",
    "required_approvers": ["Platform Security Lead", "Database Administrator"],
    "decision_notes": "Awaiting human review."
  }},
  "rollback_plan": {{
    "strategy": "Automated Revert",
    "estimated_rto_seconds": 60,
    "state_checkpoint": "git-commit-hash-or-snapshot",
    "steps": [
      {{
        "order": 1,
        "action": "Revert Git Commit or Rollback Migration",
        "command": "git revert HEAD --no-edit",
        "verification": "Check git status is clean",
        "estimated_seconds": 15
      }}
    ]
  }}
}}
"""
