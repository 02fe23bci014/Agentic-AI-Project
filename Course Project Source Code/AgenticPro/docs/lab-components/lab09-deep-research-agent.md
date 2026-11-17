# Lab 9: Deep Research Agent

The **Deep Research Agent** provides autonomous, multi-dimensional technical topic briefings and systematic evidence tables. It automates literature review, quantitative metric extraction, citation verification, and comparative tradeoff analysis.

## Key Capabilities

1. **AI Topic Briefing**:
   - Synthesizes executive summaries, key findings, and architectural deep-dives.
   - Formulates architectural tradeoffs and concrete engineering recommendations.
   - Collects formal citations, peer-reviewed publications, and industry specifications.

2. **Structured Evidence Table**:
   - Each claim is mapped to verbatim supporting quotes, source publications, and URLs/DOIs.
   - Extracts quantitative metrics (e.g., latency, throughput overhead, memory footprint).
   - Annotates credibility level (e.g., *Peer-Reviewed*, *Benchmark*, *Industry Spec*) and numeric confidence ratings.

3. **Multi-Format Serialization & Export**:
   - **Markdown**: Formatted GitHub Flavored Markdown table ready for documentation and pull request briefings.
   - **CSV**: Standard comma-separated format for spreadsheet analysis and gradebook verification.
   - **JSON**: Strongly typed machine-readable JSON array conforming to `EvidenceItem`.

4. **Swarm Integration**:
   - Exposed as a parallel `SwarmAgent` via `create_deep_research_swarm_agent()`.
   - Allows parallel orchestration alongside Sandbox, Similarity, Scoring, and Feedback agents.

## Architecture

- **Models**: `backend/models/research.py` (`EvidenceItem`, `ResearchRequest`, `TopicBriefing`, `ResearchExportRequest`)
- **Tools**: `backend/tools/research_tool.py` (`ResearchTool`)
- **Skills**: `backend/skills/deep_research/`
  - `prompt_builder.py`: Constructs synthesis and evidence extraction prompts.
  - `validator.py`: Enforces schema validity and evidence integrity.
  - `synthesizer.py`: High-fidelity domain synthesizer fallback with zero external dependencies.
  - `skill.py`: Coordinates LLM inference, pre-flight reachability checks, and fallback synthesis.
- **Agent**: `backend/agents/deep_research_agent.py` (`DeepResearchAgent`)
- **Database**: SQLite `research_reports` table in `database/evaluations.db`.
- **API Routes**: `backend/api/research_routes.py` (mounted at `/api/research`)

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/research/briefing` | Conduct deep research, return briefing and evidence table |
| `GET` | `/api/research/reports` | List saved research reports (supports `?created_by=`) |
| `GET` | `/api/research/reports/{id}` | Retrieve complete topic briefing and evidence by ID |
| `DELETE` | `/api/research/reports/{id}` | Delete a stored research report |
| `POST` | `/api/research/export-evidence` | Export evidence table to Markdown, CSV, or JSON |
