class CapstonePromptBuilder:
    """Prompt builder for autonomous multi-agent Capstone Project Studio."""

    def build_prompt(
        self,
        team_name: str,
        project_title: str,
        domain: str,
        mission_statement: str,
        team_members: list[dict],
    ) -> str:
        return f"""You are the Capstone Studio Coordinator orchestrating an autonomous multi-agent engineering team.
Generate an end-to-end Capstone Project Portfolio across 5 engineering pipeline stages:

TEAM NAME: {team_name}
PROJECT TITLE: {project_title}
DOMAIN: {domain}
MISSION: {mission_statement}
ROSTER: {team_members}

OUTPUT REQUIREMENT:
Generate valid JSON conforming to the CapstoneProjectArtifact schema:
1. "team_members": Team members with specific roles (Lead Architect, Research Intelligence, SDLC Engineer, SRE, Governance).
2. "stages": 5 pipeline stage records (Discovery, Architecture, Implementation, Testing, Governance) with duration and deliverables.
3. "messages": Inter-agent communication logs showing stage handoffs and decision consensus.
4. "deliverables": Array of deliverables including architecture blueprints, clean implementation code files, test suites, and documentation.
5. "test_run": Simulated test runner metrics with total tests, passed count, and coverage.
6. "overall_risk_score": 0-100 governance risk rating.
7. "governance_tier": 'LOW', 'MEDIUM', 'HIGH', or 'CRITICAL'.
8. "architecture_diagram": ASCII or Mermaid system topology.
"""
