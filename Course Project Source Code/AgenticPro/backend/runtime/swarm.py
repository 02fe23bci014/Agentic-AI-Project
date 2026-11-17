
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class AgentResult:
    """Stores the result produced by one swarm agent."""

    agent_name: str
    status: str = "completed"
    findings: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


@dataclass
class SwarmReport:
    """Stores the combined results from the agent swarm."""

    submission_id: str
    status: str = "running"
    agent_results: dict[str, AgentResult] = field(default_factory=dict)
    merged_findings: dict[str, Any] = field(default_factory=dict)
    conflicts: list[str] = field(default_factory=list)
    critique: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class SwarmAgent:
    """Defines an agent and its role in the swarm."""

    name: str
    role: str
    action: Callable[[dict[str, Any]], dict[str, Any]]


class SwarmCoordinator:
    """Runs agents in parallel and coordinates their results."""

    def __init__(self, max_workers: int | None = None) -> None:
        self.agents: dict[str, SwarmAgent] = {}
        self.max_workers = max_workers

    def add_agent(self, agent: SwarmAgent) -> None:
        """Register an agent with the coordinator."""

        if agent.name in self.agents:
            raise ValueError(
                f"Agent '{agent.name}' is already registered."
            )

        self.agents[agent.name] = agent

    def run(
        self,
        submission_id: str,
        context: dict[str, Any],
    ) -> SwarmReport:
        """Run registered agents concurrently and merge their findings."""

        report = SwarmReport(submission_id=submission_id)

        if not self.agents:
            report.status = "error"
            report.errors.append("No agents are registered.")
            return report

        results: dict[str, AgentResult] = {}

        def execute_agent(agent: SwarmAgent) -> AgentResult:
            # Give each agent its own context dictionary.
            agent_context = dict(context)

            try:
                findings = agent.action(agent_context)

                if not isinstance(findings, dict):
                    raise TypeError(
                        f"Agent '{agent.name}' must return a dictionary."
                    )

                return AgentResult(
                    agent_name=agent.name,
                    findings=findings,
                )

            except Exception as error:
                return AgentResult(
                    agent_name=agent.name,
                    status="error",
                    errors=[str(error)],
                )

        worker_count = self.max_workers or len(self.agents)

        try:
            with ThreadPoolExecutor(max_workers=worker_count) as executor:
                futures = {
                    executor.submit(execute_agent, agent): agent.name
                    for agent in self.agents.values()
                }

                for future in as_completed(futures):
                    agent_name = futures[future]

                    try:
                        results[agent_name] = future.result()
                    except Exception as error:
                        results[agent_name] = AgentResult(
                            agent_name=agent_name,
                            status="error",
                            errors=[str(error)],
                        )

        except Exception as error:
            report.status = "error"
            report.errors.append(
                f"Swarm execution failed: {error}"
            )
            return report

        # Preserve the registration order when storing results.
        for agent_name in self.agents:
            result = results[agent_name]
            report.agent_results[agent_name] = result

            if result.status == "error":
                for error in result.errors:
                    report.errors.append(
                        f"{agent_name}: {error}"
                    )

        # Merge findings. Different agents should use different keys
        # unless they intentionally report the same fact.
        for agent_name, result in report.agent_results.items():
            if result.status != "completed":
                continue

            for key, value in result.findings.items():
                if key not in report.merged_findings:
                    report.merged_findings[key] = value
                    continue

                existing_value = report.merged_findings[key]

                if existing_value != value:
                    report.conflicts.append(
                        f"Conflicting values for '{key}' from "
                        f"multiple agents. Existing value: "
                        f"{existing_value!r}; {agent_name} reported: "
                        f"{value!r}."
                    )

        # Critique the combined findings.
        report.critique = self.critique_report(report)

        if report.errors:
            report.status = "error"
        elif report.conflicts:
            report.status = "completed_with_conflicts"
        else:
            report.status = "completed"

        return report

    def critique_report(
        self,
        report: SwarmReport,
    ) -> list[str]:
        """Check for failed agents, conflicts, and missing findings."""

        critique: list[str] = []

        if not report.agent_results:
            critique.append("No agent results were collected.")

        for agent_name, result in report.agent_results.items():
            if result.status != "completed":
                critique.append(
                    f"Agent '{agent_name}' did not complete successfully."
                )

        if report.conflicts:
            critique.append(
                "Conflicting findings require review before being used."
            )

        if not report.merged_findings:
            critique.append("No findings were produced by the swarm.")

        return critique

    def resolve_conflicts(
        self,
        report: SwarmReport,
        resolutions: dict[str, Any],
    ) -> SwarmReport:
        """
        Apply explicit, caller-provided conflict resolutions.

        The caller must provide the approved value for each conflicting key.
        This method does not automatically decide which agent is correct.
        """

        conflict_keys = {
            key
            for key in report.merged_findings
            if any(
                f"Conflicting values for '{key}'" in conflict
                for conflict in report.conflicts
            )
        }

        unresolved = conflict_keys - resolutions.keys()

        if unresolved:
            report.errors.append(
                "Missing explicit resolutions for: "
                + ", ".join(sorted(unresolved))
            )
            report.status = "completed_with_conflicts"
            return report

        report.merged_findings.update(resolutions)
        report.conflicts.clear()
        report.errors.clear()

        # Rebuild critique after applying the supplied resolutions.
        report.critique = self.critique_report(report)

        failed_agents = any(
            result.status != "completed"
            for result in report.agent_results.values()
        )

        if failed_agents:
            report.status = "error"
        else:
            report.status = "completed"

        return report
