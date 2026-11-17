from datetime import datetime
from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    id: str = Field(description="Unique identifier for this piece of evidence")
    source: str = Field(description="Originating publication, paper, vendor spec, or benchmark")
    title: str = Field(description="Title of the paper or document")
    claim: str = Field(description="The key factual finding, claim, or conclusion")
    evidence_quote: str = Field(description="Direct supporting excerpt, data point, or observation")
    metric: str | None = Field(default=None, description="Quantitative metric (e.g. latency, throughput, accuracy)")
    credibility: str = Field(default="High", description="Credibility assessment (e.g., Peer-Reviewed, Benchmark, Industry Spec)")
    url_or_doi: str | None = Field(default=None, description="URL or DOI link reference")
    confidence_score: float = Field(default=0.9, ge=0.0, le=1.0, description="Confidence rating between 0 and 1")


class ResearchRequest(BaseModel):
    topic: str = Field(min_length=2, description="Research topic or technical question")
    depth: str = Field(default="deep", description="Research depth: 'overview', 'standard', 'deep'")
    focus_areas: list[str] = Field(default_factory=list, description="Specific sub-areas or angles of interest")
    max_sources: int = Field(default=5, ge=1, le=20, description="Maximum number of evidence sources to analyze")
    student_or_user_id: str | None = Field(default=None, description="Optional ID of student or researcher")


class TopicBriefing(BaseModel):
    id: str
    topic: str
    executive_summary: str
    key_findings: list[str]
    technical_analysis: str
    evidence_table: list[EvidenceItem]
    tradeoffs_and_comparisons: list[dict[str, str]] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ResearchExportRequest(BaseModel):
    evidence: list[EvidenceItem]
    format: str = Field(default="markdown", description="'markdown', 'csv', or 'json'")
