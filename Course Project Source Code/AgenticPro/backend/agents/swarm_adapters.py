from typing import Any
from backend.agents.deep_research_agent import DeepResearchAgent
from backend.agents.feedback_agent import FeedbackAgent
from backend.agents.result_publishing_agent import ResultPublishingAgent
from backend.agents.sandbox_agent import SandboxAgent
from backend.agents.scoring_agent import ScoringAgent
from backend.agents.similarity_agent import SimilarityAgent
from backend.models.evaluation import Evaluation
from backend.models.research import ResearchRequest
from backend.models.result import Result
from backend.runtime.swarm import SwarmAgent


def create_similarity_swarm_agent() -> SwarmAgent:
    """Adapt the existing SimilarityAgent for the parallel swarm."""

    similarity_agent = SimilarityAgent()

    def analyze(context: dict[str, Any]) -> dict[str, Any]:
        source_code = context.get("source_code")
        reference_code = context.get("reference_code")

        if not isinstance(source_code, str):
            raise ValueError("Context must include source_code as a string.")

        if not isinstance(reference_code, str):
            raise ValueError("Context must include reference_code as a string.")

        score = similarity_agent.compare(source_code, reference_code)
        return {"similarity_score": score}

    return SwarmAgent(
        name="similarity",
        role="Compare submitted code with reference code.",
        action=analyze,
    )


def create_sandbox_swarm_agent() -> SwarmAgent:
    """Adapt the existing SandboxAgent for the parallel swarm."""

    sandbox_agent = SandboxAgent()

    def execute(context: dict[str, Any]) -> dict[str, Any]:
        source_code = context.get("source_code")
        language = context.get("language")
        stdin = context.get("stdin", "")

        if not isinstance(source_code, str):
            raise ValueError("Context must include source_code as a string.")

        if not isinstance(language, str):
            raise ValueError("Context must include language as a string.")

        if not isinstance(stdin, str):
            raise ValueError("stdin must be a string.")

        result = sandbox_agent.run(source_code, language, stdin)
        return {"execution_result": result}

    return SwarmAgent(
        name="sandbox",
        role="Execute submitted code using the existing execution tool.",
        action=execute,
    )


def create_scoring_swarm_agent() -> SwarmAgent:
    """Adapt the existing ScoringAgent for the parallel swarm."""

    scoring_agent = ScoringAgent()

    def calculate_score(context: dict[str, Any]) -> dict[str, Any]:
        evaluation_data = context.get("evaluation")
        max_score = context.get("max_score")

        if not isinstance(evaluation_data, dict):
            raise ValueError(
                "Context must include evaluation as a dictionary."
            )

        if not isinstance(max_score, (int, float)) or isinstance(max_score, bool):
            raise ValueError(
                "Context must include max_score as a number."
            )

        evaluation = Evaluation(**evaluation_data)
        percentage = scoring_agent.percentage(evaluation, float(max_score))

        return {"score_percentage": percentage}

    return SwarmAgent(
        name="scoring",
        role="Calculate the evaluation score percentage.",
        action=calculate_score,
    )


def create_feedback_swarm_agent() -> SwarmAgent:
    """Adapt the existing FeedbackAgent for the parallel swarm."""

    feedback_agent = FeedbackAgent()

    def generate_feedback(context: dict[str, Any]) -> dict[str, Any]:
        evaluation_data = context.get("evaluation")

        if not isinstance(evaluation_data, dict):
            raise ValueError(
                "Context must include evaluation as a dictionary."
            )

        evaluation = Evaluation(**evaluation_data)
        feedback = feedback_agent.summarize(evaluation)

        return {"feedback": feedback}

    return SwarmAgent(
        name="feedback",
        role="Generate feedback from evaluation results.",
        action=generate_feedback,
    )


def create_result_publishing_swarm_agent() -> SwarmAgent:
    """Adapt the existing ResultPublishingAgent for the swarm."""

    publishing_agent = ResultPublishingAgent()

    def publish(context: dict[str, Any]) -> dict[str, Any]:
        result_data = context.get("result")

        if not isinstance(result_data, dict):
            raise ValueError(
                "Context must include result as a dictionary."
            )

        result = Result(**result_data)
        published_result = publishing_agent.publish(result)

        return {
            "published_result": published_result.model_dump()
        }

    return SwarmAgent(
        name="result_publishing",
        role="Publish a student's exam result using the existing publishing agent.",
        action=publish,
    )


def create_deep_research_swarm_agent() -> SwarmAgent:
    """
    Lab 9 Swarm Adapter: Adapt DeepResearchAgent for swarm orchestration pipelines.
    Extracts structured topic briefing and evidence tables asynchronously.
    """

    research_agent = DeepResearchAgent()

    def research(context: dict[str, Any]) -> dict[str, Any]:
        topic = context.get("topic")
        if not topic or not isinstance(topic, str):
            raise ValueError("Context must include 'topic' as a non-empty string.")

        depth = context.get("depth", "deep")
        focus_areas = context.get("focus_areas", [])
        max_sources = context.get("max_sources", 5)
        user_id = context.get("student_or_user_id")

        req = ResearchRequest(
            topic=topic,
            depth=depth,
            focus_areas=focus_areas,
            max_sources=max_sources,
            student_or_user_id=user_id,
        )

        briefing = research_agent.conduct_research(req)
        return {
            "briefing_id": briefing.id,
            "topic": briefing.topic,
            "summary": briefing.executive_summary,
            "evidence_count": len(briefing.evidence_table),
            "briefing": briefing.model_dump(),
        }

    return SwarmAgent(
        name="deep_research",
        role="Conduct technical topic inquiry, extract evidence, and build briefings (Lab 9).",
        action=research,
    )


