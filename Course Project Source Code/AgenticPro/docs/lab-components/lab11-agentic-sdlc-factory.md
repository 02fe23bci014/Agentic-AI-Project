# Lab 11: Agentic SDLC Factory (Requirement -> Tested Implementation)

The **Agentic SDLC Factory** is an autonomous end-to-end software engineering pipeline that transforms natural language software requirements into production-ready, modular Clean Architecture implementations, verified via automated test execution suites.

## Key Capabilities

1. **Multi-Stage SDLC Progression**:
   - **Stage 1 (Requirements Analysis)**: Breaks user requirements down into structured user stories, acceptance criteria, and priority rankings.
   - **Stage 2 (System Architecture)**: Decomposes domain models, entities, component responsibilities, public interfaces, and API contracts.
   - **Stage 3 (Implementation)**: Generates production-ready, typed source code following Clean Architecture principles.
   - **Stage 4 (Test Generation & Execution)**: Synthesizes comprehensive unit and boundary tests, executes them in-memory, and calculates branch/line coverage.
   - **Stage 5 (Delivery & Documentation)**: Packages the project into downloadable ZIP archives with generated `README.md` and API specifications.

2. **Automated In-Memory Test Runner**:
   - Evaluates generated test suites against the synthesized implementation code in isolated namespaces.
   - Reports detailed pass/fail status, execution latency, and console stdout logs.
   - Guarantees verifiable delivery gates before code artifacts are marked `completed`.

3. **Multi-Language & Framework Flexibility**:
   - Primary support for Python (Clean Architecture, FastAPI, Flask, standard library).
   - Extensible for TypeScript/Node.js and Go microservices.

4. **Swarm Integration**:
   - Adaptable into multi-agent swarms via `create_sdlc_factory_swarm_agent()`.

## Architecture

- **Models**: `backend/models/sdlc.py` (`SDLCRequirementRequest`, `SDLCProjectArtifact`, `UserStory`, `ArchitectureDesign`, `CodeFile`, `SDLCTestRun`, `TestResultItem`)
- **Tools**: `backend/tools/sdlc_tool.py` (`SDLCTool`: ZIP packaging, python test runner, README generator)
- **Skills**: `backend/skills/sdlc_factory/`
  - `prompt_builder.py`: Multi-stage SDLC prompt construction.
  - `validator.py`: Structural verification of stories, architecture, and code files.
  - `synthesizer.py`: High-fidelity deterministic domain synthesizer covering Rate Limiters, LRU Caches with TTL, Pub-Sub Event Buses, and custom domain services.
  - `skill.py`: Pre-flight reachability probe and fallback orchestration.
- **Agent**: `backend/agents/sdlc_agent.py` (`SDLCFactoryAgent`)
- **Database**: SQLite `sdlc_projects` table in `database/evaluations.db`.
- **API Routes**: `backend/api/sdlc_routes.py` (mounted at `/api/sdlc`)

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/sdlc/pipeline` | Ingest requirement, execute full SDLC pipeline, return project artifact |
| `GET` | `/api/sdlc/projects` | List all saved SDLC projects (supports `?created_by=`) |
| `GET` | `/api/sdlc/projects/{id}` | Retrieve complete project artifact, code files, and test results |
| `POST` | `/api/sdlc/projects/{id}/run-tests` | Re-run automated test suite in sandbox |
| `DELETE` | `/api/sdlc/projects/{id}` | Delete project artifact from SQLite |
| `GET` | `/api/sdlc/projects/{id}/export` | Download full project files as an in-memory `.zip` archive |
