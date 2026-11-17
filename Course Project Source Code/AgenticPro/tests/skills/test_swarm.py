
import pytest

from backend.runtime.swarm import SwarmAgent, SwarmCoordinator


def test_swarm_runs_multiple_agents():
    coordinator = SwarmCoordinator(max_workers=2)

    coordinator.add_agent(
        SwarmAgent(
            name="agent_a",
            role="Returns a score",
            action=lambda context: {"score": 80},
        )
    )
    coordinator.add_agent(
        SwarmAgent(
            name="agent_b",
            role="Returns a status",
            action=lambda context: {"status": "passed"},
        )
    )

    report = coordinator.run("submission-001", {})

    assert report.status == "completed"
    assert report.merged_findings["score"] == 80
    assert report.merged_findings["status"] == "passed"


def test_swarm_detects_conflicting_findings():
    coordinator = SwarmCoordinator(max_workers=2)

    coordinator.add_agent(
        SwarmAgent(
            name="reviewer_a",
            role="First reviewer",
            action=lambda context: {"score": 80},
        )
    )
    coordinator.add_agent(
        SwarmAgent(
            name="reviewer_b",
            role="Second reviewer",
            action=lambda context: {"score": 90},
        )
    )

    report = coordinator.run("submission-002", {})

    assert report.status == "completed_with_conflicts"
    assert len(report.conflicts) == 1
    assert "score" in report.conflicts[0]


def test_swarm_handles_agent_failure():
    coordinator = SwarmCoordinator()

    def failing_agent(context):
        raise RuntimeError("Simulated agent failure")

    coordinator.add_agent(
        SwarmAgent(
            name="failing_agent",
            role="Test error handling",
            action=failing_agent,
        )
    )

    report = coordinator.run("submission-003", {})

    assert report.status == "error"
    assert any(
        "Simulated agent failure" in error
        for error in report.errors
    )


def test_swarm_rejects_duplicate_agent_names():
    coordinator = SwarmCoordinator()

    agent = SwarmAgent(
        name="reviewer",
        role="Test duplicate registration",
        action=lambda context: {"score": 80},
    )

    coordinator.add_agent(agent)

    with pytest.raises(ValueError, match="already registered"):
        coordinator.add_agent(agent)
