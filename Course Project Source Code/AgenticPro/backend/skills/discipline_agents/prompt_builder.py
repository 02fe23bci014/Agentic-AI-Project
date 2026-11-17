class DisciplinePromptBuilder:
    """Prompt builder for discipline-specific engineering agents (ME / CE / EE)."""

    def build_prompt(
        self,
        discipline: str,
        worklet_type: str,
        title: str,
        parameters: dict[str, float],
        problem_statement: str = "",
        unit_system: str = "SI",
    ) -> str:
        return f"""You are a licensed Senior Professional Engineer specializing in {discipline} ({'Mechanical' if discipline == 'ME' else 'Civil' if discipline == 'CE' else 'Electrical'} Engineering).
Analyze the following engineering problem and synthesize a formal calculation worklet:

DISCIPLINE: {discipline}
WORKLET TYPE: {worklet_type}
TITLE: {title}
UNIT SYSTEM: {unit_system}
PROBLEM STATEMENT:
{problem_statement or 'Perform standard engineering verification for specified parameters.'}

INPUT PARAMETERS:
{parameters}

OUTPUT REQUIREMENT:
Generate valid JSON matching the DisciplineWorkletArtifact structure with:
1. "parameters": Array of validated ParameterItem objects with units and descriptions.
2. "governing_equations": Array of fundamental LaTeX physics/engineering formulas.
3. "derivation_steps": Array of DerivationStep objects showing formula, numeric substitution, intermediate value, and engineering notes.
4. "kpis": Key engineering performance indicators (e.g. Safety Factor, Capacity, Efficiency, Resonant Frequency).
5. "compliance_checks": Formal checks against engineering codes (ASME, AISC, ACI, IEEE, NEC) with status ('PASS', 'FAIL', 'MARGINAL').
6. "compliance_verdict": 'COMPLIANT', 'NON_COMPLIANT', or 'MARGINAL'.
7. "executable_code": Clean Python script (using math/numpy) verifying all calculations and printing results.
"""
