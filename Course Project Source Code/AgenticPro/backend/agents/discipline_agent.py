import json
from datetime import datetime
from typing import Any
from backend.database.connection import get_connection
from backend.models.discipline import (
    ComplianceCheck,
    DerivationStep,
    DisciplineWorkletArtifact,
    EngineeringKPI,
    ParameterItem,
    WorkletSolveRequest,
)
from backend.skills.discipline_agents.skill import DisciplineSpecificSkill
from backend.tools.discipline_tool import DisciplineTool


class DisciplineSpecificAgent:
    """
    Lab 13: Discipline-Specific Agents (ME / CE / EE domain worklet).
    Automates engineering calculations, governing formulas, analytical derivations,
    code compliance evaluations, and Python simulation scripts for Mechanical,
    Civil, and Electrical Engineering.
    """

    def __init__(self):
        self.skill = DisciplineSpecificSkill()
        self.tool = DisciplineTool()

    def solve_worklet(self, request: WorkletSolveRequest) -> DisciplineWorkletArtifact:
        """Synthesize and solve discipline-specific engineering worklet."""
        raw = self.skill.generate(
            discipline=request.discipline,
            worklet_type=request.worklet_type,
            title=request.title,
            parameters=request.parameters,
            problem_statement=request.problem_statement or "",
            unit_system=request.unit_system,
            user_id=request.user_id,
        )

        params = [ParameterItem(**p) for p in raw.get("parameters", [])]
        derivations = [DerivationStep(**s) for s in raw.get("derivation_steps", [])]
        kpis = [EngineeringKPI(**k) for k in raw.get("kpis", [])]
        checks = [ComplianceCheck(**c) for c in raw.get("compliance_checks", [])]

        worklet_id = raw.get("id") or f"wrk-{request.discipline.lower()}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        artifact = DisciplineWorkletArtifact(
            id=worklet_id,
            discipline=request.discipline.upper(),
            worklet_type=raw.get("worklet_type", request.worklet_type),
            title=raw.get("title", request.title or "Engineering Calculation Worklet"),
            problem_statement=raw.get("problem_statement", ""),
            parameters=params,
            governing_equations=raw.get("governing_equations", []),
            derivation_steps=derivations,
            kpis=kpis,
            compliance_checks=checks,
            compliance_verdict=raw.get("compliance_verdict", "COMPLIANT"),
            executable_code=raw.get("executable_code", ""),
            code_execution_stdout=None,
            schematic_svg_or_ascii=raw.get("schematic_svg_or_ascii"),
            created_by=request.user_id or "discipline_agent",
            created_at=datetime.utcnow().isoformat(),
        )

        # Run verification code simulation if requested
        if request.run_code_simulation and artifact.executable_code:
            stdout_log = self.tool.execute_python_verification(artifact.executable_code)
            artifact.code_execution_stdout = stdout_log

        self._save_worklet(artifact)
        return artifact

    def run_code(self, worklet_id: str, custom_code: str | None = None) -> DisciplineWorkletArtifact:
        """Execute or re-run Python verification script in sandbox."""
        artifact = self.get_worklet(worklet_id)
        code_to_run = custom_code or artifact.executable_code

        if custom_code:
            artifact.executable_code = custom_code

        stdout_log = self.tool.execute_python_verification(code_to_run)
        artifact.code_execution_stdout = stdout_log

        self._save_worklet(artifact)
        return artifact

    def get_worklet(self, worklet_id: str) -> DisciplineWorkletArtifact:
        """Fetch worklet artifact by ID."""
        with get_connection() as connection:
            row = connection.execute(
                "SELECT worklet_json FROM discipline_worklets WHERE id = ?",
                (worklet_id,),
            ).fetchone()

        if not row:
            raise ValueError(f"Discipline worklet '{worklet_id}' not found.")

        data = json.loads(row[0])
        return DisciplineWorkletArtifact(**data)

    def list_worklets(self, discipline: str | None = None, worklet_type: str | None = None) -> list[dict[str, Any]]:
        """List historical discipline worklets."""
        query = """
            SELECT id, discipline, worklet_type, title, status, compliance_verdict, created_by, created_at
            FROM discipline_worklets
        """
        conditions = []
        params = []
        if discipline and isinstance(discipline, str):
            conditions.append("discipline = ?")
            params.append(discipline.upper())
        if worklet_type and isinstance(worklet_type, str):
            conditions.append("worklet_type = ?")
            params.append(worklet_type)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY created_at DESC"

        with get_connection() as connection:
            rows = connection.execute(query, params).fetchall()

        worklets = []
        for r in rows:
            worklets.append({
                "id": r[0],
                "discipline": r[1],
                "worklet_type": r[2],
                "title": r[3],
                "status": r[4],
                "compliance_verdict": r[5],
                "created_by": r[6],
                "created_at": r[7],
            })
        return worklets

    def delete_worklet(self, worklet_id: str) -> bool:
        """Delete worklet record from SQLite database."""
        with get_connection() as connection:
            cursor = connection.execute("DELETE FROM discipline_worklets WHERE id = ?", (worklet_id,))
            return cursor.rowcount > 0

    def export_worklet(self, worklet: DisciplineWorkletArtifact, export_format: str = "markdown") -> str:
        """Export worklet report in Markdown or JSON format."""
        if export_format.lower() == "json":
            return self.tool.format_worklet_json(worklet)
        return self.tool.format_worklet_markdown(worklet)

    def _save_worklet(self, artifact: DisciplineWorkletArtifact) -> None:
        """Persist worklet artifact into SQLite discipline_worklets table."""
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO discipline_worklets (
                    id, discipline, worklet_type, title, status, compliance_verdict, worklet_json, created_by, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    status = excluded.status,
                    compliance_verdict = excluded.compliance_verdict,
                    worklet_json = excluded.worklet_json
                """,
                (
                    artifact.id,
                    artifact.discipline,
                    artifact.worklet_type,
                    artifact.title,
                    "computed",
                    artifact.compliance_verdict,
                    json.dumps(artifact.model_dump()),
                    artifact.created_by,
                    artifact.created_at,
                ),
            )
