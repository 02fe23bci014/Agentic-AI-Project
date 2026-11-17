from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class TeamMember(BaseModel):
    name: str = Field(description="Team member or autonomous agent display name")
    role: str = Field(description="Role designation e.g. Lead Systems Architect, SRE Officer")
    agent_type: str = Field(default="architect", description="'architect', 'research', 'sdlc', 'devops', 'governance', 'discipline'")
    avatar: str | None = Field(default=None, description="Emoji or avatar identifier")
    contribution_summary: str = Field(default="", description="Specific capstone deliverables owned")


class PipelineStageRecord(BaseModel):
    stage_id: str = Field(description="e.g. stage_1_discovery, stage_2_architecture, stage_3_implementation, stage_4_testing, stage_5_governance")
    name: str = Field(description="Display title of pipeline stage")
    status: str = Field(default="COMPLETED", description="'PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED'")
    assigned_agent: str = Field(description="Agent or team member owning this phase")
    execution_time_sec: float = Field(default=1.5, description="Duration in seconds")
    summary: str = Field(description="Phase execution summary and synthesis output")
    key_findings: list[str] = Field(default_factory=list, description="Milestone deliverables produced")


class AgentMessageLog(BaseModel):
    sender: str = Field(description="Originating agent name")
    receiver: str = Field(description="Target recipient agent or 'ALL'")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().strftime("%H:%M:%S"))
    message_type: str = Field(default="HANDOFF", description="'HANDOFF', 'QUERY', 'DECISION', 'ARTIFACT_DELIVERY'")
    content: str = Field(description="Message body exchanged across the agent swarm")


class CapstoneDeliverable(BaseModel):
    title: str = Field(description="Deliverable title e.g. Architecture Specification, Core Matching Engine")
    category: str = Field(description="'RESEARCH', 'ARCHITECTURE', 'CODE', 'TESTS', 'GOVERNANCE', 'DOCS'")
    file_path: str = Field(description="Virtual repository path e.g. src/engine.py or docs/architecture.md")
    content: str = Field(description="Full text or source code content")
    language: str | None = Field(default="python", description="Language for syntax highlighting")


class CapstoneTestRun(BaseModel):
    total_tests: int = Field(ge=0, description="Total automated test cases executed")
    passed: int = Field(ge=0, description="Test cases passed")
    failed: int = Field(ge=0, description="Test cases failed")
    coverage_pct: float = Field(ge=0.0, le=100.0, description="Branch/line test coverage percentage")
    execution_logs: str = Field(default="", description="Test runner stdout execution trace")


class CapstoneProjectArtifact(BaseModel):
    id: str = Field(description="Unique capstone project ID e.g. cap-20261117-01")
    team_name: str = Field(description="Student or agent engineering team name")
    project_title: str = Field(description="Full capstone initiative title")
    domain: str = Field(description="Industry or academic domain e.g. FinTech, Energy IoT, Healthcare")
    mission_statement: str = Field(description="Core objective and problem addressed")
    status: str = Field(default="completed", description="'completed', 'in_progress', 'planning'")
    team_members: list[TeamMember] = Field(default_factory=list)
    stages: list[PipelineStageRecord] = Field(default_factory=list)
    messages: list[AgentMessageLog] = Field(default_factory=list)
    deliverables: list[CapstoneDeliverable] = Field(default_factory=list)
    test_run: CapstoneTestRun
    overall_risk_score: int = Field(ge=0, le=100, default=15)
    governance_tier: str = Field(default="LOW", description="'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'")
    architecture_diagram: str | None = Field(default=None, description="ASCII or Mermaid system topology diagram")
    created_by: str | None = Field(default=None, description="Submitting user or team lead ID")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class CapstoneCreateRequest(BaseModel):
    team_name: str = Field(min_length=2, description="Team designation")
    project_title: str = Field(min_length=3, description="Capstone title")
    domain: str = Field(default="General Software Engineering", description="Domain focus")
    mission_statement: str = Field(default="", description="High-level engineering problem statement")
    team_members: list[TeamMember] = Field(default_factory=list, description="Custom roster of team members/agents")
    auto_execute_pipeline: bool = Field(default=True, description="Whether to execute all 5 autonomous stages immediately")
    user_id: str | None = Field(default=None, description="Student or team lead username")


class CapstoneRunStageRequest(BaseModel):
    stage_id: str = Field(description="Stage identifier to execute")
    custom_prompt: str | None = Field(default=None, description="Optional custom steering prompt")


class CapstoneRunTestsRequest(BaseModel):
    custom_code: str | None = Field(default=None, description="Custom code to execute against verification harness")


class CapstoneExportRequest(BaseModel):
    project: CapstoneProjectArtifact
    format: str = Field(default="markdown", description="'markdown' or 'json'")
