import unittest
from backend.agents.governance_agent import SafetyGovernanceAgent
from backend.agents.swarm_adapters import create_safety_governance_swarm_agent
from backend.api.governance_routes import (
    assess_action_safety,
    delete_safety_audit,
    execute_audit_rollback,
    export_governance_report,
    get_safety_audit,
    list_safety_audits,
    record_approval_decision,
)
from backend.models.governance import (
    ApprovalDecision,
    ExecuteRollbackRequest,
    GovernanceAssessmentRequest,
    GovernanceExportRequest,
    PolicyEvalCheck,
    RecordDecisionRequest,
    RiskDimension,
    RollbackPlan,
    RollbackStep,
    SafetyAuditRecord,
)
from backend.skills.safety_governance.prompt_builder import SafetyGovernancePromptBuilder
from backend.skills.safety_governance.synthesizer import SafetyGovernanceSynthesizer
from backend.skills.safety_governance.validator import SafetyGovernanceValidator
from backend.tools.governance_tool import GovernanceTool


class TestSafetyGovernanceComponents(unittest.TestCase):
    """Test suite for Lab 12: Safety & Governance (Risk, approval, eval, rollback plan)."""

    def setUp(self):
        self.tool = GovernanceTool()
        self.validator = SafetyGovernanceValidator()
        self.builder = SafetyGovernancePromptBuilder()
        self.synthesizer = SafetyGovernanceSynthesizer()
        self.agent = SafetyGovernanceAgent()

    def test_models_creation(self):
        check = PolicyEvalCheck(
            rule_id="POL-SEC-01",
            name="No Hardcoded Secrets",
            category="Security",
            status="PASS",
            details="No secrets detected",
        )
        self.assertEqual(check.rule_id, "POL-SEC-01")

        dim = RiskDimension(
            name="Data Loss Risk",
            score=85,
            tier="HIGH",
            rationale="Schema modification on primary database table",
        )
        self.assertEqual(dim.tier, "HIGH")

        step = RollbackStep(
            order=1,
            action="Restore database snapshot",
            command="aws rds restore-db-instance-to-point-in-time",
            verification="SELECT count(*) FROM users",
            estimated_seconds=120,
        )
        self.assertEqual(step.order, 1)

        plan = RollbackPlan(
            strategy="Snapshot Restore",
            estimated_rto_seconds=120,
            steps=[step],
        )
        self.assertEqual(plan.strategy, "Snapshot Restore")

        decision = ApprovalDecision(
            status="PENDING_REVIEW",
            required_approvers=["Lead SRE", "Security Architect"],
        )
        self.assertEqual(decision.status, "PENDING_REVIEW")

    def test_tool_scan_security_signatures(self):
        destructive_code = "DROP TABLE users CASCADE; rm -rf /var/data"
        findings = self.tool.scan_security_signatures(destructive_code)
        self.assertTrue(findings["has_destructive_ops"])
        self.assertGreaterEqual(len(findings["violations"]), 1)

        secret_code = 'api_key = "sk_live_998877665544332211"'
        sec_findings = self.tool.scan_security_signatures(secret_code)
        self.assertTrue(sec_findings["has_credential_leaks"])

        priv_code = "sudo chmod 777 /etc/shadow"
        priv_findings = self.tool.scan_security_signatures(priv_code)
        self.assertTrue(priv_findings["has_privilege_escalation"])

        safe_code = "SELECT id, username FROM users WHERE is_active = 1 LIMIT 50;"
        safe_findings = self.tool.scan_security_signatures(safe_code)
        self.assertFalse(safe_findings["has_destructive_ops"])
        self.assertFalse(safe_findings["has_credential_leaks"])

    def test_tool_policy_evaluation_and_rollback_simulation(self):
        prod_drop = "ALTER TABLE orders DROP COLUMN customer_ssn;"
        signatures = self.tool.scan_security_signatures(prod_drop)
        checks = self.tool.evaluate_policies("Drop SSN column", "production", prod_drop, signatures)
        self.assertTrue(any(c.status in ("WARN", "FAIL") for c in checks))

        plan = RollbackPlan(
            strategy="Automated Revert",
            estimated_rto_seconds=45,
            steps=[
                RollbackStep(order=1, action="Revert git commit", command="git revert HEAD --no-edit", verification="git status"),
                RollbackStep(order=2, action="Redeploy service", command="kubectl rollout undo deployment/api", verification="kubectl rollout status"),
            ],
        )
        logs = self.tool.simulate_rollback(plan)
        self.assertIn("Step 1", logs)
        self.assertIn("completed successfully", logs)

    def test_validator_and_synthesizer_destructive_action(self):
        high_risk_data = self.synthesizer.synthesize(
            action_title="Drop legacy customer billing archive",
            target_system="production",
            proposed_payload="DROP TABLE billing_archive_2025; rm -rf /mnt/backups",
            initiator="auto_cleaner_agent",
        )
        self.assertTrue(self.validator.validate(high_risk_data))
        self.assertIn(high_risk_data["risk_tier"], ("HIGH", "CRITICAL"))
        self.assertEqual(high_risk_data["approval"]["status"], "PENDING_REVIEW")
        self.assertGreaterEqual(len(high_risk_data["rollback_plan"]["steps"]), 1)

    def test_validator_and_synthesizer_benign_action(self):
        low_risk_data = self.synthesizer.synthesize(
            action_title="Update button CSS padding",
            target_system="staging",
            proposed_payload="button.submit { padding: 8px 16px; background: #2563eb; }",
            initiator="frontend_dev",
        )
        self.assertTrue(self.validator.validate(low_risk_data))
        self.assertIn(low_risk_data["risk_tier"], ("LOW", "MEDIUM"))

    def test_agent_lifecycle_and_persistence(self):
        req = GovernanceAssessmentRequest(
            action_title="Deploy Database Migration for Tenant Partitioning",
            target_system="production",
            proposed_payload="ALTER TABLE tenants ADD COLUMN storage_quota_gb INT DEFAULT 100;",
            initiator="platform_bot",
            declared_purpose="Support tier-based resource partitioning",
        )
        audit = self.agent.assess_action(req)
        self.assertIsInstance(audit, SafetyAuditRecord)
        self.assertEqual(audit.target_system, "production")

        # Verify listing
        audits = self.agent.list_audits()
        self.assertTrue(any(a["id"] == audit.id for a in audits))

        # Record Approval Decision (HITL workflow)
        updated = self.agent.record_decision(audit.id, "APPROVED", "lead_sre_sarah", "Validated in staging.")
        self.assertEqual(updated.approval.status, "APPROVED")
        self.assertEqual(updated.approval.reviewer, "lead_sre_sarah")

        # Execute Rollback simulation
        rb_updated = self.agent.execute_rollback(audit.id, "Drift detected after canary", "lead_sre_sarah")
        self.assertTrue(rb_updated.rollback_executed)
        self.assertIn("Rollback protocol completed successfully", rb_updated.rollback_logs or "")

        # Export test
        md_export = self.agent.export_audit(rb_updated, "markdown")
        self.assertIn("# Safety & Governance Audit Report", md_export)

        # Cleanup
        deleted = self.agent.delete_audit(audit.id)
        self.assertTrue(deleted)

    def test_api_routes_and_export(self):
        req = GovernanceAssessmentRequest(
            action_title="Purge Inactive User Tokens",
            target_system="database",
            proposed_payload="DELETE FROM auth_tokens WHERE expires_at < NOW();",
            initiator="security_agent",
        )
        record = assess_action_safety(req)
        self.assertEqual(record.action_title, "Purge Inactive User Tokens")

        # Retrieve
        fetched = get_safety_audit(record.id)
        self.assertEqual(fetched.id, record.id)

        # Approval decision route
        dec_req = RecordDecisionRequest(decision="APPROVED", reviewer="ciso_officer", notes="Routine cleanup authorized.")
        dec_res = record_approval_decision(record.id, dec_req)
        self.assertEqual(dec_res.approval.status, "APPROVED")

        # Rollback execution route
        rb_req = ExecuteRollbackRequest(reason="Session invalidation regression", executor="ciso_officer")
        rb_res = execute_audit_rollback(record.id, rb_req)
        self.assertTrue(rb_res.rollback_executed)

        # Export route
        exp_req = GovernanceExportRequest(audit=rb_res, format="json")
        exp_res = export_governance_report(exp_req)
        self.assertEqual(exp_res["format"], "json")
        self.assertIn(record.id, exp_res["content"])

        # Delete route
        del_res = delete_safety_audit(record.id)
        self.assertTrue(del_res["deleted"])

    def test_governance_swarm_adapter(self):
        swarm_agent = create_safety_governance_swarm_agent()
        self.assertEqual(swarm_agent.name, "safety_governance")
        res = swarm_agent.action({
            "action_title": "Production Secret Rotation Script",
            "target_system": "production",
            "proposed_payload": "vault write secret/db password=$(openssl rand -hex 32)",
        })
        self.assertIn("audit_id", res)
        self.assertIn("overall_risk_score", res)
        self.assertIn("risk_tier", res)
        self.assertIn("rollback_strategy", res)


if __name__ == "__main__":
    unittest.main()
