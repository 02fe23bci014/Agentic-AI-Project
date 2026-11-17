import uuid
from typing import Any
from backend.tools.governance_tool import GovernanceTool


class SafetyGovernanceSynthesizer:
    """
    High-fidelity deterministic domain synthesizer for Safety & Governance.
    Analyzes risk vectors, policy compliance, approval criteria, and rollback strategies.
    """

    def __init__(self):
        self.tool = GovernanceTool()

    def synthesize(
        self,
        action_title: str,
        target_system: str = "production",
        proposed_payload: str = "",
        initiator: str = "agent",
        declared_purpose: str = "",
    ) -> dict[str, Any]:
        signatures = self.tool.scan_security_signatures(proposed_payload)
        policies = self.tool.evaluate_policies(action_title, target_system, proposed_payload, signatures)

        # Calculate scores
        sec_score = 15
        ops_score = 20
        priv_score = 10

        lower_payload = proposed_payload.lower()
        lower_title = action_title.lower()

        # Security dimension
        if signatures["has_credential_leaks"]:
            sec_score += 45
        if signatures["has_privilege_escalation"]:
            sec_score += 40
        if signatures["has_unsafe_network_egress"]:
            sec_score += 25

        # Operational stability dimension
        if signatures["has_destructive_ops"]:
            ops_score += 55
        if target_system.lower() == "production":
            ops_score += 25
        if "migration" in lower_title or "database" in lower_title or "alter table" in lower_payload:
            ops_score += 35

        # Data privacy dimension
        if "pii" in lower_payload or "email" in lower_payload or "ssn" in lower_payload or "credit_card" in lower_payload:
            priv_score += 50
        if "user" in lower_payload and "select *" in lower_payload:
            priv_score += 30

        sec_score = min(100, sec_score)
        ops_score = min(100, ops_score)
        priv_score = min(100, priv_score)

        # Weighted aggregate risk score
        overall_score = int(sec_score * 0.40 + ops_score * 0.40 + priv_score * 0.20)

        # Determine Tier
        if overall_score >= 80 or signatures["has_destructive_ops"]:
            tier = "CRITICAL" if signatures["has_destructive_ops"] and target_system.lower() == "production" else "HIGH"
        elif overall_score >= 50:
            tier = "MEDIUM"
        else:
            tier = "LOW"

        risk_dimensions = [
            {
                "name": "Security & Vulnerability",
                "score": sec_score,
                "tier": "CRITICAL" if sec_score >= 80 else "HIGH" if sec_score >= 60 else "MEDIUM" if sec_score >= 35 else "LOW",
                "rationale": "High vulnerability detected" if sec_score >= 60 else "Nominal security parameters observed.",
            },
            {
                "name": "Operational Stability",
                "score": ops_score,
                "tier": "CRITICAL" if ops_score >= 80 else "HIGH" if ops_score >= 60 else "MEDIUM" if ops_score >= 35 else "LOW",
                "rationale": "Destructive operations on active systems" if ops_score >= 60 else "Controlled operational blast radius.",
            },
            {
                "name": "Data Privacy & Compliance",
                "score": priv_score,
                "tier": "CRITICAL" if priv_score >= 80 else "HIGH" if priv_score >= 60 else "MEDIUM" if priv_score >= 35 else "LOW",
                "rationale": "Direct sensitive data exposure risk" if priv_score >= 60 else "Compliant with data residency guidelines.",
            },
        ]

        # Approval tier
        if tier in ["CRITICAL", "HIGH"]:
            approval = {
                "status": "PENDING_REVIEW",
                "required_approvers": ["Platform Security Lead", "Faculty Admin"],
                "decision_notes": "High/Critical risk action requires multi-signature human approval before execution.",
            }
        elif tier == "MEDIUM":
            approval = {
                "status": "PENDING_REVIEW",
                "required_approvers": ["DevOps Lead"],
                "decision_notes": "Medium risk action requires single-approver signoff.",
            }
        else:
            approval = {
                "status": "AUTO_APPROVED",
                "required_approvers": [],
                "decision_notes": "Low risk action meets automated pass criteria under Policy POL-GOV-04.",
            }

        # Rollback Plan
        checkpoint_id = f"chk-{uuid.uuid4().hex[:8]}"
        if "migration" in lower_title or "table" in lower_payload:
            rollback_plan = {
                "strategy": "Database Migration Down & Snapshot Restore",
                "estimated_rto_seconds": 45,
                "state_checkpoint": checkpoint_id,
                "steps": [
                    {
                        "order": 1,
                        "action": "Halt Application Traffic on Target Database",
                        "command": "kubectl scale deployment api-gateway --replicas=0 -n " + target_system,
                        "verification": "Verify zero active database connections via pg_stat_activity",
                        "estimated_seconds": 10,
                    },
                    {
                        "order": 2,
                        "action": "Execute Down-Migration Script",
                        "command": "alembic downgrade -1",
                        "verification": "SELECT version_num FROM alembic_version matches pre-migration checkpoint",
                        "estimated_seconds": 15,
                    },
                    {
                        "order": 3,
                        "action": "Resume Service Traffic & Verify Smoke Tests",
                        "command": "kubectl scale deployment api-gateway --replicas=3 -n " + target_system,
                        "verification": "HTTP GET /healthz returns 200 OK",
                        "estimated_seconds": 20,
                    },
                ],
            }
        elif signatures["has_privilege_escalation"] or "chmod" in lower_payload or "sudo" in lower_payload:
            rollback_plan = {
                "strategy": "Security Context Reversion",
                "estimated_rto_seconds": 30,
                "state_checkpoint": checkpoint_id,
                "steps": [
                    {
                        "order": 1,
                        "action": "Revoke Elevated Privileges & Reset File Permissions",
                        "command": "chmod 750 /var/run/secrets && chown -R 10001:10001 /app",
                        "verification": "stat -c '%a %u' /app verifies restricted mode",
                        "estimated_seconds": 10,
                    },
                    {
                        "order": 2,
                        "action": "Redeploy Pod with ReadOnlyRootFilesystem Enforcement",
                        "command": "kubectl rollout restart deployment/secure-app",
                        "verification": "kubectl get pods verifies Running state with non-root UID",
                        "estimated_seconds": 20,
                    },
                ],
            }
        else:
            rollback_plan = {
                "strategy": "Automated Canary Drain & Git Revert",
                "estimated_rto_seconds": 35,
                "state_checkpoint": checkpoint_id,
                "steps": [
                    {
                        "order": 1,
                        "action": "Divert Ingress Traffic from Canary Pods",
                        "command": "kubectl patch service/ingress-router -p '{\"spec\":{\"selector\":{\"version\":\"stable\"}}}'",
                        "verification": "Verify 100% traffic routed to stable baseline",
                        "estimated_seconds": 10,
                    },
                    {
                        "order": 2,
                        "action": "Revert Application Release Image",
                        "command": "kubectl rollout undo deployment/app-service",
                        "verification": "kubectl rollout status deployment/app-service returns success",
                        "estimated_seconds": 25,
                    },
                ],
            }

        audit_id = f"gov-{uuid.uuid4().hex[:8]}"

        return {
            "id": audit_id,
            "action_title": action_title,
            "target_system": target_system,
            "proposed_payload": proposed_payload,
            "initiator": initiator,
            "declared_purpose": declared_purpose,
            "overall_risk_score": overall_score,
            "risk_tier": tier,
            "risk_dimensions": risk_dimensions,
            "policy_evaluations": [p.model_dump() for p in policies],
            "approval": approval,
            "rollback_plan": rollback_plan,
            "rollback_executed": False,
            "rollback_logs": None,
        }
