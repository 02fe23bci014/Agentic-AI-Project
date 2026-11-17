# Lab 14: Capstone Project Studio (Full Team-Owned Agentic System)

The **Capstone Project Studio** is the culminating engineering environment in AgenticPro where student or autonomous engineering teams assemble, collaborate, and orchestrate a full multi-agent collective to deliver an end-to-end mission across 5 structured engineering phases.

## Key Capabilities

1. **Multi-Agent Team Roster & Role Assignment**:
   - Assemble teams with specialized autonomous agents:
     - 🧠 **Lead Systems Architect**: System boundary modeling, API contracts, domain topologies.
     - 🔍 **Research & Intelligence Agent**: Standards review (IEEE, SEC/FINRA, HIPAA, FAA), state of the art benchmarking.
     - 💻 **SDLC Synthesis Lead**: Clean Architecture implementation, domain entities, service orchestrators.
     - 🧪 **Verification & Test Harness Lead**: Boundary testing, automated test execution, coverage calculations.
     - 🛡️ **Safety & Governance Officer**: Policy evaluation, security auditing, risk assessment, and rollback readiness.

2. **Autonomous Multi-Stage Pipeline Progression**:
   - **Stage 1 (Discovery & Requirements Analysis)**: User persona definition, regulatory benchmarking, and acceptance criteria.
   - **Stage 2 (Architecture Blueprint & Topology)**: Data flow modeling, component isolation, and threat modeling.
   - **Stage 3 (Multi-Module Implementation)**: Synthesis of production-ready, typed source code.
   - **Stage 4 (Automated Verification & Test Harness)**: In-memory test execution with branch coverage scoring.
   - **Stage 5 (Safety & Governance Gate)**: Policy validation, credential leak checks, and automated rollback protocols.

3. **Preconfigured Enterprise Capstone Presets**:
   - **Autonomous Microgrid Peer-to-Peer Energy Exchange**: Distributed solar/battery storage balancing with dynamic double-auction clearing algorithms (Energy IoT).
   - **Ultra-Low-Latency Order Matching Engine**: Microsecond price-time priority limit order book with atomic trade settlement (FinTech & High-Frequency Trading).
   - **Clinical Patient Triage & Vital Telemetry Coordinator**: HIPAA-compliant ICU/emergency vital monitoring and Emergency Severity Index (ESI) scoring (Healthcare AI).
   - **Autonomous Drone Swarm Telemetry & Collision Avoidance**: 3D Euclidean spatial deconfliction, dynamic geofencing, and formation coordination (Robotics & Aerospace).

4. **Multi-Agent Swarm Collaboration Trace**:
   - Live stream of inter-agent handoff messages, milestone queries, consensus decisions, and artifact deliveries.

5. **Capstone Portfolio Deliverables & ZIP Download**:
   - In-memory ZIP packaging containing all source files, unit tests, `README.md`, `ARCHITECTURE.md`, and execution logs.
   - 1-click Markdown and JSON dossier export for peer review and grading.

## Architecture

- **Models**: `backend/models/capstone.py` (`TeamMember`, `PipelineStageRecord`, `AgentMessageLog`, `CapstoneDeliverable`, `CapstoneTestRun`, `CapstoneProjectArtifact`, `CapstoneCreateRequest`, `CapstoneRunStageRequest`, `CapstoneRunTestsRequest`, `CapstoneExportRequest`)
- **Tools**: `backend/tools/capstone_tool.py` (`CapstoneTool`: In-memory test runner, ZIP packager, portfolio dossier generator)
- **Skills**: `backend/skills/capstone_studio/`
  - `prompt_builder.py`: LLM prompt generator.
  - `validator.py`: Pydantic structural validation.
  - `synthesizer.py`: Domain synthesizer with 4 enterprise capstone presets.
  - `skill.py`: Rapid 0.5s network reachability probe with zero-delay fallback.
- **Agent**: `backend/agents/capstone_agent.py` (`CapstoneStudioAgent`)
- **Database**: SQLite `capstone_projects` table in `database/evaluations.db`.
- **API Routes**: `backend/api/capstone_routes.py` (mounted at `/api/capstone`)

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/capstone/projects` | Initialize and execute autonomous 5-stage Capstone pipeline |
| `GET` | `/api/capstone/projects` | List all historical Capstone projects (supports `?domain=`) |
| `GET` | `/api/capstone/projects/{id}` | Retrieve complete Capstone project artifact |
| `POST` | `/api/capstone/projects/{id}/run-stage` | Re-execute or update an individual pipeline stage |
| `POST` | `/api/capstone/projects/{id}/run-tests` | Re-run automated test harness in-memory against deliverables |
| `GET` | `/api/capstone/projects/{id}/export-zip` | Download complete project as an in-memory `.zip` archive |
| `DELETE` | `/api/capstone/projects/{id}` | Delete Capstone project from database |
| `POST` | `/api/capstone/export-report` | Export executive portfolio dossier in Markdown or JSON |
