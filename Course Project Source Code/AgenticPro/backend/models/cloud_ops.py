from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class RemediationStep(BaseModel):
    step_number: int = Field(ge=1, description="Sequential order of remediation action")
    action: str = Field(description="Action title or imperative command")
    explanation: str = Field(description="Why this step is necessary")
    command_or_snippet: str | None = Field(default=None, description="CLI command or code snippet")
    risk_level: str = Field(default="Low", description="'Low', 'Medium', or 'High'")
    is_automated: bool = Field(default=True, description="Whether this can be automatically executed")


class PatchArtifact(BaseModel):
    filename: str = Field(description="Path or name of the affected configuration file")
    file_type: str = Field(default="yaml", description="'yaml', 'dockerfile', 'json', 'env', 'terraform', 'python'")
    original_snippet: str = Field(description="Defective code or configuration section")
    patched_snippet: str = Field(description="Remediated code or configuration section")
    diff_patch: str | None = Field(default=None, description="Unified diff string representing the fix")


class RootCauseAnalysis(BaseModel):
    summary: str = Field(description="High-level executive summary of why deployment failed")
    error_category: str = Field(
        description="Category (e.g., OOMKilled, CrashLoopBackOff, ConfigMissing, PortConflict, MigrationError, IAMForbidden)"
    )
    severity: str = Field(default="Critical", description="'Low', 'Medium', 'High', 'Critical'")
    failing_service: str = Field(description="Name of the service or pod that crashed")
    triggering_event: str = Field(description="Specific log entry or signal that triggered failure")
    affected_dependencies: list[str] = Field(default_factory=list, description="Downstream services impacted")


class DiagnosisRequest(BaseModel):
    service_name: str = Field(min_length=1, description="Name of the failing application or service")
    environment: str = Field(default="production", description="'production', 'staging', 'development'")
    deployment_target: str = Field(default="kubernetes", description="'kubernetes', 'docker-compose', 'aws-ecs', 'cloud-run', 'bare-metal'")
    raw_logs: str = Field(min_length=5, description="Failed deployment logs, crash dumps, or build output")
    deployment_config: str | None = Field(default=None, description="Current Dockerfile, k8s manifest, or config file")
    incident_type: str | None = Field(default=None, description="Optional incident hint (e.g. CrashLoopBackOff)")
    user_id: str | None = Field(default=None, description="ID of student or DevOps engineer submitting the incident")


class DiagnosisReport(BaseModel):
    id: str = Field(description="Unique incident diagnosis ID")
    service_name: str
    environment: str
    deployment_target: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    rca: RootCauseAnalysis
    remediation_steps: list[RemediationStep]
    patches: list[PatchArtifact] = Field(default_factory=list)
    verification_steps: list[str] = Field(default_factory=list)
    preventive_recommendations: list[str] = Field(default_factory=list)
    status: str = Field(default="diagnosed", description="'diagnosed', 'remediated', 'verified', 'failed'")


class ApplyRemediationRequest(BaseModel):
    incident_id: str
    auto_restart: bool = Field(default=True, description="Whether to simulate restarting the service after patch")


class RemediationResult(BaseModel):
    incident_id: str
    status: str = Field(description="'remediated', 'verified', 'partial'")
    success: bool
    patches_applied: list[str]
    verification_logs: str
    applied_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class PostmortemExportRequest(BaseModel):
    report: DiagnosisReport
    format: str = Field(default="markdown", description="'markdown' or 'json'")
