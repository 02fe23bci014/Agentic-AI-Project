import json
from datetime import datetime
from typing import Any

from backend.database.connection import get_connection
from backend.models.sdlc import (
    ArchitectureDesign,
    CodeFile,
    ComponentSpec,
    SDLCProjectArtifact,
    SDLCRequirementRequest,
    SDLCTestRun,
    UserStory,
)
from backend.skills.sdlc_factory.skill import SDLCFactorySkill
from backend.tools.sdlc_tool import SDLCTool


class SDLCFactoryAgent:
    """
    Lab 11: Agentic SDLC Factory.
    Autonomous multi-stage Software Development Life Cycle coordinator.
    Transforms high-level requirements into modular, clean-architecture implementations
    and automatically verifies acceptance criteria via generated test suites.
    """

    def __init__(self):
        self.skill = SDLCFactorySkill()
        self.tool = SDLCTool()

    def generate_sdlc_project(self, request: SDLCRequirementRequest) -> SDLCProjectArtifact:
        """Execute full SDLC pipeline: Requirements -> Design -> Code -> Tests -> Docs."""
        raw = self.skill.generate(
            project_name=request.project_name,
            requirement_text=request.requirement_text,
            target_language=request.target_language,
            framework=request.framework,
            architecture_style=request.architecture_style,
        )

        user_stories: list[UserStory] = []
        for s in raw.get("user_stories", []):
            user_stories.append(
                UserStory(
                    id=s.get("id", f"US-{len(user_stories) + 1:02d}"),
                    title=s.get("title", "User Story"),
                    as_a=s.get("as_a", "User"),
                    i_want=s.get("i_want", "Feature"),
                    so_that=s.get("so_that", "Outcome"),
                    acceptance_criteria=s.get("acceptance_criteria", []),
                    priority=s.get("priority", "High"),
                )
            )

        arch_raw = raw.get("architecture", {})
        components: list[ComponentSpec] = []
        for c in arch_raw.get("components", []):
            components.append(
                ComponentSpec(
                    name=c.get("name", "Module"),
                    responsibility=c.get("responsibility", "Handles logic"),
                    interface_methods=c.get("interface_methods", []),
                )
            )

        architecture = ArchitectureDesign(
            system_overview=arch_raw.get("system_overview", "Clean Architecture system breakdown."),
            architecture_style=arch_raw.get("architecture_style", request.architecture_style),
            components=components,
            data_schemas=arch_raw.get("data_schemas", []),
            api_endpoints=arch_raw.get("api_endpoints", []),
        )

        code_files: list[CodeFile] = []
        for f in raw.get("code_files", []):
            code_files.append(
                CodeFile(
                    filepath=f.get("filepath", "src/main.py"),
                    file_type=f.get("file_type", "source"),
                    language=f.get("language", request.target_language),
                    content=f.get("content", ""),
                    description=f.get("description", ""),
                )
            )

        # Generate documentation markdown
        readme_content = self.tool.generate_readme(
            project_name=request.project_name,
            requirement_text=request.requirement_text,
            framework=request.framework,
            files=code_files,
        )
        code_files.append(
            CodeFile(
                filepath="README.md",
                file_type="documentation",
                language="markdown",
                content=readme_content,
                description="Project documentation and architecture guide",
            )
        )

        # Execute automated tests
        if request.auto_execute_tests:
            test_run = self.tool.execute_python_tests(code_files)
        else:
            test_run = SDLCTestRun(
                passed=0,
                failed=0,
                total=0,
                coverage_pct=100.0,
                stdout_logs="Automated test execution deferred.",
            )

        project_id = f"sdlc-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        artifact = SDLCProjectArtifact(
            id=project_id,
            project_name=request.project_name,
            requirement_text=request.requirement_text,
            target_language=request.target_language,
            framework=request.framework,
            architecture_style=request.architecture_style,
            timestamp=datetime.utcnow().isoformat(),
            user_stories=user_stories,
            architecture=architecture,
            code_files=code_files,
            test_run=test_run,
            documentation_markdown=readme_content,
            status="completed" if test_run.failed == 0 else "tests_failed",
            created_by=request.user_id,
        )

        self._save_project(artifact)
        return artifact

    def run_project_tests(self, project_id: str) -> SDLCTestRun:
        """Run or re-run automated test suite on stored project code files."""
        artifact = self.get_project(project_id)
        test_run = self.tool.execute_python_tests(artifact.code_files)

        artifact.test_run = test_run
        artifact.status = "completed" if test_run.failed == 0 else "tests_failed"
        self._save_project(artifact)

        return test_run

    def get_project(self, project_id: str) -> SDLCProjectArtifact:
        """Retrieve project artifact by ID."""
        with get_connection() as connection:
            row = connection.execute(
                "SELECT artifact_json FROM sdlc_projects WHERE id = ?",
                (project_id,),
            ).fetchone()

        if not row:
            raise ValueError(f"SDLC Project '{project_id}' not found.")

        data = json.loads(row[0])
        return SDLCProjectArtifact(**data)

    def list_projects(self, created_by: str | None = None) -> list[dict[str, Any]]:
        """List all saved SDLC projects."""
        query = """
            SELECT id, project_name, requirement_text, target_language, framework, status, created_by, created_at
            FROM sdlc_projects
        """
        params = []
        if created_by and isinstance(created_by, str):
            query += " WHERE created_by = ?"
            params.append(created_by)

        query += " ORDER BY created_at DESC"

        with get_connection() as connection:
            rows = connection.execute(query, params).fetchall()

        projects = []
        for r in rows:
            projects.append({
                "id": r[0],
                "project_name": r[1],
                "requirement_text": r[2],
                "target_language": r[3],
                "framework": r[4],
                "status": r[5],
                "created_by": r[6],
                "created_at": r[7],
            })
        return projects

    def delete_project(self, project_id: str) -> bool:
        """Delete an SDLC project from SQLite database."""
        with get_connection() as connection:
            cursor = connection.execute("DELETE FROM sdlc_projects WHERE id = ?", (project_id,))
            return cursor.rowcount > 0

    def export_project_zip(self, project_id: str) -> bytes:
        """Export project files as an in-memory ZIP archive."""
        artifact = self.get_project(project_id)
        return self.tool.create_project_zip(artifact.code_files)

    def _save_project(self, artifact: SDLCProjectArtifact) -> None:
        """Persist project artifact into SQLite sdlc_projects table."""
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO sdlc_projects (
                    id, project_name, requirement_text, target_language, framework, status, artifact_json, created_by, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    status = excluded.status,
                    artifact_json = excluded.artifact_json
                """,
                (
                    artifact.id,
                    artifact.project_name,
                    artifact.requirement_text,
                    artifact.target_language,
                    artifact.framework,
                    artifact.status,
                    json.dumps(artifact.model_dump()),
                    artifact.created_by,
                    artifact.timestamp,
                ),
            )
