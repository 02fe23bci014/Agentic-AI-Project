import unittest
from backend.agents.discipline_agent import DisciplineSpecificAgent
from backend.agents.swarm_adapters import create_discipline_specific_swarm_agent
from backend.api.discipline_routes import (
    delete_discipline_worklet,
    execute_worklet_code,
    export_discipline_worklet,
    get_discipline_worklet,
    list_discipline_worklets,
    solve_discipline_worklet,
)
from backend.models.discipline import (
    ComplianceCheck,
    DerivationStep,
    DisciplineExportRequest,
    DisciplineWorkletArtifact,
    EngineeringKPI,
    ParameterItem,
    WorkletRunCodeRequest,
    WorkletSolveRequest,
)
from backend.skills.discipline_agents.prompt_builder import DisciplinePromptBuilder
from backend.skills.discipline_agents.synthesizer import DisciplineSynthesizer
from backend.skills.discipline_agents.validator import DisciplineValidator
from backend.tools.discipline_tool import DisciplineTool


class TestDisciplineSpecificComponents(unittest.TestCase):
    """Test suite for Lab 13: Discipline-Specific Agents (ME / CE / EE domain worklet)."""

    def setUp(self):
        self.tool = DisciplineTool()
        self.validator = DisciplineValidator()
        self.builder = DisciplinePromptBuilder()
        self.synthesizer = DisciplineSynthesizer()
        self.agent = DisciplineSpecificAgent()

    def test_models_creation(self):
        param = ParameterItem(
            name="Torque",
            symbol="T",
            value=1200.0,
            unit="N·m",
            description="Applied twisting moment",
        )
        self.assertEqual(param.symbol, "T")

        step = DerivationStep(
            step_number=1,
            title="Calculate Polar Moment of Inertia",
            formula=r"J = \frac{\pi d^4}{32}",
            substitution="J = pi * (0.05)^4 / 32 = 6.136e-7 m^4",
            result_value=6.136e-7,
            unit="m^4",
        )
        self.assertEqual(step.step_number, 1)

        comp = ComplianceCheck(
            standard_code="ASME B106.1M",
            parameter_checked="Torsional Safety Factor",
            threshold="SF >= 1.5",
            actual_value="SF = 2.95",
            status="PASS",
        )
        self.assertEqual(comp.status, "PASS")

        kpi = EngineeringKPI(
            label="Safety Factor",
            value=2.95,
            unit="",
            status="OPTIMAL",
        )
        self.assertEqual(kpi.label, "Safety Factor")

    def test_tool_execution_and_formatting(self):
        code = "print('Engineering verification test: J = 6.14e-7 m4')\n"
        stdout = self.tool.execute_python_verification(code)
        self.assertIn("Engineering verification test", stdout)

        artifact = DisciplineWorkletArtifact(
            id="wrk-me-sample",
            discipline="ME",
            worklet_type="shaft_torsion_stress",
            title="Sample Shaft Worklet",
            problem_statement="Test shaft analysis",
            parameters=[
                ParameterItem(name="Torque", symbol="T", value=1000.0, unit="N*m", description="Applied torque")
            ],
            governing_equations=[r"J = \frac{\pi d^4}{32}"],
            derivation_steps=[
                DerivationStep(
                    step_number=1,
                    title="Compute J",
                    formula="J = pi*d^4/32",
                    substitution="pi*(0.05)^4/32",
                    result_value=6.136e-7,
                    unit="m^4",
                )
            ],
            kpis=[EngineeringKPI(label="Safety Factor", value=2.5, unit="", status="OPTIMAL")],
            compliance_checks=[
                ComplianceCheck(
                    standard_code="ASME B106.1M",
                    parameter_checked="Safety Factor",
                    threshold="SF >= 1.5",
                    actual_value="SF = 2.5",
                    status="PASS",
                )
            ],
            compliance_verdict="COMPLIANT",
            executable_code=code,
            code_execution_stdout=stdout,
        )

        md = self.tool.format_worklet_markdown(artifact)
        self.assertIn("# Mechanical Engineering Worklet", md)
        self.assertIn("ASME B106.1M", md)

        js = self.tool.format_worklet_json(artifact)
        self.assertIn("wrk-me-sample", js)

    def test_synthesizer_mechanical_shaft(self):
        data = self.synthesizer.synthesize(
            discipline="ME",
            worklet_type="shaft_torsion_stress",
            title="Solid Drive Shaft Torsion Analysis",
            parameters={"torque": 1500.0, "diameter_mm": 55.0},
        )
        self.assertTrue(self.validator.validate(data))
        self.assertEqual(data["discipline"], "ME")
        self.assertGreaterEqual(len(data["derivation_steps"]), 3)
        self.assertIn("ASME B106.1M", [c["standard_code"] for c in data["compliance_checks"]])

    def test_synthesizer_civil_rcc_beam(self):
        data = self.synthesizer.synthesize(
            discipline="CE",
            worklet_type="rcc_beam_flexure",
            title="RCC Beam Ultimate Moment Capacity",
            parameters={"span_m": 6.5, "dead_load_kn_m": 20.0, "live_load_kn_m": 15.0},
        )
        self.assertTrue(self.validator.validate(data))
        self.assertEqual(data["discipline"], "CE")
        self.assertGreaterEqual(len(data["derivation_steps"]), 3)
        self.assertIn("ACI 318-19", data["compliance_checks"][0]["standard_code"])

    def test_synthesizer_electrical_rlc(self):
        data = self.synthesizer.synthesize(
            discipline="EE",
            worklet_type="rlc_filter_resonance",
            title="Tuned RLC Tank Circuit Selectivity",
            parameters={"r_ohms": 40.0, "l_millihenry": 12.0, "c_microfarad": 0.2},
        )
        self.assertTrue(self.validator.validate(data))
        self.assertEqual(data["discipline"], "EE")
        self.assertGreaterEqual(len(data["kpis"]), 3)
        self.assertIn("IEEE", data["compliance_checks"][0]["standard_code"])

    def test_agent_lifecycle_and_persistence(self):
        req = WorkletSolveRequest(
            discipline="EE",
            worklet_type="three_phase_power_factor",
            title="Industrial Plant Power Factor Correction",
            parameters={"apparent_power_kva": 300.0, "initial_pf": 0.75, "target_pf": 0.95},
            user_id="student_engineer_01",
            run_code_simulation=True,
        )
        artifact = self.agent.solve_worklet(req)
        self.assertIsInstance(artifact, DisciplineWorkletArtifact)
        self.assertEqual(artifact.discipline, "EE")
        self.assertIsNotNone(artifact.code_execution_stdout)

        # Retrieve
        retrieved = self.agent.get_worklet(artifact.id)
        self.assertEqual(retrieved.id, artifact.id)

        # List
        worklets = self.agent.list_worklets(discipline="EE")
        self.assertTrue(any(w["id"] == artifact.id for w in worklets))

        # Re-run custom simulation code
        custom_code = "print('Re-running custom EE power simulation: capacitor bank active!')\n"
        updated = self.agent.run_code(artifact.id, custom_code=custom_code)
        self.assertIn("Re-running custom EE power simulation", updated.code_execution_stdout or "")

        # Export
        md_text = self.agent.export_worklet(updated, "markdown")
        self.assertIn("# Electrical Engineering Worklet", md_text)

        # Cleanup
        deleted = self.agent.delete_worklet(artifact.id)
        self.assertTrue(deleted)

    def test_api_routes(self):
        req = WorkletSolveRequest(
            discipline="ME",
            worklet_type="carnot_rankine_heat_engine",
            title="Thermal Efficiency Verification",
            parameters={"th_temp_c": 560.0, "tc_temp_c": 30.0, "heat_input_qh_mw": 60.0},
        )
        artifact = solve_discipline_worklet(req)
        self.assertEqual(artifact.discipline, "ME")

        fetched = get_discipline_worklet(artifact.id)
        self.assertEqual(fetched.id, artifact.id)

        code_res = execute_worklet_code(artifact.id, WorkletRunCodeRequest(custom_code="print('API code execution')"))
        self.assertIn("API code execution", code_res.code_execution_stdout or "")

        exp_res = export_discipline_worklet(DisciplineExportRequest(worklet=code_res, format="json"))
        self.assertEqual(exp_res["format"], "json")
        self.assertIn(artifact.id, exp_res["content"])

        del_res = delete_discipline_worklet(artifact.id)
        self.assertTrue(del_res["deleted"])

    def test_swarm_adapter(self):
        swarm_agent = create_discipline_specific_swarm_agent()
        self.assertEqual(swarm_agent.name, "discipline_specific")
        res = swarm_agent.action({
            "discipline": "CE",
            "worklet_type": "retaining_wall_stability",
            "title": "Highway Embankment Retaining Wall",
            "parameters": {"height_h_m": 5.0, "footing_width_b_m": 3.0},
        })
        self.assertIn("worklet_id", res)
        self.assertEqual(res["discipline"], "CE")
        self.assertGreater(res["derivation_steps_count"], 0)


if __name__ == "__main__":
    unittest.main()