from backend.agents.cloud_operations_agent import CloudOperationsAgent
from backend.models.cloud_ops import DiagnosisRequest


def create_cloud_operations_swarm_agent() -> SwarmAgent:
    """
    Lab 10 Swarm Adapter: Adapt CloudOperationsAgent for swarm orchestration pipelines.
    Diagnoses failed deployment logs and generates verified remediation patches asynchronously.
    """

    cloud_ops_agent = CloudOperationsAgent()

    def diagnose_and_remediate(context: dict[str, Any]) -> dict[str, Any]:
        service_name = context.get("service_name")
        if not service_name or not isinstance(service_name, str):
            raise ValueError("Context must include 'service_name' as a non-empty string.")

        raw_logs = context.get("raw_logs")
        if not raw_logs or not isinstance(raw_logs, str):
            raise ValueError("Context must include 'raw_logs' as a non-empty string.")

        environment = context.get("environment", "production")
        deployment_target = context.get("deployment_target", "kubernetes")
        deployment_config = context.get("deployment_config")
        incident_type = context.get("incident_type")
        user_id = context.get("user_id")

        req = DiagnosisRequest(
            service_name=service_name,
            environment=environment,
            deployment_target=deployment_target,
            raw_logs=raw_logs,
            deployment_config=deployment_config,
            incident_type=incident_type,
            user_id=user_id,
        )

        report = cloud_ops_agent.diagnose_and_fix(req)
        return {
            "incident_id": report.id,
            "service_name": report.service_name,
            "error_category": report.rca.error_category,
            "severity": report.rca.severity,
            "summary": report.rca.summary,
            "remediation_steps_count": len(report.remediation_steps),
            "patches_count": len(report.patches),
            "report": report.model_dump(),
        }

    return SwarmAgent(
        name="cloud_operations",
        role="Diagnose failed deployment logs, formulate RCA, and synthesize remediation patches (Lab 10).",
        action=diagnose_and_remediate,
    )


from backend.agents.sdlc_agent import SDLCFactoryAgent
from backend.models.sdlc import SDLCRequirementRequest


def create_sdlc_factory_swarm_agent() -> SwarmAgent:
    """
    Lab 11 Swarm Adapter: Adapt SDLCFactoryAgent for swarm orchestration pipelines.
    Autonomously transforms requirements into tested clean-architecture implementations.
    """

    sdlc_agent = SDLCFactoryAgent()

    def generate_software_project(context: dict[str, Any]) -> dict[str, Any]:
        project_name = context.get("project_name")
        if not project_name or not isinstance(project_name, str):
            raise ValueError("Context must include 'project_name' as a non-empty string.")

        requirement_text = context.get("requirement_text")
        if not requirement_text or not isinstance(requirement_text, str):
            raise ValueError("Context must include 'requirement_text' as a non-empty string.")

        target_language = context.get("target_language", "python")
        framework = context.get("framework", "fastapi")
        architecture_style = context.get("architecture_style", "clean_architecture")
        auto_execute_tests = context.get("auto_execute_tests", True)
        user_id = context.get("user_id")

        req = SDLCRequirementRequest(
            project_name=project_name,
            requirement_text=requirement_text,
            target_language=target_language,
            framework=framework,
            architecture_style=architecture_style,
            auto_execute_tests=auto_execute_tests,
            user_id=user_id,
        )

        artifact = sdlc_agent.generate_sdlc_project(req)
        return {
            "project_id": artifact.id,
            "project_name": artifact.project_name,
            "status": artifact.status,
            "user_stories_count": len(artifact.user_stories),
            "files_count": len(artifact.code_files),
            "tests_passed": artifact.test_run.passed,
            "tests_failed": artifact.test_run.failed,
            "coverage_pct": artifact.test_run.coverage_pct,
            "artifact": artifact.model_dump(),
        }

    return SwarmAgent(
        name="sdlc_factory",
        role="Execute end-to-end SDLC pipeline: requirements -> architecture -> code -> tests (Lab 11).",
        action=generate_software_project,
    )


from backend.agents.governance_agent import SafetyGovernanceAgent
from backend.models.governance import GovernanceAssessmentRequest


