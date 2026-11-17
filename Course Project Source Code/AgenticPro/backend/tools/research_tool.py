import csv
import io
import json
from typing import Any
from backend.models.research import EvidenceItem


class ResearchTool:
    """
    Tool for evidence collection, structuring, and tabular export.
    Supports academic citation formatting and multi-format evidence table serialization.
    """

    @staticmethod
    def format_evidence_markdown(evidence_list: list[EvidenceItem]) -> str:
        """Render evidence list as a GitHub Flavored Markdown table."""
        if not evidence_list:
            return "_No evidence records collected._"

        headers = [
            "ID",
            "Source",
            "Claim / Finding",
            "Supporting Evidence",
            "Metric",
            "Credibility",
            "Confidence",
        ]

        rows = [
            f"| {' | '.join(headers)} |",
            f"| {' | '.join(['---'] * len(headers))} |",
        ]

        for item in evidence_list:
            clean_claim = item.claim.replace("|", "\\|").replace("\n", " ")
            clean_quote = item.evidence_quote.replace("|", "\\|").replace("\n", " ")
            metric_val = item.metric or "N/A"
            conf_pct = f"{int(item.confidence_score * 100)}%"
            row = (
                f"| `{item.id}` "
                f"| {item.source} "
                f"| {clean_claim} "
                f"| {clean_quote} "
                f"| {metric_val} "
                f"| {item.credibility} "
                f"| {conf_pct} |"
            )
            rows.append(row)

        return "\n".join(rows)

    @staticmethod
    def format_evidence_csv(evidence_list: list[EvidenceItem]) -> str:
        """Export evidence list as CSV data."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "ID",
            "Source",
            "Title",
            "Claim",
            "Evidence Quote",
            "Metric",
            "Credibility",
            "URL / Reference",
            "Confidence",
        ])

        for item in evidence_list:
            writer.writerow([
                item.id,
                item.source,
                item.title,
                item.claim,
                item.evidence_quote,
                item.metric or "",
                item.credibility,
                item.url_or_doi or "",
                f"{item.confidence_score:.2f}",
            ])

        return output.getvalue()

    @staticmethod
    def format_evidence_json(evidence_list: list[EvidenceItem]) -> str:
        """Export evidence list as formatted JSON string."""
        data = [item.model_dump() for item in evidence_list]
        return json.dumps(data, indent=2)

    def export(self, evidence_list: list[EvidenceItem], export_format: str = "markdown") -> str:
        """Serialize evidence table to the requested format."""
        fmt = export_format.lower().strip()
        if fmt == "csv":
            return self.format_evidence_csv(evidence_list)
        elif fmt == "json":
            return self.format_evidence_json(evidence_list)
        return self.format_evidence_markdown(evidence_list)
