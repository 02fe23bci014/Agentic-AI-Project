import json
from typing import Any
from fastapi import APIRouter, HTTPException, Query

from backend.agents.cloud_operations_agent import CloudOperationsAgent
from backend.database.connection import get_connection
from backend.models.cloud_ops import (
    ApplyRemediationRequest,
    DiagnosisReport,
    DiagnosisRequest,
    PostmortemExportRequest,
    RemediationResult,
)
from backend.tools.cloud_ops_tool import CloudOpsTool

router = APIRouter()
agent = CloudOperationsAgent()
tool = CloudOpsTool()


@router.post("/diagnose", response_model=DiagnosisReport)
def diagnose_failed_deployment(request: DiagnosisRequest) -> DiagnosisReport:
    """
    Lab 10: Cloud Operations Agent.
    Diagnose deployment crash logs and configuration, perform Root Cause Analysis (RCA),
    and generate actionable remediation steps with unified diff patches.
    """
    try:
        report = agent.diagnose_and_fix(request)
        return report
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Deployment diagnosis failed: {exc}",
        )


@router.get("/incidents")
def list_incident_reports(
    status: str | None = None,
    severity: str | None = None,
    created_by: str | None = None,
) -> list[dict[str, Any]]:
    """Retrieve all logged cloud deployment incidents and diagnostics."""
    query = """
        SELECT id, service_name, environment, severity, error_category, root_cause, status, created_by, created_at
        FROM cloud_incidents
    """
    conditions = []
    params = []

    if status and isinstance(status, str):
        conditions.append("status = ?")
        params.append(status)

    if severity and isinstance(severity, str):
        conditions.append("severity = ?")
        params.append(severity)

    if created_by and isinstance(created_by, str):
        conditions.append("created_by = ?")
        params.append(created_by)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY created_at DESC"

    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()

    incidents = []
    for row in rows:
        incidents.append({
            "id": row[0],
            "service_name": row[1],
            "environment": row[2],
            "severity": row[3],
            "error_category": row[4],
            "root_cause": row[5],
            "status": row[6],
            "created_by": row[7],
            "created_at": row[8],
        })
    return incidents


@router.get("/incidents/{incident_id}", response_model=DiagnosisReport)
def get_incident_report(incident_id: str) -> DiagnosisReport:
    """Retrieve the full diagnosis and remediation report by incident ID."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT report_json FROM cloud_incidents WHERE id = ?",
            (incident_id,),
        ).fetchone()

    if not row:
        raise HTTPException(
            status_code=404,
            detail=f"Incident '{incident_id}' was not found.",
        )

    report_dict = json.loads(row[0])
    return DiagnosisReport(**report_dict)


@router.post("/incidents/{incident_id}/apply", response_model=RemediationResult)
def apply_incident_remediation(incident_id: str, request: ApplyRemediationRequest | None = None) -> RemediationResult:
    """
    Execute automated rolling redeployment and simulated health verification probes.
    """
    try:
        auto_restart = request.auto_restart if request else True
        result = agent.apply_remediation(incident_id, auto_restart=auto_restart)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to apply remediation: {exc}")


@router.delete("/incidents/{incident_id}")
def delete_incident_report(incident_id: str) -> dict[str, Any]:
    """Delete an incident record from the database."""
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM cloud_incidents WHERE id = ?",
            (incident_id,),
        )
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Incident '{incident_id}' was not found.",
            )

    return {"deleted": True, "id": incident_id}


@router.post("/export-postmortem")
def export_postmortem_report(request: PostmortemExportRequest) -> dict[str, str]:
    """
    Export incident diagnosis report to formatted Markdown post-mortem or JSON.
    """
    try:
        content = tool.export(request.report, export_format=request.format)
        return {
            "format": request.format.lower(),
            "content": content,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Postmortem export failed: {exc}",
        )