def create_safety_governance_swarm_agent() -> SwarmAgent:
    """
    Lab 12 Swarm Adapter: Adapt SafetyGovernanceAgent for swarm orchestration pipelines.
    Evaluates action payloads, scores multi-dimensional risk, assesses policy checks,
    and derives deterministic rollback strategies asynchronously.
    """

    governance_agent = SafetyGovernanceAgent()

    def assess_safety(context: dict[str, Any]) -> dict[str, Any]:
        action_title = context.get("action_title")
        if not action_title or not isinstance(action_title, str):
            raise ValueError("Context must include 'action_title' as a non-empty string.")

        proposed_payload = context.get("proposed_payload")
        if not proposed_payload or not isinstance(proposed_payload, str):
            raise ValueError("Context must include 'proposed_payload' as a non-empty string.")

        target_system = context.get("target_system", "production")
        initiator = context.get("initiator", "swarm_coordinator")
        declared_purpose = context.get("declared_purpose", "")

        req = GovernanceAssessmentRequest(
            action_title=action_title,
            target_system=target_system,
            proposed_payload=proposed_payload,
            initiator=initiator,
            declared_purpose=declared_purpose,
        )

        audit = governance_agent.assess_action(req)
        return {
            "audit_id": audit.id,
            "overall_risk_score": audit.overall_risk_score,
            "risk_tier": audit.risk_tier,
            "approval_status": audit.approval.status,
            "policy_violations_count": sum(1 for p in audit.policy_evaluations if p.status == "FAIL"),
            "rollback_strategy": audit.rollback_plan.strategy,
            "rollback_steps_count": len(audit.rollback_plan.steps),
            "audit": audit.model_dump(),
        }

    return SwarmAgent(
        name="safety_governance",
        role="Multi-dimensional risk scoring, policy evaluation, approval gating, and rollback planning (Lab 12).",
        action=assess_safety,
    )


from backend.agents.discipline_agent import DisciplineSpecificAgent
from backend.models.discipline import WorkletSolveRequest


def create_discipline_specific_swarm_agent() -> SwarmAgent:
    """
    Lab 13 Swarm Adapter: Adapt DisciplineSpecificAgent for swarm orchestration pipelines.
    Automates engineering domain calculations, derivations, code compliance checks,
    and Python simulations for ME (Mechanical), CE (Civil), and EE (Electrical).
    """

    discipline_agent = DisciplineSpecificAgent()

    def solve_worklet_action(context: dict[str, Any]) -> dict[str, Any]:
        discipline = context.get("discipline", "ME")
        worklet_type = context.get("worklet_type", "shaft_torsion_stress")
        title = context.get("title", "")
        problem_statement = context.get("problem_statement", "")
        parameters = context.get("parameters", {})
        user_id = context.get("user_id")

        req = WorkletSolveRequest(
            discipline=discipline,
            worklet_type=worklet_type,
            title=title,
            problem_statement=problem_statement,
            parameters=parameters,
            user_id=user_id,
            run_code_simulation=True,
        )

        artifact = discipline_agent.solve_worklet(req)
        return {
            "worklet_id": artifact.id,
            "discipline": artifact.discipline,
            "worklet_type": artifact.worklet_type,
            "title": artifact.title,
            "compliance_verdict": artifact.compliance_verdict,
            "derivation_steps_count": len(artifact.derivation_steps),
            "kpis_count": len(artifact.kpis),
            "compliance_checks_count": len(artifact.compliance_checks),
            "code_simulation_output": artifact.code_execution_stdout,
            "artifact": artifact.model_dump(),
        }

    return SwarmAgent(
        name="discipline_specific",
        role="Solve domain calculations, governing derivations, compliance checks, and simulation scripts for ME/CE/EE (Lab 13).",
        action=solve_worklet_action,
    )


from backend.agents.capstone_agent import CapstoneStudioAgent
from backend.models.capstone import CapstoneCreateRequest


def create_capstone_studio_swarm_agent() -> SwarmAgent:
    """
    Lab 14 Swarm Adapter: Adapt CapstoneStudioAgent for multi-agent swarm pipelines.
    Coordinates full team-owned autonomous agentic systems across Discovery,
    Architecture, SDLC Synthesis, Test Harness, and Governance Audits.
    """

    capstone_agent = CapstoneStudioAgent()

    def coordinate_capstone(context: dict[str, Any]) -> dict[str, Any]:
        team_name = context.get("team_name", "Autonomous Capstone Swarm")
        project_title = context.get("project_title", "Team-Owned Agentic System")
        domain = context.get("domain", "General Engineering")
        mission_statement = context.get("mission_statement", "")
        user_id = context.get("user_id")

        req = CapstoneCreateRequest(
            team_name=team_name,
            project_title=project_title,
            domain=domain,
            mission_statement=mission_statement,
            user_id=user_id,
            auto_execute_pipeline=True,
        )

        artifact = capstone_agent.create_project(req)
        return {
            "project_id": artifact.id,
            "team_name": artifact.team_name,
            "project_title": artifact.project_title,
            "domain": artifact.domain,
            "status": artifact.status,
            "stages_count": len(artifact.stages),
            "deliverables_count": len(artifact.deliverables),
            "tests_passed": artifact.test_run.passed,
            "risk_score": artifact.overall_risk_score,
            "artifact": artifact.model_dump(),
        }

    return SwarmAgent(
        name="capstone_studio",
        role="Orchestrate full team-owned autonomous agentic system across 5 pipeline stages (Lab 14).",
        action=coordinate_capstone,
    )



