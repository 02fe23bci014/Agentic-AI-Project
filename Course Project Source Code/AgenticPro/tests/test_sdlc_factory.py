import unittest
from backend.agents.sdlc_agent import SDLCFactoryAgent
from backend.agents.swarm_adapters import create_sdlc_factory_swarm_agent
from backend.api.sdlc_routes import (
    delete_sdlc_project,
    execute_project_tests,
    execute_sdlc_pipeline,
    export_project_zip,
    get_sdlc_project,
    list_sdlc_projects,
)
from backend.models.sdlc import (
    ArchitectureDesign,
    CodeFile,
    SDLCProjectArtifact,
    SDLCRequirementRequest,
    SDLCTestRun,
    UserStory,
)
from backend.skills.sdlc_factory.prompt_builder import SDLCFactoryPromptBuilder
from backend.skills.sdlc_factory.synthesizer import SDLCFactorySynthesizer
from backend.skills.sdlc_factory.validator import SDLCFactoryValidator
from backend.tools.sdlc_tool import SDLCTool


class TestSDLCFactoryComponents(unittest.TestCase):
    """Test suite for Lab 11: Agentic SDLC Factory (Requirement -> Tested Implementation)."""

    def setUp(self):
        self.tool = SDLCTool()
        self.validator = SDLCFactoryValidator()
        self.builder = SDLCFactoryPromptBuilder()
        self.synthesizer = SDLCFactorySynthesizer()
        self.agent = SDLCFactoryAgent()

    def test_models_creation(self):
        story = UserStory(
            id="US-01",
            title="Token Refill",
            as_a="API Gateway",
            i_want="Refill tokens per second",
            so_that="Bandwidth is regulated",
            acceptance_criteria=["Tokens increase over time", "Never exceed capacity"],
        )
        self.assertEqual(story.id, "US-01")

        arch = ArchitectureDesign(
            system_overview="Clean Architecture",
            architecture_style="clean_architecture",
        )
        self.assertEqual(arch.architecture_style, "clean_architecture")

    def test_tool_execute_python_tests(self):
        code_files = [
            CodeFile(
                filepath="src/calc.py",
                file_type="source",
                language="python",
                content="def add(a, b):\n    return a + b\n",
            ),
            CodeFile(
                filepath="tests/test_calc.py",
                file_type="test",
                language="python",
                content="def test_add():\n    assert add(2, 3) == 5\n",
            ),
        ]
        test_run = self.tool.execute_python_tests(code_files)
        self.assertEqual(test_run.passed, 1)
        self.assertEqual(test_run.failed, 0)
        self.assertEqual(test_run.coverage_pct, 100.0)

    def test_tool_create_zip_and_readme(self):
        files = [
            CodeFile(
                filepath="main.py",
                file_type="source",
                language="python",
                content="print('Hello world')",
            )
        ]
        zip_bytes = self.tool.create_project_zip(files)
        self.assertGreater(len(zip_bytes), 50)
        self.assertTrue(zip_bytes.startswith(b"PK"))

        readme = self.tool.generate_readme("Payment Service", "Process payments", "fastapi", files)
        self.assertIn("# Payment Service", readme)
        self.assertIn("Clean Architecture", readme)

    def test_validator_and_synthesizer_rate_limiter(self):
        data = self.synthesizer.synthesize(
            project_name="Token Bucket Rate Limiter",
            requirement_text="Implement a token bucket rate limiter with configurable capacity and refill rate.",
        )
        self.assertTrue(self.validator.validate(data))
        self.assertGreaterEqual(len(data["user_stories"]), 1)
        self.assertGreaterEqual(len(data["code_files"]), 3)

    def test_agent_full_pipeline_execution_and_persistence(self):
        req = SDLCRequirementRequest(
            project_name="In-Memory Cache with TTL",
            requirement_text="Design an in-memory cache with Least Recently Used (LRU) eviction and TTL support.",
            target_language="python",
            framework="fastapi",
            auto_execute_tests=True,
            user_id="lead-architect-01",
        )
        artifact = self.agent.generate_sdlc_project(req)
        self.assertIsInstance(artifact, SDLCProjectArtifact)
        self.assertEqual(artifact.project_name, "In-Memory Cache with TTL")
        self.assertEqual(artifact.status, "completed")
        self.assertGreater(artifact.test_run.passed, 0)
        self.assertEqual(artifact.test_run.failed, 0)

        # Verify listing API returns project
        projects = list_sdlc_projects(created_by="lead-architect-01")
        self.assertTrue(any(p["id"] == artifact.id for p in projects))

        # Verify retrieve endpoint
        retrieved = get_sdlc_project(artifact.id)
        self.assertEqual(retrieved.id, artifact.id)

        # Verify test re-execution endpoint
        rerun = execute_project_tests(artifact.id)
        self.assertGreater(rerun.passed, 0)

        # Verify ZIP export endpoint
        response = export_project_zip(artifact.id)
        self.assertEqual(response.media_type, "application/zip")
        self.assertTrue(len(response.body) > 100)

        # Cleanup
        del_res = delete_sdlc_project(artifact.id)
        self.assertTrue(del_res["deleted"])

    def test_sdlc_factory_swarm_adapter(self):
        swarm_agent = create_sdlc_factory_swarm_agent()
        self.assertEqual(swarm_agent.name, "sdlc_factory")
        res = swarm_agent.action({
            "project_name": "PubSub Event Bus",
            "requirement_text": "Thread-safe event bus with topic subscribe and publish mechanism.",
        })
        self.assertIn("project_id", res)
        self.assertEqual(res["status"], "completed")
        self.assertGreater(res["tests_passed"], 0)


if __name__ == "__main__":
    unittest.main()
