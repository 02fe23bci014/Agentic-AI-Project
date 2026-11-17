import unittest
from backend.agents.deep_research_agent import DeepResearchAgent
from backend.agents.swarm_adapters import create_deep_research_swarm_agent
from backend.api.research_routes import (
    create_topic_briefing,
    delete_research_report,
    export_evidence_table,
    get_research_report,
    list_research_reports,
)
from backend.models.research import (
    EvidenceItem,
    ResearchExportRequest,
    ResearchRequest,
    TopicBriefing,
)
from backend.skills.deep_research.prompt_builder import ResearchPromptBuilder
from backend.skills.deep_research.synthesizer import ResearchSynthesizer
from backend.skills.deep_research.validator import ResearchValidator
from backend.tools.research_tool import ResearchTool


class TestDeepResearchComponents(unittest.TestCase):
    """Test suite for Lab 9: Deep Research Agent and Evidence Table."""

    def setUp(self):
        self.tool = ResearchTool()
        self.validator = ResearchValidator()
        self.builder = ResearchPromptBuilder()
        self.synthesizer = ResearchSynthesizer()
        self.agent = DeepResearchAgent()

    def test_evidence_item_model(self):
        item = EvidenceItem(
            id="EV-01",
            source="IEEE Trans. Software Eng.",
            title="Study on Microservices",
            claim="Decomposition reduces cognitive load but adds network latency",
            evidence_quote="Observed p99 latency increased by 18ms across 12 services",
            metric="18ms p99 overhead",
            credibility="Peer-Reviewed",
            confidence_score=0.95,
        )
        self.assertEqual(item.id, "EV-01")
        self.assertEqual(item.confidence_score, 0.95)

    def test_research_tool_markdown_export(self):
        items = [
            EvidenceItem(
                id="EV-01",
                source="ACM Queue",
                title="Consensus Benchmarks",
                claim="Raft achieves equivalent throughput to Paxos under steady state",
                evidence_quote="Throughput peaked at 45,000 op/s in both implementations",
                metric="45,000 op/s",
                credibility="Benchmark",
                confidence_score=0.92,
            )
        ]
        md = self.tool.format_evidence_markdown(items)
        self.assertIn("| ID | Source |", md)
        self.assertIn("`EV-01`", md)
        self.assertIn("45,000 op/s", md)

    def test_research_tool_csv_and_json_export(self):
        items = [
            EvidenceItem(
                id="EV-02",
                source="OSDI '20",
                title="Kernel Bypass Networking",
                claim="DPDK drops latency to sub-microsecond levels",
                evidence_quote="Mean RTT measured at 850ns",
                metric="850ns",
                credibility="Peer-Reviewed",
                confidence_score=0.98,
            )
        ]
        csv_out = self.tool.format_evidence_csv(items)
        self.assertIn("EV-02", csv_out)
        self.assertIn("850ns", csv_out)

        json_out = self.tool.format_evidence_json(items)
        self.assertIn('"id": "EV-02"', json_out)

    def test_validator_detects_valid_and_invalid_data(self):
        valid_payload = {
            "topic": "Query Optimization",
            "executive_summary": "Summary text",
            "key_findings": ["Point 1", "Point 2"],
            "technical_analysis": "Detailed technical analysis of cost models and cardinality estimation.",
            "evidence_table": [
                {
                    "source": "SIGMOD",
                    "claim": "Cost-based optimizer outperforms heuristic",
                    "evidence_quote": "3.4x faster plan generation",
                }
            ],
        }
        self.assertTrue(self.validator.validate(valid_payload))

        invalid_payload = {"topic": "Incomplete"}
        self.assertFalse(self.validator.validate(invalid_payload))

    def test_prompt_builder(self):
        prompt = self.builder.build(
            topic="B-Tree Indexing",
            depth="standard",
            focus_areas=["fanout", "write amplification"],
            max_sources=3,
        )
        self.assertIn("B-Tree Indexing", prompt)
        self.assertIn("fanout", prompt)
        self.assertIn("evidence_table", prompt)

    def test_domain_synthesizer_generation(self):
        data = self.synthesizer.synthesize(
            topic="Zero-Knowledge Proofs",
            depth="deep",
            focus_areas=["SNARKs", "STARKs"],
            max_sources=4,
        )
        self.assertEqual(data["topic"], "Zero-Knowledge Proofs")
        self.assertGreaterEqual(len(data["evidence_table"]), 3)
        self.assertTrue(self.validator.validate(data))

    def test_agent_conduct_research_and_persistence(self):
        req = ResearchRequest(
            topic="Serverless Cold Start Optimization",
            depth="deep",
            focus_areas=["Firecracker", "Snapshotting"],
            max_sources=4,
            student_or_user_id="student-test-001",
        )
        briefing = self.agent.conduct_research(req)
        self.assertIsInstance(briefing, TopicBriefing)
        self.assertEqual(briefing.topic, "Serverless Cold Start Optimization")
        self.assertGreater(len(briefing.evidence_table), 0)

        # Verify API routes retrieve this saved report
        reports = list_research_reports(created_by="student-test-001")
        self.assertTrue(any(r["id"] == briefing.id for r in reports))

        retrieved = get_research_report(briefing.id)
        self.assertEqual(retrieved.id, briefing.id)
        self.assertEqual(retrieved.topic, briefing.topic)

        # Cleanup
        del_res = delete_research_report(briefing.id)
        self.assertTrue(del_res["deleted"])

    def test_swarm_adapter_action(self):
        swarm_agent = create_deep_research_swarm_agent()
        self.assertEqual(swarm_agent.name, "deep_research")
        result = swarm_agent.action({"topic": "Event-Driven Microservices"})
        self.assertIn("briefing_id", result)
        self.assertGreater(result["evidence_count"], 0)


if __name__ == "__main__":
    unittest.main()
