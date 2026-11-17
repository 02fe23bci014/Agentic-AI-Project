import io
import json
import math
import sys
from typing import Any
from backend.models.discipline import (
    ComplianceCheck,
    DerivationStep,
    DisciplineWorkletArtifact,
    EngineeringKPI,
    ParameterItem,
)


class DisciplineTool:
    """
    Engineering discipline calculation, derivation, simulation execution, and reporting tool
    for Mechanical Engineering (ME), Civil Engineering (CE), and Electrical Engineering (EE).
    """

    @staticmethod
    def execute_python_verification(code: str) -> str:
        """
        Execute generated Python verification code in a controlled namespace
        and return the captured standard output.
        """
        buffer = io.StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = buffer
            local_scope: dict[str, Any] = {"math": math}
            exec(code, local_scope)
            output = buffer.getvalue().strip()
            return output if output else "[Simulation Execution: Succeeded with 0 console warnings]"
        except Exception as exc:
            return f"[Execution Error]: {type(exc).__name__}: {exc}"
        finally:
            sys.stdout = old_stdout

    @staticmethod
    def format_worklet_markdown(worklet: DisciplineWorkletArtifact) -> str:
        """Format an engineering calculation worklet report in GitHub Flavored Markdown with KaTeX math."""
        disc_label = {
            "ME": "Mechanical Engineering",
            "CE": "Civil Engineering",
            "EE": "Electrical Engineering",
        }.get(worklet.discipline, worklet.discipline)

        lines = [
            f"# {disc_label} Worklet: {worklet.title}",
            f"",
            f"- **Worklet ID**: `{worklet.id}`",
            f"- **Discipline**: `{worklet.discipline}` ({disc_label})",
            f"- **Worklet Type**: `{worklet.worklet_type}`",
            f"- **Compliance Status**: **{worklet.compliance_verdict}**",
            f"- **Generated At**: {worklet.created_at}",
            f"",
            f"---",
            f"",
            f"## 1. Problem Statement & Context",
            f"",
            f"{worklet.problem_statement}",
            f"",
            f"## 2. Input Parameters",
            f"",
            f"| Parameter | Symbol | Value | Unit | Description |",
            f"|---|---|---|---|---|",
        ]

        for p in worklet.parameters:
            lines.append(f"| **{p.name}** | `${p.symbol}$` | `{p.value}` | `{p.unit}` | {p.description} |")

        lines.extend([
            f"",
            f"## 3. Governing Equations",
            f"",
        ])
        for eq in worklet.governing_equations:
            lines.append(f"- $${eq}$$")

        lines.extend([
            f"",
            f"## 4. Step-by-Step Analytical Derivations",
            f"",
        ])
        for step in worklet.derivation_steps:
            lines.append(f"### Step {step.step_number}: {step.title}")
            lines.append(f"- **Formula**: $${step.formula}$$")
            lines.append(f"- **Substitution**: {step.substitution}")
            lines.append(f"- **Computed Value**: **`{step.result_value}` {step.unit}**")
            if step.notes:
                lines.append(f"- *Note*: {step.notes}")
            lines.append("")

        lines.extend([
            f"## 5. Key Engineering Performance Indicators (KPIs)",
            f"",
            f"| KPI Metric | Value | Unit | Status |",
            f"|---|---|---|---|",
        ])
        for kpi in worklet.kpis:
            lines.append(f"| **{kpi.label}** | `{kpi.value}` | `{kpi.unit}` | `{kpi.status}` |")

        lines.extend([
            f"",
            f"## 6. Code Compliance & Safety Checks",
            f"",
            f"| Regulatory Code | Evaluated Metric | Threshold Rule | Observed Value | Verdict |",
            f"|---|---|---|---|---|",
        ])
        for chk in worklet.compliance_checks:
            lines.append(f"| `{chk.standard_code}` | {chk.parameter_checked} | `{chk.threshold}` | `{chk.actual_value}` | **{chk.status}** |")

        lines.extend([
            f"",
            f"## 7. Python Verification Script",
            f"",
            f"```python",
            f"{worklet.executable_code}",
            f"```",
        ])

        if worklet.code_execution_stdout:
            lines.extend([
                f"",
                f"### Execution Simulation Output",
                f"```text",
                f"{worklet.code_execution_stdout}",
                f"```",
            ])

        return "\n".join(lines)

    @staticmethod
    def format_worklet_json(worklet: DisciplineWorkletArtifact) -> str:
        """Serialize engineering worklet as JSON."""
        return json.dumps(worklet.model_dump(), indent=2)
