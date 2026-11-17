
from backend.models.evaluation import Evaluation
from backend.models.submission import Submission
from backend.runtime.state import WorkflowState
from backend.runtime.swarm import SwarmCoordinator
from backend.agents.swarm_adapters import (
    create_scoring_swarm_agent,
    create_feedback_swarm_agent,
)
from backend.tools.test_case_tool import get_test_cases
from backend.tools.code_execution_tool import execute_code
from backend.skills.code_evaluation.evaluator import evaluate_outputs


def evaluate_submission(
    submission: Submission,
) -> tuple[WorkflowState, Evaluation]:
    state = WorkflowState(
        submission_id=submission.id,
        status="running",
    )

    try:
        # Step 1: Load test cases.
        cases = get_test_cases(submission.question_id)

        # Step 2: Execute the submitted code against each test case.
        actual_outputs = []

        for case in cases:
            result = execute_code(
                submission.source_code,
                submission.language,
                case.stdin,
            )
            actual_outputs.append(str(result.get("stdout", "")))

        # Step 3: Evaluate the outputs.
        evaluation = evaluate_outputs(
            submission.id,
            cases,
            actual_outputs,
        )

        # Step 4: Calculate the maximum possible score.
        max_score = sum(case.points for case in cases)

        # Step 5: Run scoring and feedback agents in parallel.
        coordinator = SwarmCoordinator(max_workers=2)

        coordinator.add_agent(create_scoring_swarm_agent())
        coordinator.add_agent(create_feedback_swarm_agent())

        report = coordinator.run(
            submission_id=submission.id,
            context={
                "evaluation": evaluation.model_dump(),
                "max_score": max_score,
            },
        )

        # Save the evaluation even if a supporting agent fails.
        state.outputs["evaluation"] = evaluation.model_dump()
        state.outputs["max_score"] = max_score

        if report.status != "completed":
            state.status = "error"
            state.errors.extend(report.errors)
            state.outputs["swarm_status"] = report.status
            state.outputs["swarm_findings"] = report.merged_findings
            state.outputs["swarm_critique"] = report.critique
            return state, evaluation

        # Step 6: Save the swarm findings.
        state.outputs["swarm_status"] = report.status
        state.outputs["swarm_findings"] = report.merged_findings
        state.outputs["swarm_critique"] = report.critique
        state.status = "completed"

        return state, evaluation

    except Exception as error:
        state.status = "error"
        state.errors.append(str(error))
        raise
