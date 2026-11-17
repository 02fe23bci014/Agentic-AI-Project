from typing import Any
from fastapi import APIRouter, HTTPException, Response
from backend.agents.capstone_agent import CapstoneStudioAgent
from backend.models.capstone import (
    CapstoneCreateRequest,
    CapstoneExportRequest,
    CapstoneProjectArtifact,
    CapstoneRunStageRequest,
    CapstoneRunTestsRequest,
    CapstoneTestRun,
)

router = APIRouter()
agent = CapstoneStudioAgent()


@router.post("/projects", response_model=CapstoneProjectArtifact)
def create_capstone_project(request: CapstoneCreateRequest) -> CapstoneProjectArtifact:
    """
    Lab 14: Capstone Project Studio.
    Initialize and execute a full team-owned autonomous agentic system pipeline
    (Discovery, Architecture, Implementation, Testing, Governance).
    """
    try:
        artifact = agent.create_project(request)
        return artifact
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Capstone project creation failed: {exc}")


@router.get("/projects")
def list_capstone_projects(domain: str | None = None) -> list[dict[str, Any]]:
    """List historical capstone projects."""
    return agent.list_projects(domain=domain)


@router.get("/projects/{project_id}", response_model=CapstoneProjectArtifact)
def get_capstone_project(project_id: str) -> CapstoneProjectArtifact:
    """Retrieve complete capstone project artifact by ID."""
    try:
        return agent.get_project(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/projects/{project_id}/run-stage", response_model=CapstoneProjectArtifact)
def run_pipeline_stage(project_id: str, request: CapstoneRunStageRequest) -> CapstoneProjectArtifact:
    """Trigger re-execution or updates for a specific pipeline stage."""
    try:
        return agent.run_stage(project_id, request.stage_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Stage execution failed: {exc}")


@router.post("/projects/{project_id}/run-tests", response_model=CapstoneTestRun)
def execute_capstone_tests(project_id: str, request: CapstoneRunTestsRequest) -> CapstoneTestRun:
    """Re-run automated test harness in-memory against capstone deliverables."""
    try:
        return agent.run_tests(project_id, custom_code=request.custom_code)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Test harness failed: {exc}")


@router.get("/projects/{project_id}/export-zip")
def download_capstone_zip(project_id: str):
    """Download full capstone project deliverables, code files, and docs as a ZIP archive."""
    try:
        zip_bytes = agent.export_zip(project_id)
        return Response(
            content=zip_bytes,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={project_id}.zip"},
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Export failed: {exc}")


@router.delete("/projects/{project_id}")
def delete_capstone_project(project_id: str) -> dict[str, Any]:
    """Delete a capstone project from SQLite database."""
    deleted = agent.delete_project(project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found.")
    return {"deleted": True, "id": project_id}


@router.post("/export-report")
def export_capstone_report(request: CapstoneExportRequest) -> dict[str, str]:
    """Export capstone portfolio report in Markdown or JSON format."""
    try:
        content = agent.export_report(request.project, export_format=request.format)
        return {
            "format": request.format.lower(),
            "content": content,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Report export failed: {exc}")
