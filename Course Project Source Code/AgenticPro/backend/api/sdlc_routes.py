from typing import Any
from fastapi import APIRouter, HTTPException, Response

from backend.agents.sdlc_agent import SDLCFactoryAgent
from backend.models.sdlc import (
    SDLCProjectArtifact,
    SDLCRequirementRequest,
    SDLCTestRun,
)

router = APIRouter()
agent = SDLCFactoryAgent()


@router.post("/pipeline", response_model=SDLCProjectArtifact)
def execute_sdlc_pipeline(request: SDLCRequirementRequest) -> SDLCProjectArtifact:
    """
    Lab 11: Agentic SDLC Factory.
    Autonomous multi-stage software factory pipeline:
    Requirement -> User Stories -> Architecture -> Implementation -> Tests -> Verification.
    """
    try:
        artifact = agent.generate_sdlc_project(request)
        return artifact
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"SDLC Factory pipeline failed: {exc}",
        )


@router.get("/projects")
def list_sdlc_projects(created_by: str | None = None) -> list[dict[str, Any]]:
    """Retrieve all saved SDLC project artifacts."""
    return agent.list_projects(created_by=created_by)


@router.get("/projects/{project_id}", response_model=SDLCProjectArtifact)
def get_sdlc_project(project_id: str) -> SDLCProjectArtifact:
    """Retrieve the full SDLC project artifact by ID."""
    try:
        return agent.get_project(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/projects/{project_id}/run-tests", response_model=SDLCTestRun)
def execute_project_tests(project_id: str) -> SDLCTestRun:
    """
    Execute or re-run automated test suite against project code files in sandbox.
    """
    try:
        return agent.run_project_tests(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Test runner error: {exc}")


@router.delete("/projects/{project_id}")
def delete_sdlc_project(project_id: str) -> dict[str, Any]:
    """Delete an SDLC project artifact from the database."""
    deleted = agent.delete_project(project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found.")
    return {"deleted": True, "id": project_id}


@router.get("/projects/{project_id}/export")
def export_project_zip(project_id: str) -> Response:
    """Download the complete generated project files as a ZIP archive."""
    try:
        artifact = agent.get_project(project_id)
        zip_bytes = agent.export_project_zip(project_id)
        filename = f"{artifact.project_name.lower().replace(' ', '_')}.zip"
        return Response(
            content=zip_bytes,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
