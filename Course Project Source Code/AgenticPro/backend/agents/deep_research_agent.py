import json
from datetime import datetime
from typing import Any

from backend.database.connection import get_connection
from backend.models.research import EvidenceItem, ResearchRequest, TopicBriefing
from backend.skills.deep_research.skill import DeepResearchSkill
from backend.tools.research_tool import ResearchTool


class DeepResearchAgent:
    """
    Lab 9: Deep Research Agent.
    Specialized agent responsible for autonomous technical topic briefings,
    systematic evidence extraction, and tabular evidence generation.
    """

    def __init__(self):
        self.skill = DeepResearchSkill()
        self.tool = ResearchTool()

    def conduct_research(self, request: ResearchRequest) -> TopicBriefing:
        """
        Conduct deep inquiry on the specified topic, returning an executive
        topic briefing and structured evidence table.
        """
        raw_data = self.skill.generate(
            topic=request.topic,
            depth=request.depth,
            focus_areas=request.focus_areas,
            max_sources=request.max_sources,
        )

        # Parse evidence items
        evidence_items: list[EvidenceItem] = []
        for idx, item in enumerate(raw_data.get("evidence_table", [])):
            ev_id = item.get("id") or f"EV-{idx + 1:02d}"
            evidence_items.append(
                EvidenceItem(
                    id=ev_id,
                    source=item.get("source", "Technical Literature"),
                    title=item.get("title", f"Study on {request.topic}"),
                    claim=item.get("claim", ""),
                    evidence_quote=item.get("evidence_quote", ""),
                    metric=item.get("metric"),
                    credibility=item.get("credibility", "High"),
                    url_or_doi=item.get("url_or_doi"),
                    confidence_score=float(item.get("confidence_score", 0.9)),
                )
            )

        report_id = raw_data.get("id") or f"briefing-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        briefing = TopicBriefing(
            id=report_id,
            topic=raw_data.get("topic", request.topic),
            executive_summary=raw_data.get("executive_summary", ""),
            key_findings=raw_data.get("key_findings", []),
            technical_analysis=raw_data.get("technical_analysis", ""),
            evidence_table=evidence_items,
            tradeoffs_and_comparisons=raw_data.get("tradeoffs_and_comparisons", []),
            recommendations=raw_data.get("recommendations", []),
            references=raw_data.get("references", []),
            created_at=datetime.utcnow().isoformat(),
        )

        # Persist report in SQLite database
        self._save_report(briefing, created_by=request.student_or_user_id)

        return briefing

    def _save_report(self, briefing: TopicBriefing, created_by: str | None = None) -> None:
        """Store research briefing in SQLite research_reports table."""
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO research_reports (
                    id, topic, summary, briefing_json, evidence_count, created_by, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    summary = excluded.summary,
                    briefing_json = excluded.briefing_json,
                    evidence_count = excluded.evidence_count
                """,
                (
                    briefing.id,
                    briefing.topic,
                    briefing.executive_summary,
                    json.dumps(briefing.model_dump()),
                    len(briefing.evidence_table),
                    created_by,
                    briefing.created_at,
                ),
            )

    def export_evidence(self, evidence_list: list[EvidenceItem], export_format: str = "markdown") -> str:
        """Export evidence table into the specified serialization format."""
        return self.tool.export(evidence_list, export_format=export_format)
