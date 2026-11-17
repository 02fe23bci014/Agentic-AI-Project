# Lab 12: Safety & Governance (Risk, Approval, Eval, Rollback Plan)

The **Safety & Governance Agent** provides automated safety policy evaluation, multi-dimensional risk scoring, human-in-the-loop (HITL) approval workflows, and deterministic rollback plan generation & execution simulation. It ensures autonomous agent actions and production changes remain auditable, compliant, and reversible.

## Key Capabilities

1. **Multi-Dimensional Risk Assessment Engine**:
   - Scores actions across crucial enterprise risk dimensions:
     - **Security & Vulnerability Vector** (credential leakage, command injection, privilege escalation).
     - **System Stability & Operational Blast Radius** (service disruption, cascade failures, data schema modifications).
     - **Data Privacy & Compliance Governance** (PII handling, GDPR/HIPAA regulatory exposure, audit trail retention).
     - **Privilege & Access Control** (least privilege violations, root/sudo execution, unauthenticated network egress).
   - Generates an aggregate 0–100 risk score and maps it to a strict risk tier: `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`.

2. **Policy Evaluation Engine (Eval Checks)**:
   - Evaluates actions against standardized enterprise policy guardrails:
     - `POL-SEC-01`: Credential & Private Key Protection (zero hardcoded secrets).
     - `POL-SEC-02`: Destructive Operations Safeguard (checks for `rm -rf`, `DROP TABLE`, `TRUNCATE`).
     - `POL-SEC-03`: Principle of Least Privilege (disallows root containers, unchecked `sudo`, `chmod 777`).
     - `POL-GOV-01`: Production Change Gating (enforces explicit change windows and multi-party approvals).
     - `POL-GOV-02`: Privacy & Data Retention Compliance (PII sanitization & audit controls).
   - Outputs fine-grained check statuses: `PASS`, `WARN`, `FAIL`, alongside remediation hints.

3. **Human-in-the-Loop (HITL) Multi-Tier Approvals**:
   - Automatically approves safe, low-risk actions (`LOW` risk tier -> `AUTO_APPROVED`).
   - Gates risky, high-blast-radius, or policy-violating operations with mandatory human sign-off (`PENDING_REVIEW`).
   - Supports explicit reviewer actions: `APPROVED`, `REJECTED`, or `ESCALATED`.

4. **Deterministic Rollback Plan Generator & Simulator**:
   - Generates structured, sequenced recovery procedures with shell/CLI commands and verification probes.
   - Calculates estimated Recovery Time Objective (RTO in seconds).
   - Simulates end-to-end rollback execution, verifying post-rollback system health probes (`/healthz` 200 OK) and logging state transitions.

5. **Swarm Integration**:
   - Accessible via swarm workflows using `create_safety_governance_swarm_agent()`.

## Architecture

- **Models**: `backend/models/governance.py` (`PolicyEvalCheck`, `RiskDimension`, `RollbackStep`, `RollbackPlan`, `ApprovalDecision`, `GovernanceAssessmentRequest`, `SafetyAuditRecord`, `RecordDecisionRequest`, `ExecuteRollbackRequest`, `GovernanceExportRequest`)
- **Tools**: `backend/tools/governance_tool.py` (`GovernanceTool`: Signature scanning, policy evaluation, rollback simulation, Markdown/JSON report export)
- **Skills**: `backend/skills/safety_governance/`
  - `prompt_builder.py`: LLM prompt generator for risk and governance auditing.
  - `validator.py`: Pydantic structural validation.
  - `synthesizer.py`: Deterministic fallback domain synthesizer for offline/sandboxed environments.
  - `skill.py`: Rapid 0.5s network reachability probe with graceful synthesizer fallback.
- **Agent**: `backend/agents/governance_agent.py` (`SafetyGovernanceAgent`)
- **Database**: SQLite `governance_audits` table in `database/evaluations.db`.
- **API Routes**: `backend/api/governance_routes.py` (mounted at `/api/governance`)

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/governance/assess` | Ingest proposed action or code diff, execute risk assessment, evaluate policies, generate rollback plan |
| `GET` | `/api/governance/audits` | List all safety audit records (supports filtering by `?status=` and `?risk_tier=`) |
| `GET` | `/api/governance/audits/{id}` | Retrieve full audit record details |
| `POST` | `/api/governance/audits/{id}/decision` | Record HITL approval decision (`APPROVED`, `REJECTED`, `ESCALATED`) |
| `POST` | `/api/governance/audits/{id}/rollback` | Execute simulated rollback protocol and record recovery logs |
| `DELETE` | `/api/governance/audits/{id}` | Permanently delete an audit record |
| `POST` | `/api/governance/export-report` | Export audit report in Markdown or JSON format |
