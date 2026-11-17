import difflib
import json
import re
from typing import Any
from backend.models.cloud_ops import DiagnosisReport, PatchArtifact


class CloudOpsTool:
    """
    Tool for DevOps failure analysis, diff generation, patch simulation, and post-mortem reporting.
    """

    @staticmethod
    def generate_unified_diff(original: str, patched: str, filename: str = "deployment-config.yaml") -> str:
        """Generate a standard unified diff between original and patched configurations."""
        orig_lines = original.splitlines(keepends=True)
        patch_lines = patched.splitlines(keepends=True)
        diff = difflib.unified_diff(
            orig_lines,
            patch_lines,
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}",
            lineterm="",
        )
        return "".join(diff).strip()

    @staticmethod
    def extract_log_signatures(raw_logs: str) -> dict[str, Any]:
        """Extract key error signatures, exit codes, and stack traces from raw log text."""
        signatures: dict[str, Any] = {
            "exit_codes": [],
            "oom_detected": False,
            "crashloop_detected": False,
            "port_conflict_detected": False,
            "connection_refused_detected": False,
            "permission_denied_detected": False,
            "missing_env_detected": False,
            "error_lines": [],
        }

        # Look for standard exit codes
        exit_codes = re.findall(r"(?:exit code|code|status)[\s:=]+([0-9]{1,3})", raw_logs, re.IGNORECASE)
        signatures["exit_codes"] = list(dict.fromkeys(exit_codes))

        # Pattern matches
        lower_logs = raw_logs.lower()
        if "oomkilled" in lower_logs or "out of memory" in lower_logs or "exit code 137" in lower_logs:
            signatures["oom_detected"] = True
        if "crashloopbackoff" in lower_logs or "back-off restarting failed container" in lower_logs:
            signatures["crashloop_detected"] = True
        if "address already in use" in lower_logs or "port" in lower_logs and "already allocated" in lower_logs:
            signatures["port_conflict_detected"] = True
        if "connection refused" in lower_logs or "econnrefused" in lower_logs:
            signatures["connection_refused_detected"] = True
        if "permission denied" in lower_logs or "eacces" in lower_logs or "forbidden" in lower_logs:
            signatures["permission_denied_detected"] = True
        if "keyerror" in lower_logs or "environment variable" in lower_logs and "not set" in lower_logs or "undefined variable" in lower_logs:
            signatures["missing_env_detected"] = True

        # Extract highlighted error lines
        for line in raw_logs.splitlines():
            line_str = line.strip()
            if any(term in line_str.lower() for term in ["error", "fatal", "exception", "failed", "panic", "crash", "oom", "terminated", "kill"]):
                signatures["error_lines"].append(line_str[:200])

        # Keep top 10 unique error lines
        signatures["error_lines"] = list(dict.fromkeys(signatures["error_lines"]))[:10]
        return signatures

    @staticmethod
    def simulate_fix_verification(service_name: str, patches: list[PatchArtifact]) -> str:
        """Simulate applying patch artifacts and running post-deployment health check probes."""
        lines = [
            f"[AgenticPro Cloud-Ops] Initiating automated rolling redeployment for service: '{service_name}'...",
            f"[Config Engine] Validating {len(patches)} patch artifact(s)...",
        ]

        for p in patches:
            lines.append(f"  -> Applied patch to: {p.filename} ({p.file_type.upper()})")

        lines.extend([
            "[Container Runtime] Pulling base image layers: cached [OK]",
            f"[Container Runtime] Starting container for '{service_name}' [OK]",
            f"[Health Probes] HTTP GET /healthz on container port -> 200 OK (latency: 14ms)",
            f"[Health Probes] TCP readiness socket check -> CONNECTED",
            f"[Deployment Status] Zero crash loops detected across 30s observation window.",
            f"[AgenticPro Cloud-Ops] Deployment for '{service_name}' marked HEALTHY and STABLE.",
        ])

        return "\n".join(lines)

    @staticmethod
    def format_postmortem_markdown(report: DiagnosisReport) -> str:
        """Generate an executive Post-Mortem Incident Report in GitHub Flavored Markdown."""
        lines = [
            f"# Post-Mortem Incident Report: {report.service_name} ({report.id})",
            f"",
            f"- **Service Name**: `{report.service_name}`",
            f"- **Environment**: `{report.environment}`",
            f"- **Deployment Target**: `{report.deployment_target}`",
            f"- **Incident Severity**: **{report.rca.severity}**",
            f"- **Error Category**: `{report.rca.error_category}`",
            f"- **Diagnosis Timestamp**: {report.timestamp}",
            f"- **Resolution Status**: `{report.status.upper()}`",
            f"",
            f"---",
            f"",
            f"## 1. Executive Summary",
            f"",
            f"{report.rca.summary}",
            f"",
            f"- **Failing Component**: `{report.rca.failing_service}`",
            f"- **Triggering Signal**: `{report.rca.triggering_event}`",
            f"",
            f"## 2. Root Cause Analysis (RCA)",
            f"",
            f"The deployment failed due to `{report.rca.error_category}`. Downstream components impacted: "
            + (", ".join([f"`{c}`" for c in report.rca.affected_dependencies]) if report.rca.affected_dependencies else "None"),
            f"",
            f"## 3. Step-by-Step Remediation Plan",
            f"",
        ]

        for step in report.remediation_steps:
            lines.append(f"### Step {step.step_number}: {step.action}")
            lines.append(f"- **Explanation**: {step.explanation}")
            lines.append(f"- **Risk Level**: `{step.risk_level}` | **Automated**: `{step.is_automated}`")
            if step.command_or_snippet:
                lines.append(f"```bash\n{step.command_or_snippet}\n```")
            lines.append("")

        if report.patches:
            lines.append("## 4. Remediation Patches & Diffs")
            lines.append("")
            for patch in report.patches:
                lines.append(f"#### File: `{patch.filename}` ({patch.file_type})")
                if patch.diff_patch:
                    lines.append(f"```diff\n{patch.diff_patch}\n```")
                else:
                    lines.append(f"**Remediated Snippet:**\n```yaml\n{patch.patched_snippet}\n```")
                lines.append("")

        lines.extend([
            "## 5. Post-Fix Verification Probes",
            "",
        ])
        for v in report.verification_steps:
            lines.append(f"- [x] {v}")

        lines.extend([
            "",
            "## 6. Preventive Recommendations & Guardrails",
            "",
        ])
        for rec in report.preventive_recommendations:
            lines.append(f"- {rec}")

        return "\n".join(lines)

    @staticmethod
    def format_postmortem_json(report: DiagnosisReport) -> str:
        """Export report as formatted JSON string."""
        return json.dumps(report.model_dump(), indent=2)

    def export(self, report: DiagnosisReport, export_format: str = "markdown") -> str:
        """Export report to requested format."""
        if export_format.lower().strip() == "json":
            return self.format_postmortem_json(report)
        return self.format_postmortem_markdown(report)
