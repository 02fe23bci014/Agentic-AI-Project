import json
from datetime import datetime
from typing import Any

from backend.database.connection import get_connection
from backend.models.cloud_ops import (
    DiagnosisReport,
    DiagnosisRequest,
    PatchArtifact,
    RemediationResult,
    RemediationStep,
    RootCauseAnalysis,
)
from backend.skills.cloud_operations.skill import CloudOperationsSkill
from backend.tools.cloud_ops_tool import CloudOpsTool


class CloudOperationsAgent:
    """
    Lab 10: Cloud Operations Agent.
    Autonomous DevOps and SRE agent responsible for diagnosing failed deployments,
    performing Root Cause Analysis (RCA), and generating verified remediation patches.
    """

    def __init__(self):
        self.skill = CloudOperationsSkill()
        self.tool = CloudOpsTool()

    def diagnose_and_fix(self, request: DiagnosisRequest) -> DiagnosisReport:
        """
        Diagnose a failed deployment from logs and configuration, synthesize RCA,
        and generate a verified step-by-step remediation plan with unified diff patches.
        """
        raw = self.skill.generate(
            service_name=request.service_name,
            environment=request.environment,
            deployment_target=request.deployment_target,
            raw_logs=request.raw_logs,
            deployment_config=request.deployment_config,
            incident_type=request.incident_type,
        )

        rca_data = raw.get("rca", {})
        rca = RootCauseAnalysis(
            summary=rca_data.get("summary", "Deployment failure diagnosed."),
            error_category=rca_data.get("error_category", "CrashLoopBackOff"),
            severity=rca_data.get("severity", "High"),
            failing_service=rca_data.get("failing_service", request.service_name),
            triggering_event=rca_data.get("triggering_event", "Unknown fatal signal"),
            affected_dependencies=rca_data.get("affected_dependencies", []),
        )

        steps: list[RemediationStep] = []
        for idx, s in enumerate(raw.get("remediation_steps", [])):
            steps.append(
                RemediationStep(
                    step_number=s.get("step_number", idx + 1),
                    action=s.get("action", f"Step {idx + 1}"),
                    explanation=s.get("explanation", ""),
                    command_or_snippet=s.get("command_or_snippet"),
                    risk_level=s.get("risk_level", "Low"),
                    is_automated=s.get("is_automated", True),
                )
            )

        patches: list[PatchArtifact] = []
        for p in raw.get("patches", []):
            orig = p.get("original_snippet", "")
            patched = p.get("patched_snippet", "")
            fname = p.get("filename", "config.yaml")
            diff = p.get("diff_patch") or self.tool.generate_unified_diff(orig, patched, filename=fname)

            patches.append(
                PatchArtifact(
                    filename=fname,
                    file_type=p.get("file_type", "yaml"),
                    original_snippet=orig,
                    patched_snippet=patched,
                    diff_patch=diff,
                )
            )

        report_id = raw.get("id") or f"inc-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        report = DiagnosisReport(
            id=report_id,
            service_name=request.service_name,
            environment=request.environment,
            deployment_target=request.deployment_target,
            timestamp=datetime.utcnow().isoformat(),
            rca=rca,
            remediation_steps=steps,
            patches=patches,
            verification_steps=raw.get("verification_steps", []),
            preventive_recommendations=raw.get("preventive_recommendations", []),
            status="diagnosed",
        )

        # Persist incident report in SQLite
        self._save_incident(report, created_by=request.user_id)

        return report

    def apply_remediation(self, incident_id: str, auto_restart: bool = True) -> RemediationResult:
        """
        Execute or simulate applying the synthesized remediation patch and verify health.
        """
        with get_connection() as connection:
            row = connection.execute(
                "SELECT report_json, service_name FROM cloud_incidents WHERE id = ?",
                (incident_id,),
            ).fetchone()

        if not row:
            raise ValueError(f"Incident '{incident_id}' not found.")

        report_dict = json.loads(row[0])
        report = DiagnosisReport(**report_dict)

        # Run simulated verification
        verification_log = self.tool.simulate_fix_verification(
            service_name=report.service_name,
            patches=report.patches,
        )

        # Update status in database
        report.status = "remediated"
        with get_connection() as connection:
            connection.execute(
                "UPDATE cloud_incidents SET status = ?, report_json = ? WHERE id = ?",
                ("remediated", json.dumps(report.model_dump()), incident_id),
            )

        return RemediationResult(
            incident_id=incident_id,
            status="remediated",
            success=True,
            patches_applied=[p.filename for p in report.patches],
            verification_logs=verification_log,
            applied_at=datetime.utcnow().isoformat(),
        )

    def _save_incident(self, report: DiagnosisReport, created_by: str | None = None) -> None:
        """Store incident diagnosis in SQLite cloud_incidents table."""
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO cloud_incidents (
                    id, service_name, environment, severity, error_category, root_cause, report_json, status, created_by, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    status = excluded.status,
                    report_json = excluded.report_json,
                    severity = excluded.severity
                """,
                (
                    report.id,
                    report.service_name,
                    report.environment,
                    report.rca.severity,
                    report.rca.error_category,
                    report.rca.summary,
                    json.dumps(report.model_dump()),
                    report.status,
                    created_by,
                    report.timestamp,
                ),
            )

    def export_postmortem(self, report: DiagnosisReport, export_format: str = "markdown") -> str:
        """Export post-mortem report to markdown or json."""
        return self.tool.export(report, export_format=export_format)
