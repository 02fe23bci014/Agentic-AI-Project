import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import unittest
from backend.agents.capstone_agent import CapstoneStudioAgent
from backend.agents.swarm_adapters import create_capstone_studio_swarm_agent
from backend.api.capstone_routes import (
    create_capstone_project,
    delete_capstone_project,
    download_capstone_zip,
    execute_capstone_tests,
    export_capstone_report,
    get_capstone_project,
    list_capstone_projects,
    run_pipeline_stage,
)
from backend.models.capstone import (
    AgentMessageLog,
    CapstoneCreateRequest,
    CapstoneDeliverable,
    CapstoneExportRequest,
    CapstoneProjectArtifact,
    CapstoneRunStageRequest,
    CapstoneRunTestsRequest,
    CapstoneTestRun,
    PipelineStageRecord,
    TeamMember,
)
from backend.skills.capstone_studio.prompt_builder import CapstonePromptBuilder
from backend.skills.capstone_studio.synthesizer import CapstoneSynthesizer
from backend.skills.capstone_studio.validator import CapstoneValidator
from backend.tools.capstone_tool import CapstoneTool


class TestCapstoneStudioComponents(unittest.TestCase):
    """Test suite for Lab 14: Capstone Project Studio (Full team-owned agentic system)."""

    def setUp(self):
        self.tool = CapstoneTool()
        self.validator = CapstoneValidator()
        self.builder = CapstonePromptBuilder()
        self.synthesizer = CapstoneSynthesizer()
        self.agent = CapstoneStudioAgent()

    def test_models_creation(self):
        member = TeamMember(
            name="Dr. Aris Vance",
            role="Lead Systems Architect",
            agent_type="architect",
            avatar="🧠",
            contribution_summary="Microgrid domain boundaries and state machine",
        )
        self.assertEqual(member.name, "Dr. Aris Vance")

        stage = PipelineStageRecord(
            stage_id="stage_1_discovery",
            name="Discovery & Requirements Analysis",
            status="COMPLETED",
            assigned_agent="Elena Rostova",
            execution_time_sec=1.2,
            summary="Requirements synthesized",
            key_findings=["Sub-second order clearing", "IEEE 1547 compliance"],
        )
        self.assertEqual(stage.status, "COMPLETED")

        msg = AgentMessageLog(
            sender="Lead Architect",
            receiver="SDLC Engineer",
            message_type="HANDOFF",
            content="Architecture blueprint approved. Begin code synthesis.",
        )
        self.assertEqual(msg.message_type, "HANDOFF")

        test_run = CapstoneTestRun(
            total_tests=3,
            passed=3,
            failed=0,
            coverage_pct=100.0,
            execution_logs="3 passed, 0 failed",
        )
        self.assertEqual(test_run.coverage_pct, 100.0)

    def test_tool_execution_and_zip_creation(self):
        code_deliv = CapstoneDeliverable(
            title="Calculator Module",
            category="CODE",
            file_path="src/calc.py",
            content="def add(a, b):\n    return a + b\n",
            language="python",
        )
        test_deliv = CapstoneDeliverable(
            title="Calculator Test",
            category="TESTS",
            file_path="tests/test_calc.py",
            content="def test_add_op():\n    assert add(3, 4) == 7\n",
            language="python",
        )
        run = self.tool.execute_capstone_tests([code_deliv, test_deliv])
        self.assertEqual(run.passed, 1)
        self.assertEqual(run.failed, 0)
        self.assertEqual(run.coverage_pct, 100.0)

        # Artifact & ZIP export test
        artifact = CapstoneProjectArtifact(
            id="cap-sample-01",
            team_name="Pioneer Lab",
            project_title="Distributed Compute Mesh",
            domain="Distributed Systems",
            mission_statement="P2P compute dispatch",
            team_members=[TeamMember(name="Lead", role="Architect", agent_type="architect")],
            stages=[PipelineStageRecord(stage_id="stage_1", name="Discovery", status="COMPLETED", assigned_agent="Lead", summary="OK")],
            messages=[AgentMessageLog(sender="Lead", receiver="ALL", content="Kickoff")],
            deliverables=[code_deliv, test_deliv],
            test_run=run,
            overall_risk_score=15,
            governance_tier="LOW",
        )

        zip_bytes = self.tool.create_capstone_zip(artifact)
        self.assertTrue(zip_bytes.startswith(b"PK"))
        self.assertGreater(len(zip_bytes), 100)

        md = self.tool.format_capstone_markdown(artifact)
        self.assertIn("# Capstone Project Dossier: Distributed Compute Mesh", md)

        js = self.tool.format_capstone_json(artifact)
        self.assertIn("cap-sample-01", js)

    def test_synthesizer_presets(self):
        # Microgrid
        grid_data = self.synthesizer.synthesize(
            team_name="VoltGrid Team",
            project_title="Autonomous Microgrid Energy Exchange",
            domain="Energy IoT",
        )
        self.assertTrue(self.validator.validate(grid_data))
        self.assertEqual(len(grid_data["stages"]), 5)
        self.assertGreaterEqual(len(grid_data["deliverables"]), 3)

        # FinTech Order Matching
        trade_data = self.synthesizer.synthesize(
            team_name="Apex Quant",
            project_title="Ultra-Low-Latency Order Matching Engine",
            domain="FinTech",
        )
        self.assertTrue(self.validator.validate(trade_data))
        self.assertEqual(trade_data["domain"], "FinTech & Algorithmic Trading")

        # Healthcare Clinical Triage
        health_data = self.synthesizer.synthesize(
            team_name="BioMed Lab",
            project_title="Clinical Patient Triage Coordinator",
            domain="Healthcare",
        )
        self.assertTrue(self.validator.validate(health_data))

    def test_agent_lifecycle_and_persistence(self):
        req = CapstoneCreateRequest(
            team_name="RoboSwarm Aerospace",
            project_title="Autonomous Drone Swarm Telemetry & Collision Avoidance",
            domain="Robotics & Aerospace",
            mission_statement="Multi-UAV spatial collision avoidance and trajectory deconfliction",
            user_id="student_lead_01",
            auto_execute_pipeline=True,
        )
        project = self.agent.create_project(req)
        self.assertIsInstance(project, CapstoneProjectArtifact)
        self.assertEqual(project.team_name, "RoboSwarm Aerospace")
        self.assertEqual(len(project.stages), 5)
        self.assertGreater(project.test_run.passed, 0)

        # Retrieve
        fetched = self.agent.get_project(project.id)
        self.assertEqual(fetched.id, project.id)

        # List
        projects = self.agent.list_projects()
        self.assertTrue(any(p["id"] == project.id for p in projects))

        # Re-run stage
        st_updated = self.agent.run_stage(project.id, "stage_3_implementation")
        self.assertEqual(st_updated.stages[2].status, "COMPLETED")

        # Re-run test harness
        test_run = self.agent.run_tests(project.id)
        self.assertGreaterEqual(test_run.passed, 1)

        # ZIP export
        zip_bytes = self.agent.export_zip(project.id)
        self.assertTrue(zip_bytes.startswith(b"PK"))

        # Cleanup
        deleted = self.agent.delete_project(project.id)
        self.assertTrue(deleted)

    def test_api_routes(self):
        req = CapstoneCreateRequest(
            team_name="Test Swarm Alpha",
            project_title="Autonomous Microgrid Energy Exchange",
            domain="Energy IoT",
            mission_statement="P2P microgrid power clearing",
            auto_execute_pipeline=True,
        )
        project = create_capstone_project(req)
        self.assertEqual(project.team_name, "Test Swarm Alpha")

        fetched = get_capstone_project(project.id)
        self.assertEqual(fetched.id, project.id)

        # Stage runner route
        stage_res = run_pipeline_stage(project.id, CapstoneRunStageRequest(stage_id="stage_4_testing"))
        self.assertEqual(stage_res.id, project.id)

        # Test runner route
        tests_res = execute_capstone_tests(project.id, CapstoneRunTestsRequest())
        self.assertGreater(tests_res.passed, 0)

        # ZIP download route
        zip_res = download_capstone_zip(project.id)
        self.assertEqual(zip_res.media_type, "application/zip")

        # Report export route
        rep_res = export_capstone_report(CapstoneExportRequest(project=project, format="markdown"))
        self.assertEqual(rep_res["format"], "markdown")
        self.assertIn(project.team_name, rep_res["content"])

        # Delete route
        del_res = delete_capstone_project(project.id)
        self.assertTrue(del_res["deleted"])

    def test_swarm_adapter(self):
        swarm_agent = create_capstone_studio_swarm_agent()
        self.assertEqual(swarm_agent.name, "capstone_studio")
        res = swarm_agent.action({
            "team_name": "Quant Collective",
            "project_title": "High-Frequency Order Matching Engine",
            "domain": "FinTech",
        })
        self.assertIn("project_id", res)
        self.assertEqual(res["team_name"], "Quant Collective")
        self.assertEqual(res["stages_count"], 5)


if __name__ == "__main__":
    unittest.main()
