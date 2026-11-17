class ResearchPromptBuilder:
    """
    Builds structured prompts for Deep Research Agent topic briefings and evidence tables.
    """

    def build(
        self,
        topic: str,
        depth: str = "deep",
        focus_areas: list[str] | None = None,
        max_sources: int = 5,
    ) -> str:
        focus_str = ", ".join(focus_areas) if focus_areas else "Core concepts, architecture, performance benchmarks, and real-world trade-offs"

        return f"""
You are an elite Computer Science Principal Research Scientist and AI Deep Research Agent.

Your objective is to produce a rigorous, publication-grade AI Topic Briefing and an exhaustive, structured Evidence Table on the following inquiry:

TOPIC: "{topic}"
DEPTH LEVEL: {depth}
FOCUS AREAS: {focus_str}
MAXIMUM EVIDENCE SOURCES: {max_sources}

You must respond with ONLY valid JSON adhering to the exact schema below. Do not wrap with conversational commentary or markdown outside the JSON block.

JSON Schema:
{{
    "id": "briefing-unique-id",
    "topic": "{topic}",
    "executive_summary": "Comprehensive 2-3 paragraph executive summary synthesizing the state of the art, fundamental principles, and empirical consensus.",
    "key_findings": [
        "Finding 1 with specific architectural insight",
        "Finding 2 with empirical quantitative metric",
        "Finding 3 with system bottleneck or complexity analysis",
        "Finding 4 with deployment/production consideration"
    ],
    "technical_analysis": "In-depth multi-section technical analysis examining the underlying mechanisms, algorithmic details, memory/compute bounds, and systems trade-offs.",
    "evidence_table": [
        {{
            "id": "EV-01",
            "source": "Source Name (e.g. arXiv 2307.08691, IEEE Trans. on Cloud Computing, ACM SIGMOD)",
            "title": "Title of research paper, technical specification, or benchmark study",
            "claim": "Specific factual assertion or technical conclusion",
            "evidence_quote": "Direct quote or verbatim empirical observation from the source",
            "metric": "Key quantitative metric (e.g., '3.2x speedup', '99.4% recall@10', 'O(N log N) space')",
            "credibility": "Peer-Reviewed / Benchmark / Vendor Spec / Industry Consensus",
            "url_or_doi": "https://doi.org/... or https://arxiv.org/abs/...",
            "confidence_score": 0.95
        }}
    ],
    "tradeoffs_and_comparisons": [
        {{
            "dimension": "Latency vs Accuracy",
            "approach_a": "Details for approach A",
            "approach_b": "Details for approach B",
            "verdict": "Which approach excels in which scenario"
        }}
    ],
    "recommendations": [
        "Concrete recommendation 1",
        "Concrete recommendation 2"
    ],
    "references": [
        "Full citation 1",
        "Full citation 2"
    ]
}}

Quality Requirements:
- The Evidence Table must contain at least {min(max_sources, 3)} distinct, well-attributed evidence rows.
- Every evidence item must have a clear claim, supporting evidence excerpt, and confidence rating.
- The technical analysis must be deep, precise, and academically rigorous.
"""
