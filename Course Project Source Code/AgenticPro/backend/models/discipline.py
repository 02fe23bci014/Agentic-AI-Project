from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class ParameterItem(BaseModel):
    name: str = Field(description="Parameter key e.g. torque or beam_span")
    symbol: str = Field(description="Mathematical symbol e.g. T, L, R")
    value: float = Field(description="Numerical value in base units")
    unit: str = Field(description="Unit of measurement e.g. N*m, m, MPa, Ohm, uF")
    description: str = Field(description="Brief explanation of parameter")


class DerivationStep(BaseModel):
    step_number: int = Field(ge=1, description="Sequential step index")
    title: str = Field(description="Action title e.g. Calculate Polar Moment of Inertia")
    formula: str = Field(description="Analytical mathematical equation in LaTeX or text")
    substitution: str = Field(description="Formula populated with numeric arguments")
    result_value: float = Field(description="Calculated value for this intermediate step")
    unit: str = Field(description="Unit of intermediate result")
    notes: str | None = Field(default=None, description="Physical assumption or boundary condition")


class ComplianceCheck(BaseModel):
    standard_code: str = Field(description="Regulatory code e.g. ASME B106.1M, ACI 318-19, IEEE Std 519")
    parameter_checked: str = Field(description="Metric under evaluation e.g. Max Torsional Shear Stress")
    threshold: str = Field(description="Threshold rule e.g. tau <= 50.0 MPa")
    actual_value: str = Field(description="Observed result value e.g. tau = 39.1 MPa")
    status: str = Field(description="'PASS', 'FAIL', 'MARGINAL'")
    recommendation: str | None = Field(default=None, description="Engineering recommendation or redesign suggestion")


class EngineeringKPI(BaseModel):
    label: str = Field(description="Display label e.g. Safety Factor (SF), Thermal Efficiency (eta)")
    value: float = Field(description="Numerical value")
    unit: str = Field(default="", description="Unit of KPI (if dimensioned)")
    status: str = Field(default="OPTIMAL", description="'OPTIMAL', 'ACCEPTABLE', 'WARNING', 'CRITICAL'")


class DisciplineWorkletArtifact(BaseModel):
    id: str = Field(description="Unique worklet ID e.g. wrk-me-20261117-01")
    discipline: str = Field(description="'ME' (Mechanical), 'CE' (Civil), 'EE' (Electrical)")
    worklet_type: str = Field(description="Worklet template key e.g. shaft_torsion_stress, rcc_beam_flexure")
    title: str = Field(description="Descriptive engineering worklet title")
    problem_statement: str = Field(description="Context and engineering requirements")
    parameters: list[ParameterItem] = Field(default_factory=list)
    governing_equations: list[str] = Field(default_factory=list)
    derivation_steps: list[DerivationStep] = Field(default_factory=list)
    kpis: list[EngineeringKPI] = Field(default_factory=list)
    compliance_checks: list[ComplianceCheck] = Field(default_factory=list)
    compliance_verdict: str = Field(default="COMPLIANT", description="'COMPLIANT', 'NON_COMPLIANT', 'MARGINAL'")
    executable_code: str = Field(description="Python verification code block (NumPy/SciPy/SymPy)")
    code_execution_stdout: str | None = Field(default=None, description="Captured console stdout from verification execution")
    schematic_svg_or_ascii: str | None = Field(default=None, description="ASCII or SVG representation of engineering system")
    created_by: str | None = Field(default=None, description="User or agent author ID")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class WorkletSolveRequest(BaseModel):
    discipline: str = Field(description="'ME', 'CE', 'EE'")
    worklet_type: str = Field(description="Template type e.g. shaft_torsion_stress, rcc_beam_flexure, rlc_filter_resonance")
    title: str = Field(default="", description="Optional custom title")
    problem_statement: str | None = Field(default="", description="Custom problem context")
    parameters: dict[str, float] = Field(default_factory=dict, description="Dictionary of parameter key to numeric values")
    unit_system: str = Field(default="SI", description="'SI' or 'Imperial'")
    user_id: str | None = Field(default=None, description="Username or student ID")
    run_code_simulation: bool = Field(default=True, description="Whether to execute verification script immediately")


class WorkletRunCodeRequest(BaseModel):
    custom_code: str | None = Field(default=None, description="Custom Python script to execute against worklet parameters")


class DisciplineExportRequest(BaseModel):
    worklet: DisciplineWorkletArtifact
    format: str = Field(default="markdown", description="'markdown' or 'json'")
