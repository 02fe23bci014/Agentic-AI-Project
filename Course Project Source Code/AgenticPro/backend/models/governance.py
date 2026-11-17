from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class PolicyEvalCheck(BaseModel):
    rule_id: str = Field(description="Policy identifier e.g. POL-SEC-01")
    name: str = Field(description="Name of the safety policy")
    category: str = Field(description="'Security', 'Privacy', 'Reliability', 'Compliance'")
    status: str = Field(description="'PASS', 'WARN', 'FAIL'")
    details: str = Field(description="Evaluation findings or violation explanation")
    remediation_hint: str | None = Field(default=None, description="Suggested policy alignment fix")


class RiskDimension(BaseModel):
    name: str = Field(description="Dimension name (e.g. Data Privacy, System Stability, Privilege Escalation)")
    score: int = Field(ge=0, le=100, description="Risk score 0-100")
    tier: str = Field(description="'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'")
    rationale: str = Field(description="Why this score was assigned")


class RollbackStep(BaseModel):
    order: int = Field(ge=1, description="Execution order")
    action: str = Field(description="Imperative rollback action")
    command: str | None = Field(default=None, description="Automated shell command or SQL statement")
    verification: str = Field(description="How to verify rollback success")
    estimated_seconds: int = Field(default=30, description="Estimated duration in seconds")


class RollbackPlan(BaseModel):
    strategy: str = Field(description="'Automated Revert', 'Canary Drain', 'Snapshot Restore', 'Circuit Breaker'")
    estimated_rto_seconds: int = Field(description="Recovery Time Objective (RTO) in seconds")
    steps: list[RollbackStep] = Field(default_factory=list)
    state_checkpoint: str | None = Field(default=None, description="Snapshot ID or commit hash to restore")


class ApprovalDecision(BaseModel):
    status: str = Field(description="'PENDING_REVIEW', 'APPROVED', 'REJECTED', 'AUTO_APPROVED', 'ESCALATED'")
    reviewer: str | None = Field(default=None, description="Reviewer username")
    decision_notes: str | None = Field(default=None, description="Approval or rejection explanation")
    decided_at: str | None = Field(default=None, description="Timestamp of decision")
    required_approvers: list[str] = Field(default_factory=list, description="Roles required for approval")


class GovernanceAssessmentRequest(BaseModel):
    action_title: str = Field(min_length=3, description="Title of proposed action or deployment")
    target_system: str = Field(default="production", description="'production', 'staging', 'database', 'infrastructure'")
    proposed_payload: str = Field(min_length=5, description="Code diff, shell commands, SQL script, or agent prompt")
    initiator: str | None = Field(default=None, description="Agent or user submitting the action")
    declared_purpose: str = Field(default="", description="Business context or functional justification")


class SafetyAuditRecord(BaseModel):
    id: str = Field(description="Unique audit ID e.g. gov-20261117-01")
    action_title: str
    target_system: str
    proposed_payload: str
    initiator: str
    declared_purpose: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    overall_risk_score: int = Field(ge=0, le=100, description="Aggregate risk rating 0-100")
    risk_tier: str = Field(description="'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'")
    risk_dimensions: list[RiskDimension] = Field(default_factory=list)
    policy_evaluations: list[PolicyEvalCheck] = Field(default_factory=list)
    approval: ApprovalDecision
    rollback_plan: RollbackPlan
    rollback_executed: bool = Field(default=False)
    rollback_logs: str | None = Field(default=None)


class RecordDecisionRequest(BaseModel):
    decision: str = Field(description="'APPROVED', 'REJECTED', 'ESCALATED'")
    reviewer: str = Field(description="Reviewer username")
    notes: str = Field(default="", description="Decision comments")


class ExecuteRollbackRequest(BaseModel):
    reason: str = Field(description="Reason for triggering rollback")
    executor: str = Field(description="User triggering rollback")


class GovernanceExportRequest(BaseModel):
    audit: SafetyAuditRecord
    format: str = Field(default="markdown", description="'markdown' or 'json'")
