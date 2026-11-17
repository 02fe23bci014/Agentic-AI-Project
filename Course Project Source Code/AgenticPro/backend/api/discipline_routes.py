from typing import Any
from fastapi import APIRouter, HTTPException
from backend.agents.discipline_agent import DisciplineSpecificAgent
from backend.models.discipline import (
    DisciplineExportRequest,
    DisciplineWorkletArtifact,
    WorkletRunCodeRequest,
    WorkletSolveRequest,
)

router = APIRouter()
agent = DisciplineSpecificAgent()


@router.post("/solve", response_model=DisciplineWorkletArtifact)
def solve_discipline_worklet(request: WorkletSolveRequest) -> DisciplineWorkletArtifact:
    """
    Lab 13: Discipline-Specific Agents (ME / CE / EE domain worklet).
    Synthesizes analytical derivations, evaluates code compliance,
    and runs verified Python simulation scripts.
    """
    try:
        artifact = agent.solve_worklet(request)
        return artifact
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Discipline worklet solving failed: {exc}",
        )


@router.get("/worklets")
def list_discipline_worklets(
    discipline: str | None = None,
    worklet_type: str | None = None,
) -> list[dict[str, Any]]:
    """List historical engineering discipline worklets."""
    return agent.list_worklets(discipline=discipline, worklet_type=worklet_type)


@router.get("/worklets/{worklet_id}", response_model=DisciplineWorkletArtifact)
def get_discipline_worklet(worklet_id: str) -> DisciplineWorkletArtifact:
    """Retrieve full engineering worklet by ID."""
    try:
        return agent.get_worklet(worklet_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/worklets/{worklet_id}/run-code", response_model=DisciplineWorkletArtifact)
def execute_worklet_code(worklet_id: str, request: WorkletRunCodeRequest) -> DisciplineWorkletArtifact:
    """Execute or re-run Python simulation script for an engineering worklet."""
    try:
        return agent.run_code(worklet_id, custom_code=request.custom_code)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Code simulation failed: {exc}")


@router.delete("/worklets/{worklet_id}")
def delete_discipline_worklet(worklet_id: str) -> dict[str, Any]:
    """Delete an engineering worklet from the SQLite database."""
    deleted = agent.delete_worklet(worklet_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Worklet '{worklet_id}' not found.")
    return {"deleted": True, "id": worklet_id}


@router.post("/export")
def export_discipline_worklet(request: DisciplineExportRequest) -> dict[str, str]:
    """Export engineering worklet report in Markdown or JSON format."""
    try:
        content = agent.export_worklet(request.worklet, export_format=request.format)
        return {
            "format": request.format.lower(),
            "content": content,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Export failed: {exc}")
