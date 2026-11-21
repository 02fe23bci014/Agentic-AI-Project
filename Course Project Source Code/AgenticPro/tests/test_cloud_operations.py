import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import unittest
from backend.agents.cloud_operations_agent import CloudOperationsAgent
from backend.agents.swarm_adapters import create_cloud_operations_swarm_agent
from backend.api.cloud_ops_routes import (
    apply_incident_remediation,
    delete_incident_report,
    diagnose_failed_deployment,
    export_postmortem_report,
    get_incident_report,
    list_incident_reports,
)
from backend.models.cloud_ops import (
    DiagnosisReport,
    DiagnosisRequest,
    PatchArtifact,
    PostmortemExportRequest,
    RemediationStep,
    RootCauseAnalysis,
)
from backend.skills.cloud_operations.prompt_builder import CloudOpsPromptBuilder
from backend.skills.cloud_operations.synthesizer import CloudOpsSynthesizer
from backend.skills.cloud_operations.validator import CloudOpsValidator
from backend.tools.cloud_ops_tool import CloudOpsTool


class TestCloudOperationsComponents(unittest.TestCase):
    """Test suite for Lab 10: Cloud Operations Agent (Diagnose & Fix)."""

    def setUp(self):
        self.tool = CloudOpsTool()
        self.validator = CloudOpsValidator()
        self.builder = CloudOpsPromptBuilder()
        self.synthesizer = CloudOpsSynthesizer()
        self.agent = CloudOperationsAgent()

    def test_models_creation(self):
        rca = RootCauseAnalysis(
            summary="Node out of memory",
            error_category="OOMKilled",
            severity="Critical",
            failing_service="auth-service",
            triggering_event="OOM killer invoked",
            affected_dependencies=["api-gateway"],
        )
        self.assertEqual(rca.error_category, "OOMKilled")

        step = RemediationStep(
            step_number=1,
            action="Increase pod memory limit",
            explanation="Prevent Linux kernel SIGKILL",
            risk_level="Low",
            is_automated=True,
        )
        self.assertEqual(step.step_number, 1)

    def test_tool_unified_diff(self):
        orig = "memory: 256Mi\ncpu: 200m"
        patched = "memory: 1Gi\ncpu: 500m"
        diff = self.tool.generate_unified_diff(orig, patched, filename="manifest.yaml")
        self.assertIn("--- a/manifest.yaml", diff)
        self.assertIn("+++ b/manifest.yaml", diff)
        self.assertIn("-memory: 256Mi", diff)
        self.assertIn("+memory: 1Gi", diff)

    def test_tool_log_signature_extraction(self):
        logs = """
        [2026-11-13T10:00:00Z] Application booting...
        [2026-11-13T10:00:02Z] Memory consumption: 255MB / 256MB limit
        [2026-11-13T10:00:03Z] Container terminated. Exit code 137: OOMKilled
        """
        sigs = self.tool.extract_log_signatures(logs)
        self.assertTrue(sigs["oom_detected"])
        self.assertIn("137", sigs["exit_codes"])
        self.assertGreater(len(sigs["error_lines"]), 0)

    def test_tool_simulate_verification(self):
        patches = [
            PatchArtifact(
                filename="deployment.yaml",
                file_type="yaml",
                original_snippet="limits: 256Mi",
                patched_snippet="limits: 1Gi",
            )
        ]
        log = self.tool.simulate_fix_verification("payment-service", patches)
        self.assertIn("HEALTHY and STABLE", log)
        self.assertIn("deployment.yaml", log)

    def test_validator_and_synthesizer_oom(self):
        logs = "fatal error: runtime: out of memory; exit code 137 (OOMKilled)"
        data = self.synthesizer.synthesize(
            service_name="payment-service",
            environment="production",
            raw_logs=logs,
        )
        self.assertTrue(self.validator.validate(data))
        self.assertEqual(data["rca"]["error_category"], "OOMKilled")
        self.assertGreaterEqual(len(data["remediation_steps"]), 2)
        self.assertGreaterEqual(len(data["patches"]), 1)

    def test_synthesizer_port_conflict(self):
        logs = "listen tcp :8080: bind: address already in use"
        data = self.synthesizer.synthesize(
            service_name="web-gateway",
            environment="staging",
            raw_logs=logs,
        )
        self.assertEqual(data["rca"]["error_category"], "PortConflict")
        self.assertIn("8080", data["rca"]["summary"])

    def test_agent_diagnose_and_persistence(self):
        req = DiagnosisRequest(
            service_name="checkout-service",
            environment="production",
            raw_logs="CrashLoopBackOff: back-off 5m0s restarting failed container=checkout",
            incident_type="CrashLoopBackOff",
            user_id="devops-engineer-01",
        )
        report = self.agent.diagnose_and_fix(req)
        self.assertIsInstance(report, DiagnosisReport)
        self.assertEqual(report.service_name, "checkout-service")
        self.assertEqual(report.rca.error_category, "CrashLoopBackOff")

        # Verify listing API returns this report
        incidents = list_incident_reports(created_by="devops-engineer-01")
        self.assertTrue(any(i["id"] == report.id for i in incidents))

        # Verify retrieve endpoint
        retrieved = get_incident_report(report.id)
        self.assertEqual(retrieved.id, report.id)

        # Verify applying remediation
        rem_res = apply_incident_remediation(report.id)
        self.assertTrue(rem_res.success)
        self.assertEqual(rem_res.status, "remediated")

        # Verify postmortem export
        exp = export_postmortem_report(PostmortemExportRequest(report=retrieved, format="markdown"))
        self.assertIn("# Post-Mortem Incident Report", exp["content"])

        # Cleanup
        del_res = delete_incident_report(report.id)
        self.assertTrue(del_res["deleted"])

    def test_cloud_ops_swarm_adapter(self):
        swarm_agent = create_cloud_operations_swarm_agent()
        self.assertEqual(swarm_agent.name, "cloud_operations")
        result = swarm_agent.action({
            "service_name": "inventory-api",
            "raw_logs": "KeyError: 'DATABASE_URL' is missing in environment",
            "incident_type": "ConfigMissing",
        })
        self.assertIn("incident_id", result)
        self.assertEqual(result["error_category"], "ConfigMissing")
        self.assertGreater(result["remediation_steps_count"], 0)


if __name__ == "__main__":
    unittest.main()
