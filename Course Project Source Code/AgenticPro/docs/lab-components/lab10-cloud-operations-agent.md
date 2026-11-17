# Lab 10: Cloud Operations Agent (Failed Deployment: Diagnose & Fix)

The **Cloud Operations Agent** is an autonomous DevOps and Site Reliability Engineering (SRE) agent that diagnoses failed container and cloud deployments, identifies root causes, and formulates verified remediation plans with unified diff patches.

## Key Capabilities

1. **Automated Root Cause Analysis (RCA)**:
   - Ingests crash dumps, pod logs, build logs, and configuration manifests (Kubernetes YAML, Dockerfile, Docker Compose, Terraform).
   - Identifies failure categories such as `OOMKilled` (Exit code 137), `CrashLoopBackOff`, `PortConflict`, `ConfigMissing` (missing env vars/secrets), `MigrationError`, `ImagePullError`, and `IAMForbidden`.
   - Produces executive summaries, affected dependencies, and triggering signals.

2. **Remediation Plan & Patch Synthesis**:
   - Generates step-by-step imperative actions with explanations and risk ratings.
   - Generates unified diff patches (`.diff`) ready for pull requests or GitOps pipelines.
   - Formulates post-fix verification checks and preventive architectural recommendations.

3. **Automated Fix Verification Simulation**:
   - Validates patch application and simulates deployment rollouts with container startup probes, HTTP healthz checks, and crash loop monitors.
   - Automatically records state transitions (`diagnosed` -> `remediated` -> `verified`).

4. **Multi-Format Post-Mortem Export**:
   - Formats comprehensive Post-Mortem Incident Reports in GitHub Flavored Markdown and structured JSON.

5. **Swarm Integration**:
   - Adaptable into parallel multi-agent swarms via `create_cloud_operations_swarm_agent()`.

## Architecture

- **Models**: `backend/models/cloud_ops.py` (`DiagnosisRequest`, `DiagnosisReport`, `RootCauseAnalysis`, `RemediationStep`, `PatchArtifact`, `RemediationResult`, `PostmortemExportRequest`)
- **Tools**: `backend/tools/cloud_ops_tool.py` (`CloudOpsTool`: unified diff, log signature parsing, fix verification, markdown/json export)
- **Skills**: `backend/skills/cloud_operations/`
  - `prompt_builder.py`: LLM diagnostic prompt construction.
  - `validator.py`: Structural integrity and remediation plan validation.
  - `synthesizer.py`: High-fidelity deterministic cloud failure synthesizer with zero external dependencies.
  - `skill.py`: Pre-flight reachability probe and fallback orchestration.
- **Agent**: `backend/agents/cloud_operations_agent.py` (`CloudOperationsAgent`)
- **Database**: SQLite `cloud_incidents` table in `database/evaluations.db`.
- **API Routes**: `backend/api/cloud_ops_routes.py` (mounted at `/api/cloud-ops`)

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/cloud-ops/diagnose` | Ingest logs & config, perform RCA, generate remediation & diff patch |
| `GET` | `/api/cloud-ops/incidents` | List incident reports (supports `?status=`, `?severity=`, `?created_by=`) |
| `GET` | `/api/cloud-ops/incidents/{id}` | Retrieve complete diagnosis report and patch artifacts |
| `POST` | `/api/cloud-ops/incidents/{id}/apply` | Execute / simulate remediation fix and verification |
| `DELETE` | `/api/cloud-ops/incidents/{id}` | Delete incident report |
| `POST` | `/api/cloud-ops/export-postmortem` | Export post-mortem incident report (Markdown / JSON) |
