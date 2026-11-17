import json
from typing import Any
from fastapi import APIRouter, HTTPException, Query

from backend.agents.deep_research_agent import DeepResearchAgent
from backend.database.connection import get_connection
from backend.models.research import (
    EvidenceItem,
    ResearchExportRequest,
    ResearchRequest,
    TopicBriefing,
)
from backend.tools.research_tool import ResearchTool

router = APIRouter()
agent = DeepResearchAgent()
tool = ResearchTool()


@router.post("/briefing", response_model=TopicBriefing)
def create_topic_briefing(request: ResearchRequest) -> TopicBriefing:
    """
    Lab 9: Deep Research Agent.
    Executes systematic technical topic inquiry, synthesizing an AI executive
    briefing along with a structured evidence table.
    """
    try:
        briefing = agent.conduct_research(request)
        return briefing
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Research generation failed: {exc}",
        )


@router.get("/reports")
def list_research_reports(
    created_by: str | None = None,
) -> list[dict[str, Any]]:
    """Retrieve all persisted research reports and briefings."""
    query = """
        SELECT id, topic, summary, evidence_count, created_by, created_at
        FROM research_reports
    """
    params = []
    if created_by and isinstance(created_by, str):
        query += " WHERE created_by = ?"
        params.append(created_by)

    query += " ORDER BY created_at DESC"

    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()

    reports = []
    for row in rows:
        reports.append({
            "id": row[0],
            "topic": row[1],
            "summary": row[2],
            "evidence_count": row[3],
            "created_by": row[4],
            "created_at": row[5],
        })
    return reports


@router.get("/reports/{report_id}", response_model=TopicBriefing)
def get_research_report(report_id: str) -> TopicBriefing:
    """Retrieve full details of a specific topic briefing by ID."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT briefing_json FROM research_reports WHERE id = ?",
            (report_id,),
        ).fetchone()

    if not row:
        raise HTTPException(
            status_code=404,
            detail=f"Research report '{report_id}' was not found.",
        )

    briefing_dict = json.loads(row[0])
    return TopicBriefing(**briefing_dict)


@router.delete("/reports/{report_id}")
def delete_research_report(report_id: str) -> dict[str, Any]:
    """Delete a research report from the database."""
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM research_reports WHERE id = ?",
            (report_id,),
        )
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Research report '{report_id}' was not found.",
            )

    return {"deleted": True, "id": report_id}


@router.post("/export-evidence")
def export_evidence_table(request: ResearchExportRequest) -> dict[str, str]:
    """
    Export evidence table items into formatted serialization (markdown, csv, or json).
    """
    try:
        content = tool.export(request.evidence, export_format=request.format)
        return {
            "format": request.format.lower(),
            "content": content,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Evidence export failed: {exc}",
        )
