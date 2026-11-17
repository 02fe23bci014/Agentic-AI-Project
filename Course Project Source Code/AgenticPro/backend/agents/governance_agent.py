import json
from datetime import datetime
from typing import Any

from backend.database.connection import get_connection
from backend.models.governance import (
    ApprovalDecision,
    GovernanceAssessmentRequest,
    PolicyEvalCheck,
    RiskDimension,
    RollbackPlan,
    RollbackStep,
    SafetyAuditRecord,
)
from backend.skills.safety_governance.skill import SafetyGovernanceSkill
from backend.tools.governance_tool import GovernanceTool


class SafetyGovernanceAgent:
    """
    Lab 12: Safety & Governance Agent.
    Evaluates proposed actions for multi-dimensional risks, enforces policy guardrails,
    manages multi-tier human approval workflows, and prepares verified rollback plans.
    """

    def __init__(self):
        self.skill = SafetyGovernanceSkill()
        self.tool = GovernanceTool()

    def assess_action(self, request: GovernanceAssessmentRequest) -> SafetyAuditRecord:
        """Conduct safety and risk assessment on a proposed action or code payload."""
        raw = self.skill.generate(
            action_title=request.action_title,
            target_system=request.target_system,
            proposed_payload=request.proposed_payload,
            initiator=request.initiator or "agent",
            declared_purpose=request.declared_purpose,
        )

        risk_dims = [RiskDimension(**d) for d in raw.get("risk_dimensions", [])]
        policy_evals = [PolicyEvalCheck(**p) for p in raw.get("policy_evaluations", [])]

        appr_raw = raw.get("approval", {})
        approval = ApprovalDecision(
            status=appr_raw.get("status", "PENDING_REVIEW"),
            reviewer=appr_raw.get("reviewer"),
            decision_notes=appr_raw.get("decision_notes"),
            decided_at=appr_raw.get("decided_at"),
            required_approvers=appr_raw.get("required_approvers", []),
        )

        rb_raw = raw.get("rollback_plan", {})
        steps = [RollbackStep(**s) for s in rb_raw.get("steps", [])]
        rollback_plan = RollbackPlan(
            strategy=rb_raw.get("strategy", "Automated Revert"),
            estimated_rto_seconds=rb_raw.get("estimated_rto_seconds", 60),
            steps=steps,
            state_checkpoint=rb_raw.get("state_checkpoint"),
        )

        audit_id = raw.get("id") or f"gov-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        record = SafetyAuditRecord(
            id=audit_id,
            action_title=request.action_title,
            target_system=request.target_system,
            proposed_payload=request.proposed_payload,
            initiator=request.initiator or "system",
            declared_purpose=request.declared_purpose,
            timestamp=datetime.utcnow().isoformat(),
            overall_risk_score=raw.get("overall_risk_score", 50),
            risk_tier=raw.get("risk_tier", "MEDIUM"),
            risk_dimensions=risk_dims,
            policy_evaluations=policy_evals,
            approval=approval,
            rollback_plan=rollback_plan,
            rollback_executed=False,
            rollback_logs=None,
        )

        self._save_audit(record)
        return record

    def record_decision(self, audit_id: str, decision: str, reviewer: str, notes: str) -> SafetyAuditRecord:
        """Update approval decision (HITL approval workflow)."""
        record = self.get_audit(audit_id)
        record.approval.status = decision.upper()
        record.approval.reviewer = reviewer
        record.approval.decision_notes = notes
        record.approval.decided_at = datetime.utcnow().isoformat()

        self._save_audit(record)
        return record

    def execute_rollback(self, audit_id: str, reason: str, executor: str) -> SafetyAuditRecord:
        """Execute simulated rollback protocol and record recovery logs."""
        record = self.get_audit(audit_id)
        logs = self.tool.simulate_rollback(record.rollback_plan)

        record.rollback_executed = True
        record.rollback_logs = (
            f"[Triggered by: {executor} | Reason: {reason}]\n" + logs
        )

        self._save_audit(record)
        return record

    def get_audit(self, audit_id: str) -> SafetyAuditRecord:
        """Retrieve audit record by ID."""
        with get_connection() as connection:
            row = connection.execute(
                "SELECT audit_json FROM governance_audits WHERE id = ?",
                (audit_id,),
            ).fetchone()

        if not row:
            raise ValueError(f"Safety audit '{audit_id}' not found.")

        data = json.loads(row[0])
        return SafetyAuditRecord(**data)

    def list_audits(self, status: str | None = None, risk_tier: str | None = None) -> list[dict[str, Any]]:
        """List all governance audits."""
        query = """
            SELECT id, action_title, target_system, overall_risk_score, risk_tier, status, initiator, created_at
            FROM governance_audits
        """
        conditions = []
        params = []
        if status and isinstance(status, str):
            conditions.append("status = ?")
            params.append(status)
        if risk_tier and isinstance(risk_tier, str):
            conditions.append("risk_tier = ?")
            params.append(risk_tier)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY created_at DESC"

        with get_connection() as connection:
            rows = connection.execute(query, params).fetchall()

        audits = []
        for r in rows:
            audits.append({
                "id": r[0],
                "action_title": r[1],
                "target_system": r[2],
                "overall_risk_score": r[3],
                "risk_tier": r[4],
                "status": r[5],
                "initiator": r[6],
                "created_at": r[7],
            })
        return audits

    def delete_audit(self, audit_id: str) -> bool:
        """Delete an audit from SQLite database."""
        with get_connection() as connection:
            cursor = connection.execute("DELETE FROM governance_audits WHERE id = ?", (audit_id,))
            return cursor.rowcount > 0

    def export_audit(self, audit: SafetyAuditRecord, export_format: str = "markdown") -> str:
        """Export audit report in Markdown or JSON."""
        return self.tool.export(audit, export_format=export_format)

    def _save_audit(self, record: SafetyAuditRecord) -> None:
        """Persist safety audit into SQLite governance_audits table."""
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO governance_audits (
                    id, action_title, target_system, overall_risk_score, risk_tier, status, audit_json, initiator, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    status = excluded.status,
                    audit_json = excluded.audit_json,
                    overall_risk_score = excluded.overall_risk_score,
                    risk_tier = excluded.risk_tier
                """,
                (
                    record.id,
                    record.action_title,
                    record.target_system,
                    record.overall_risk_score,
                    record.risk_tier,
                    record.approval.status,
                    json.dumps(record.model_dump()),
                    record.initiator,
                    record.timestamp,
                ),
            )
