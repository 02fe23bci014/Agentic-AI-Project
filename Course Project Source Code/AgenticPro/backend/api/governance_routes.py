from typing import Any
from fastapi import APIRouter, HTTPException

from backend.agents.governance_agent import SafetyGovernanceAgent
from backend.models.governance import (
    ExecuteRollbackRequest,
    GovernanceAssessmentRequest,
    GovernanceExportRequest,
    RecordDecisionRequest,
    SafetyAuditRecord,
)
from backend.tools.governance_tool import GovernanceTool

router = APIRouter()
agent = SafetyGovernanceAgent()
tool = GovernanceTool()


@router.post("/assess", response_model=SafetyAuditRecord)
def assess_action_safety(request: GovernanceAssessmentRequest) -> SafetyAuditRecord:
    """
    Lab 12: Safety & Governance Agent.
    Evaluates proposed actions for multi-dimensional risks, validates policy compliance,
    determines human approval requirements, and constructs a deterministic rollback plan.
    """
    try:
        record = agent.assess_action(request)
        return record
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Safety governance assessment failed: {exc}",
        )


@router.get("/audits")
def list_safety_audits(
    status: str | None = None,
    risk_tier: str | None = None,
) -> list[dict[str, Any]]:
    """Retrieve all safety & governance audit records."""
    return agent.list_audits(status=status, risk_tier=risk_tier)


@router.get("/audits/{audit_id}", response_model=SafetyAuditRecord)
def get_safety_audit(audit_id: str) -> SafetyAuditRecord:
    """Retrieve full safety audit record by ID."""
    try:
        return agent.get_audit(audit_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/audits/{audit_id}/decision", response_model=SafetyAuditRecord)
def record_approval_decision(audit_id: str, request: RecordDecisionRequest) -> SafetyAuditRecord:
    """
    Record human-in-the-loop (HITL) approval, rejection, or escalation decision.
    """
    try:
        return agent.record_decision(
            audit_id=audit_id,
            decision=request.decision,
            reviewer=request.reviewer,
            notes=request.notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to record decision: {exc}")


@router.post("/audits/{audit_id}/rollback", response_model=SafetyAuditRecord)
def execute_audit_rollback(audit_id: str, request: ExecuteRollbackRequest) -> SafetyAuditRecord:
    """
    Execute simulated rollback plan to revert system back to pre-incident baseline.
    """
    try:
        return agent.execute_rollback(
            audit_id=audit_id,
            reason=request.reason,
            executor=request.executor,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Rollback execution failed: {exc}")


@router.delete("/audits/{audit_id}")
def delete_safety_audit(audit_id: str) -> dict[str, Any]:
    """Delete a safety audit record from the database."""
    deleted = agent.delete_audit(audit_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Audit '{audit_id}' not found.")
    return {"deleted": True, "id": audit_id}


@router.post("/export-report")
def export_governance_report(request: GovernanceExportRequest) -> dict[str, str]:
    """Export safety governance audit report in Markdown or JSON format."""
    try:
        content = tool.export(request.audit, export_format=request.format)
        return {
            "format": request.format.lower(),
            "content": content,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Export failed: {exc}")
