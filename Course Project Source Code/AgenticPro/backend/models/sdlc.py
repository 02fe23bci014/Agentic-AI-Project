from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class UserStory(BaseModel):
    id: str = Field(description="User story ID e.g. US-01")
    title: str = Field(description="Story title")
    as_a: str = Field(description="Role / persona")
    i_want: str = Field(description="Desired capability")
    so_that: str = Field(description="Business outcome or value")
    acceptance_criteria: list[str] = Field(default_factory=list, description="Verifiable acceptance criteria")
    priority: str = Field(default="High", description="'High', 'Medium', 'Low'")


class ComponentSpec(BaseModel):
    name: str = Field(description="Component or module name")
    responsibility: str = Field(description="Core domain responsibility")
    interface_methods: list[str] = Field(default_factory=list, description="Public methods or endpoints")


class ArchitectureDesign(BaseModel):
    system_overview: str = Field(description="High-level architecture overview")
    architecture_style: str = Field(default="Clean Architecture", description="Architecture pattern applied")
    components: list[ComponentSpec] = Field(default_factory=list, description="System components decomposition")
    data_schemas: list[dict[str, str]] = Field(default_factory=list, description="Entity models and schemas")
    api_endpoints: list[dict[str, str]] = Field(default_factory=list, description="REST / gRPC endpoint definitions")


class CodeFile(BaseModel):
    filepath: str = Field(description="Path relative to project root, e.g. 'src/service.py'")
    file_type: str = Field(description="'source', 'test', 'config', 'documentation'")
    language: str = Field(default="python", description="'python', 'typescript', 'go', 'yaml', 'markdown'")
    content: str = Field(description="Full file source code or text")
    description: str = Field(default="", description="Summary of file purpose")


class TestResultItem(BaseModel):
    test_name: str = Field(description="Test function or method name")
    status: str = Field(description="'passed', 'failed', 'skipped'")
    execution_time_ms: float = Field(default=0.0, description="Execution duration in milliseconds")
    error_message: str | None = Field(default=None, description="Failure stack trace or assertion error")


class SDLCTestRun(BaseModel):
    passed: int = Field(default=0)
    failed: int = Field(default=0)
    total: int = Field(default=0)
    coverage_pct: float = Field(default=100.0, ge=0.0, le=100.0)
    test_details: list[TestResultItem] = Field(default_factory=list)
    stdout_logs: str = Field(default="", description="Test runner console output")


class SDLCRequirementRequest(BaseModel):
    project_name: str = Field(min_length=2, description="Project name")
    requirement_text: str = Field(min_length=10, description="Software requirements or problem specification")
    target_language: str = Field(default="python", description="'python', 'typescript', 'go'")
    framework: str = Field(default="fastapi", description="'fastapi', 'flask', 'express', 'standard-lib'")
    architecture_style: str = Field(default="clean_architecture", description="e.g. 'clean_architecture', 'modular_monolith'")
    auto_execute_tests: bool = Field(default=True, description="Whether to immediately run test suite after code gen")
    user_id: str | None = Field(default=None, description="Student or Engineer username")


class SDLCProjectArtifact(BaseModel):
    id: str = Field(description="Unique project artifact ID")
    project_name: str
    requirement_text: str
    target_language: str
    framework: str
    architecture_style: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    user_stories: list[UserStory] = Field(default_factory=list)
    architecture: ArchitectureDesign
    code_files: list[CodeFile] = Field(default_factory=list)
    test_run: SDLCTestRun
    documentation_markdown: str = Field(default="", description="Generated README and API docs")
    status: str = Field(default="completed", description="'completed', 'tests_failed', 'in_progress'")
    created_by: str | None = None


class RunTestsRequest(BaseModel):
    project_id: str
