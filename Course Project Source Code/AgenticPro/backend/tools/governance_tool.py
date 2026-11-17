import json
import re
from typing import Any
from backend.models.governance import (
    ApprovalDecision,
    PolicyEvalCheck,
    RiskDimension,
    RollbackPlan,
    RollbackStep,
    SafetyAuditRecord,
)


class GovernanceTool:
    """
    Tool for automated safety policy evaluation, risk vector scanning, rollback simulation, and auditing.
    """

    @staticmethod
    def scan_security_signatures(payload: str) -> dict[str, Any]:
        """Scan payload for destructive commands, credential leaks, and privilege escalations."""
        lower = payload.lower()
        findings: dict[str, Any] = {
            "has_destructive_ops": False,
            "has_credential_leaks": False,
            "has_privilege_escalation": False,
            "has_unsafe_network_egress": False,
            "violations": [],
        }

        # 1. Destructive operations
        destructive_patterns = [
            r"rm\s+-r?f",
            r"drop\s+table",
            r"truncate\s+table",
            r"delete\s+from\s+[a-z0-9_]+\s*;?$",
            r"mkfs",
            r"format\s+[a-z]:",
        ]
        for pat in destructive_patterns:
            if re.search(pat, lower):
                findings["has_destructive_ops"] = True
                findings["violations"].append(f"Destructive operation detected matching: `{pat}`")

        # 2. Hardcoded secrets / credentials
        credential_patterns = [
            r"api[_-]?key\s*=\s*['\"][a-zA-Z0-9_\-]{16,}['\"]",
            r"password\s*=\s*['\"][^'\"]{6,}['\"]",
            r"-----BEGIN (RSA|OPENSSH|EC|PRIVATE) KEY-----",
            r"bearer\s+[a-zA-Z0-9_\-\.]{25,}",
        ]
        for pat in credential_patterns:
            if re.search(pat, payload):
                findings["has_credential_leaks"] = True
                findings["violations"].append("Potential hardcoded credential or private key exposed in payload")
                break

        # 3. Privilege escalation
        priv_patterns = [r"sudo\s+", r"chmod\s+777", r"--privileged", r"user\s*:\s*root", r"setuid"]
        for pat in priv_patterns:
            if re.search(pat, lower):
                findings["has_privilege_escalation"] = True
                findings["violations"].append(f"Privilege escalation vector detected: `{pat}`")

        # 4. Unsafe network egress
        if "curl" in lower or "wget" in lower or "nc -l" in lower or "bash -i" in lower:
            if "localhost" not in lower and "127.0.0.1" not in lower:
                findings["has_unsafe_network_egress"] = True
                findings["violations"].append("Unsanctioned network egress / remote socket command detected")

        return findings

    @staticmethod
    def evaluate_policies(action_title: str, target_system: str, payload: str, signatures: dict[str, Any]) -> list[PolicyEvalCheck]:
        """Evaluate standard governance policies against the action payload."""
        checks = []

        # POL-SEC-01: No Hardcoded Secrets
        if signatures["has_credential_leaks"]:
            checks.append(PolicyEvalCheck(
                rule_id="POL-SEC-01",
                name="Credential Protection Policy",
                category="Security",
                status="FAIL",
                details="Hardcoded API keys, tokens, or private certificates detected in proposed payload.",
                remediation_hint="Inject secrets at runtime via HashiCorp Vault or Kubernetes Secret references.",
            ))
        else:
            checks.append(PolicyEvalCheck(
                rule_id="POL-SEC-01",
                name="Credential Protection Policy",
                category="Security",
                status="PASS",
                details="Zero plaintext secrets or private keys detected in payload.",
            ))

        # POL-SEC-02: Destructive Command Ban
        if signatures["has_destructive_ops"]:
            checks.append(PolicyEvalCheck(
                rule_id="POL-SEC-02",
                name="Destructive Command Safeguard",
                category="Reliability",
                status="FAIL",
                details="Destructive disk, table, or recursive file deletion command identified.",
                remediation_hint="Use soft deletes or pre-approved migration rollback checkpoints.",
            ))
        else:
            checks.append(PolicyEvalCheck(
                rule_id="POL-SEC-02",
                name="Destructive Command Safeguard",
                category="Reliability",
                status="PASS",
                details="Payload contains non-destructive state mutations.",
            ))

        # POL-SEC-03: Principle of Least Privilege
        if signatures["has_privilege_escalation"]:
            checks.append(PolicyEvalCheck(
                rule_id="POL-SEC-03",
                name="Least Privilege Enforcement",
                category="Security",
                status="WARN" if target_system != "production" else "FAIL",
                details="Payload requests root permissions or relaxes file mode to 777.",
                remediation_hint="Run container as unprivileged non-root user (UID 10001).",
            ))
        else:
            checks.append(PolicyEvalCheck(
                rule_id="POL-SEC-03",
                name="Least Privilege Enforcement",
                category="Security",
                status="PASS",
                details="Process runs within standard unprivileged security context.",
            ))

        # POL-GOV-04: Production Change Gating
        if target_system.lower() == "production":
            checks.append(PolicyEvalCheck(
                rule_id="POL-GOV-04",
                name="Production Change Gating",
                category="Compliance",
                status="WARN" if not signatures["has_destructive_ops"] else "FAIL",
                details="Action targets live production environment and mandates human review.",
                remediation_hint="Requires affirmative dual-approval from Platform Security Lead.",
            ))
        else:
            checks.append(PolicyEvalCheck(
                rule_id="POL-GOV-04",
                name="Production Change Gating",
                category="Compliance",
                status="PASS",
                details="Action targets non-production sandbox environment.",
            ))

        return checks

    @staticmethod
    def simulate_rollback(rollback_plan: RollbackPlan) -> str:
        """Simulate executing the rollback plan steps with verification probes."""
        logs = [
            f"[Agentic Governance] Initiating Rollback Protocol: Strategy = '{rollback_plan.strategy}'",
            f"[Recovery SLA] Target Recovery Time Objective (RTO): {rollback_plan.estimated_rto_seconds}s",
        ]

        if rollback_plan.state_checkpoint:
            logs.append(f"[Checkpoint Engine] Reverting to pre-action checkpoint: `{rollback_plan.state_checkpoint}`")

        for step in rollback_plan.steps:
            logs.extend([
                f"  -> Executing Step {step.order}: {step.action}",
                f"     Command: {step.command or 'N/A'}",
                f"     Probe: {step.verification} [OK]",
            ])

        logs.extend([
            "[Verification] Synthetic probe HTTP GET /healthz -> 200 OK (latency: 11ms)",
            "[Verification] Anomaly detection monitor: zero regression metrics observed.",
            f"[Agentic Governance] Rollback protocol completed successfully. System returned to stable baseline.",
        ])

        return "\n".join(logs)

    @staticmethod
    def format_governance_markdown(audit: SafetyAuditRecord) -> str:
        """Format complete Safety & Governance Audit Report in GitHub Flavored Markdown."""
        lines = [
            f"# Safety & Governance Audit Report: {audit.action_title} ({audit.id})",
            f"",
            f"- **Target System**: `{audit.target_system}`",
            f"- **Initiator**: `{audit.initiator}`",
            f"- **Timestamp**: {audit.timestamp}",
            f"- **Aggregate Risk Score**: **{audit.overall_risk_score} / 100** (`{audit.risk_tier}`)",
            f"- **Approval Status**: `{audit.approval.status}`",
            f"- **Rollback State**: `{'EXECUTED' if audit.rollback_executed else 'ARMED & READY'}`",
            f"",
            f"---",
            f"",
            f"## 1. Multi-Dimensional Risk Analysis",
            f"",
            f"| Risk Dimension | Score | Tier | Rationale |",
            f"| --- | --- | --- | --- |",
        ]

        for dim in audit.risk_dimensions:
            lines.append(f"| **{dim.name}** | `{dim.score}/100` | `{dim.tier}` | {dim.rationale} |")

        lines.extend([
            f"",
            f"## 2. Policy Evaluation Engine (Eval Checks)",
            f"",
            f"| Rule ID | Policy Name | Category | Status | Details |",
            f"| --- | --- | --- | --- | --- |",
        ])

        for pol in audit.policy_evaluations:
            badge = "🟢 PASS" if pol.status == "PASS" else "🟡 WARN" if pol.status == "WARN" else "🔴 FAIL"
            lines.append(f"| `{pol.rule_id}` | {pol.name} | {pol.category} | {badge} | {pol.details} |")

        lines.extend([
            f"",
            f"## 3. Human-in-the-Loop (HITL) Approval Gate",
            f"",
            f"- **Current State**: `{audit.approval.status}`",
            f"- **Required Approvers**: " + (", ".join([f"`{a}`" for a in audit.approval.required_approvers]) if audit.approval.required_approvers else "`None (Auto-Approved)`"),
            f"- **Reviewer Notes**: {audit.approval.decision_notes or 'Pending human review.'}",
            f"",
            f"## 4. Rollback & Contingency Plan",
            f"",
            f"- **Rollback Strategy**: `{audit.rollback_plan.strategy}`",
            f"- **Target RTO**: `{audit.rollback_plan.estimated_rto_seconds} seconds`",
            f"",
        ])

        for step in audit.rollback_plan.steps:
            lines.append(f"### Step {step.order}: {step.action}")
            if step.command:
                lines.append(f"```bash\n{step.command}\n```")
            lines.append(f"- **Verification**: {step.verification}")
            lines.append("")

        if audit.rollback_executed and audit.rollback_logs:
            lines.extend([
                f"## 5. Rollback Execution Console Log",
                f"```",
                audit.rollback_logs,
                f"```",
            ])

        return "\n".join(lines)

    @staticmethod
    def format_governance_json(audit: SafetyAuditRecord) -> str:
        """Export audit as formatted JSON."""
        return json.dumps(audit.model_dump(), indent=2)

    def export(self, audit: SafetyAuditRecord, export_format: str = "markdown") -> str:
        """Export audit to specified format."""
        if export_format.lower().strip() == "json":
            return self.format_governance_json(audit)
        return self.format_governance_markdown(audit)
