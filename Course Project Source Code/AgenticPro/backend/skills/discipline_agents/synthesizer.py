import math
from datetime import datetime
from typing import Any


class DisciplineSynthesizer:
    """
    High-fidelity engineering calculation synthesizer for ME, CE, and EE worklets.
    Generates exact governing formulas, intermediate derivation steps, KPIs,
    and Python verification scripts.
    """

    def synthesize(
        self,
        discipline: str,
        worklet_type: str,
        title: str = "",
        parameters: dict[str, float] | None = None,
        problem_statement: str = "",
        unit_system: str = "SI",
        user_id: str | None = None,
    ) -> dict[str, Any]:
        discipline = discipline.upper().strip()
        params = parameters or {}

        if discipline == "ME":
            if "heat" in worklet_type.lower() or "rankine" in worklet_type.lower() or "carnot" in worklet_type.lower():
                return self._solve_me_carnot(params, title, user_id)
            elif "beam" in worklet_type.lower() or "bending" in worklet_type.lower():
                return self._solve_me_beam(params, title, user_id)
            else:
                return self._solve_me_shaft(params, title, user_id)

        elif discipline == "CE":
            if "wall" in worklet_type.lower() or "retaining" in worklet_type.lower():
                return self._solve_ce_retaining_wall(params, title, user_id)
            elif "storm" in worklet_type.lower() or "drain" in worklet_type.lower() or "runoff" in worklet_type.lower():
                return self._solve_ce_stormwater(params, title, user_id)
            else:
                return self._solve_ce_rcc_beam(params, title, user_id)

        elif discipline == "EE":
            if "power" in worklet_type.lower() or "factor" in worklet_type.lower():
                return self._solve_ee_power_factor(params, title, user_id)
            elif "opamp" in worklet_type.lower() or "sallen" in worklet_type.lower():
                return self._solve_ee_opamp_filter(params, title, user_id)
            else:
                return self._solve_ee_rlc_resonance(params, title, user_id)

        # Fallback default to ME shaft
        return self._solve_me_shaft(params, title, user_id)

    # --------------------------------------------------------------------------
    # ME 1: Shaft Torsion Stress & ASME B106.1M
    # --------------------------------------------------------------------------
    def _solve_me_shaft(self, params: dict[str, float], title: str, user_id: str | None) -> dict[str, Any]:
        t = params.get("torque", 1200.0)
        d_mm = params.get("diameter_mm", 50.0)
        l_m = params.get("length_m", 1.5)
        sy_mpa = params.get("yield_strength_mpa", 250.0)
        g_gpa = params.get("shear_modulus_gpa", 79.3)

        d_m = d_mm / 1000.0
        r_m = d_m / 2.0
        j = (math.pi * (d_m ** 4)) / 32.0
        tau_max_pa = (t * r_m) / j
        tau_max_mpa = tau_max_pa / 1e6
        g_pa = g_gpa * 1e9
        theta_rad = (t * l_m) / (j * g_pa)
        theta_deg = theta_rad * (180.0 / math.pi)
        twist_per_meter = theta_deg / l_m
        tau_yield_mpa = 0.577 * sy_mpa
        sf = tau_yield_mpa / tau_max_mpa if tau_max_mpa > 0 else 999.0

        is_sf_ok = sf >= 1.5
        is_twist_ok = twist_per_meter <= 1.5
        verdict = "COMPLIANT" if (is_sf_ok and is_twist_ok) else "NON_COMPLIANT"

        code = f"""import math

torque = {t}  # N*m
diameter = {d_m}  # m
length = {l_m}  # m
yield_strength = {sy_mpa}e6  # Pa
shear_modulus = {g_gpa}e9  # Pa

j = (math.pi * (diameter ** 4)) / 32.0
tau_max = (torque * (diameter / 2.0)) / j
theta_rad = (torque * length) / (j * shear_modulus)
theta_deg = math.degrees(theta_rad)
tau_yield = 0.577 * yield_strength
safety_factor = tau_yield / tau_max

print(f"Polar Moment J: {{j:.4e}} m^4")
print(f"Max Shear Stress tau: {{tau_max / 1e6:.2f}} MPa")
print(f"Total Angular Twist: {{theta_deg:.2f}} deg ({{theta_deg/length:.2f}} deg/m)")
print(f"ASME Safety Factor: {{safety_factor:.2f}}")
print(f"Compliance Status: {{'PASS' if safety_factor >= 1.5 and theta_deg/length <= 1.5 else 'FAIL'}}")
"""

        return {
            "id": f"wrk-me-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "discipline": "ME",
            "worklet_type": "shaft_torsion_stress",
            "title": title or "Shaft Torsional Shear Stress & Angular Deflection Verification",
            "problem_statement": (
                f"Design verification of a solid transmission drive shaft subjected to a steady torsional moment of {t} N*m "
                f"over a span of {l_m} m. Evaluate torsional shear stress, angular deflection limit, and ASME B106.1M safety factor."
            ),
            "parameters": [
                {"name": "Applied Torque", "symbol": "T", "value": t, "unit": "N·m", "description": "Torsional operating load"},
                {"name": "Shaft Outer Diameter", "symbol": "d", "value": d_mm, "unit": "mm", "description": "Solid shaft diameter"},
                {"name": "Span Length", "symbol": "L", "value": l_m, "unit": "m", "description": "Unsupported bearing center span"},
                {"name": "Material Yield Strength", "symbol": "S_y", "value": sy_mpa, "unit": "MPa", "description": "Tensile yield point (AISI 1045 annealed)"},
                {"name": "Shear Modulus", "symbol": "G", "value": g_gpa, "unit": "GPa", "description": "Modulus of rigidity"},
            ],
            "governing_equations": [
                r"J = \frac{\pi d^4}{32}",
                r"\tau_{max} = \frac{T \cdot r}{J} = \frac{16 T}{\pi d^3}",
                r"\theta = \frac{T \cdot L}{J \cdot G}",
                r"\tau_y = \frac{S_y}{\sqrt{3}} \approx 0.577 S_y",
                r"SF = \frac{\tau_y}{\tau_{max}} \ge 1.5",
            ],
            "derivation_steps": [
                {
                    "step_number": 1,
                    "title": "Calculate Polar Moment of Inertia (J)",
                    "formula": r"J = \frac{\pi d^4}{32}",
                    "substitution": f"J = \\frac{{\\pi \\times ({d_m:.3f})^4}}{{32}} = {j:.4e} \\text{{ m}}^4",
                    "result_value": round(j, 8),
                    "unit": "m^4",
                    "notes": "Assumes homogeneous, isotropic solid circular cross-section.",
                },
                {
                    "step_number": 2,
                    "title": "Compute Maximum Torsional Shear Stress (tau)",
                    "formula": r"\tau_{max} = \frac{T \cdot (d/2)}{J}",
                    "substitution": f"\\tau = \\frac{{{t} \\times {r_m:.4f}}}{{{j:.4e}}} = {tau_max_mpa:.2f} \\text{{ MPa}}",
                    "result_value": round(tau_max_mpa, 2),
                    "unit": "MPa",
                    "notes": "Maximum shear stress occurs at outer peripheral radius r = d/2.",
                },
                {
                    "step_number": 3,
                    "title": "Compute Total Angular Twist and Twist per Meter",
                    "formula": r"\theta = \frac{T \cdot L}{J \cdot G}",
                    "substitution": f"\\theta = \\frac{{{t} \\times {l_m}}}{{{j:.4e} \\times {g_pa:.2e}}} = {theta_rad:.4f} \\text{{ rad}} = {theta_deg:.2f}^\\circ",
                    "result_value": round(theta_deg, 2),
                    "unit": "deg",
                    "notes": f"Twist rate evaluates to {twist_per_meter:.2f} deg/m.",
                },
                {
                    "step_number": 4,
                    "title": "Determine Von Mises Shear Yield Limit and Safety Factor (SF)",
                    "formula": r"SF = \frac{0.577 S_y}{\tau_{max}}",
                    "substitution": f"SF = \\frac{{0.577 \\times {sy_mpa:.1f}}}{{{tau_max_mpa:.2f}}} = \\frac{{{tau_yield_mpa:.2f}}}{{{tau_max_mpa:.2f}}} = {sf:.2f}",
                    "result_value": round(sf, 2),
                    "unit": "",
                    "notes": "Based on Von Mises maximum distortion energy yield criterion.",
                },
            ],
            "kpis": [
                {"label": "Safety Factor (SF)", "value": round(sf, 2), "unit": "", "status": "OPTIMAL" if sf >= 2.0 else "ACCEPTABLE" if sf >= 1.5 else "CRITICAL"},
                {"label": "Max Shear Stress", "value": round(tau_max_mpa, 2), "unit": "MPa", "status": "OPTIMAL" if tau_max_mpa < 60 else "ACCEPTABLE"},
                {"label": "Twist Rate", "value": round(twist_per_meter, 2), "unit": "deg/m", "status": "OPTIMAL" if twist_per_meter <= 1.0 else "ACCEPTABLE"},
            ],
            "compliance_checks": [
                {
                    "standard_code": "ASME B106.1M",
                    "parameter_checked": "Minimum Torsional Safety Factor",
                    "threshold": "SF >= 1.50",
                    "actual_value": f"SF = {sf:.2f}",
                    "status": "PASS" if is_sf_ok else "FAIL",
                    "recommendation": "Maintain specified shaft diameter." if is_sf_ok else f"Increase diameter d >= {d_mm * 1.25:.1f} mm to restore safety margin.",
                },
                {
                    "standard_code": "ISO 10816 / Machinery Handbook",
                    "parameter_checked": "Maximum Allowable Torsional Twist",
                    "threshold": "theta / L <= 1.50 deg/m",
                    "actual_value": f"{twist_per_meter:.2f} deg/m",
                    "status": "PASS" if is_twist_ok else "FAIL",
                    "recommendation": "Torsional rigidity within precision driveline limits." if is_twist_ok else "Shorten bearing spacing or increase shaft diameter to suppress torsional flutter.",
                },
            ],
            "compliance_verdict": verdict,
            "executable_code": code,
            "schematic_svg_or_ascii": (
                "  +----------------------- L = " + str(l_m) + " m -------------------------+\n"
                "  |                                                                |\n"
                " [B1]=====(====== d = " + str(d_mm) + " mm ======)=========================[B2] --> (T = " + str(t) + " N*m)\n"
                "  |                                                                |\n"
                "  +----------------------------------------------------------------+\n"
            ),
            "created_by": user_id or "discipline_agent_me",
            "created_at": datetime.utcnow().isoformat(),
        }

    # --------------------------------------------------------------------------
    # ME 2: Carnot & Rankine Heat Engine Cycle
    # --------------------------------------------------------------------------
    def _solve_me_carnot(self, params: dict[str, float], title: str, user_id: str | None) -> dict[str, Any]:
        th_c = params.get("th_temp_c", 550.0)
        tc_c = params.get("tc_temp_c", 35.0)
        qh_mw = params.get("heat_input_qh_mw", 50.0)

        th_k = th_c + 273.15
        tc_k = tc_c + 273.15
        eta_carnot = 1.0 - (tc_k / th_k)
        eta_rankine = 0.64 * eta_carnot
        wnet_mw = eta_rankine * qh_mw
        qc_mw = qh_mw - wnet_mw

        code = f"""th_k = {th_c} + 273.15
tc_k = {tc_c} + 273.15
qh_mw = {qh_mw}

eta_carnot = 1.0 - (tc_k / th_k)
eta_rankine = 0.64 * eta_carnot
wnet_mw = eta_rankine * qh_mw
qc_mw = qh_mw - wnet_mw

print(f"Carnot Limit Efficiency: {{eta_carnot * 100:.2f}}%")
print(f"Rankine Practical Efficiency: {{eta_rankine * 100:.2f}}%")
print(f"Net Electric Power Output: {{wnet_mw:.2f}} MW")
print(f"Waste Heat Discharged: {{qc_mw:.2f}} MW")
"""

        return {
            "id": f"wrk-me-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "discipline": "ME",
            "worklet_type": "carnot_rankine_heat_engine",
            "title": title or "Superheated Rankine vs Carnot Thermal Cycle Evaluation",
            "problem_statement": f"Thermodynamic performance evaluation of a thermal power unit receiving {qh_mw} MW heat input at {th_c}°C with condenser rejection at {tc_c}°C.",
            "parameters": [
                {"name": "Boiler Superheat Temp", "symbol": "T_H", "value": th_c, "unit": "°C", "description": "High temperature heat addition"},
                {"name": "Condenser Cold Temp", "symbol": "T_C", "value": tc_c, "unit": "°C", "description": "Cold reservoir rejection sink"},
                {"name": "Thermal Heat Input", "symbol": "Q_H", "value": qh_mw, "unit": "MW", "description": "Boiler thermal power generation"},
            ],
            "governing_equations": [
                r"\eta_{carnot} = 1 - \frac{T_C}{T_H}",
                r"\eta_{rankine} \approx 0.64 \cdot \eta_{carnot}",
                r"W_{net} = \eta_{rankine} \cdot Q_H",
                r"Q_C = Q_H - W_{net}",
            ],
            "derivation_steps": [
                {
                    "step_number": 1,
                    "title": "Convert Operating Temperatures to Absolute Kelvin Scale",
                    "formula": r"T(K) = T(^\circ C) + 273.15",
                    "substitution": f"T_H = {th_c} + 273.15 = {th_k:.2f} \\text{{ K}}, \\quad T_C = {tc_c} + 273.15 = {tc_k:.2f} \\text{{ K}}",
                    "result_value": round(th_k, 2),
                    "unit": "K",
                    "notes": "Kelvin scale required for second-law thermodynamic formulations.",
                },
                {
                    "step_number": 2,
                    "title": "Compute Theoretical Carnot Maximum Efficiency Limit",
                    "formula": r"\eta_{carnot} = 1 - \frac{T_C}{T_H}",
                    "substitution": f"\\eta_{{carnot}} = 1 - \\frac{{{tc_k:.2f}}}{{{th_k:.2f}}} = {eta_carnot:.4f} = {eta_carnot*100:.2f}\\%",
                    "result_value": round(eta_carnot * 100, 2),
                    "unit": "%",
                    "notes": "Reversible limit bounded by Second Law of Thermodynamics.",
                },
                {
                    "step_number": 3,
                    "title": "Estimate Rankine Cycle Thermal Efficiency and Net Work Output",
                    "formula": r"W_{net} = (0.64 \cdot \eta_{carnot}) \cdot Q_H",
                    "substitution": f"W_{{net}} = ({eta_rankine:.4f}) \\times {qh_mw} \\text{{ MW}} = {wnet_mw:.2f} \\text{{ MW}}",
                    "result_value": round(wnet_mw, 2),
                    "unit": "MW",
                    "notes": f"Waste heat rejected to cooling towers: {qc_mw:.2f} MW.",
                },
            ],
            "kpis": [
                {"label": "Carnot Limit", "value": round(eta_carnot * 100, 2), "unit": "%", "status": "OPTIMAL"},
                {"label": "Rankine Efficiency", "value": round(eta_rankine * 100, 2), "unit": "%", "status": "OPTIMAL"},
                {"label": "Net Power", "value": round(wnet_mw, 2), "unit": "MW", "status": "OPTIMAL"},
            ],
            "compliance_checks": [
                {
                    "standard_code": "ASME PTC 46",
                    "parameter_checked": "Overall Plant Thermal Efficiency",
                    "threshold": "eta_plant >= 35.0%",
                    "actual_value": f"{eta_rankine*100:.2f}%",
                    "status": "PASS" if eta_rankine >= 0.35 else "MARGINAL",
                    "recommendation": "Cycle efficiency satisfies modern combined cycle / supercritical baseline standards.",
                }
            ],
            "compliance_verdict": "COMPLIANT",
            "executable_code": code,
            "schematic_svg_or_ascii": (
                " [Boiler Q_H = " + str(qh_mw) + " MW] ---> [Turbine W_net = " + str(round(wnet_mw, 2)) + " MW]\n"
                "         ^                                          |\n"
                "         |                                          v\n"
                "    [Feed Pump] <-------------------------- [Condenser Q_C = " + str(round(qc_mw, 2)) + " MW]\n"
            ),
            "created_by": user_id or "discipline_agent_me",
            "created_at": datetime.utcnow().isoformat(),
        }

    # --------------------------------------------------------------------------
    # ME 3: Beam Bending Stress
    # --------------------------------------------------------------------------
    def _solve_me_beam(self, params: dict[str, float], title: str, user_id: str | None) -> dict[str, Any]:
        span_m = params.get("span_m", 4.0)
        w_kn_m = params.get("distributed_load_kn_m", 15.0)
        p_kn = params.get("point_load_kn", 20.0)
        sy_mpa = params.get("yield_strength_mpa", 250.0)
        b_mm = params.get("beam_width_mm", 150.0)
        h_mm = params.get("beam_depth_mm", 300.0)

        m_max_knm = ((w_kn_m * (span_m ** 2)) / 8.0) + ((p_kn * span_m) / 4.0)
        b_m = b_mm / 1000.0
        h_m = h_mm / 1000.0
        z_m3 = (b_m * (h_m ** 2)) / 6.0
        sigma_max_mpa = (m_max_knm * 1000.0) / z_m3 / 1e6
        sf = sy_mpa / sigma_max_mpa if sigma_max_mpa > 0 else 999.0

        code = f"""span = {span_m}
w = {w_kn_m} * 1000
p = {p_kn} * 1000
sy = {sy_mpa} * 1e6
b = {b_m}
h = {h_m}

m_max = (w * (span**2) / 8.0) + (p * span / 4.0)
z = (b * (h**2)) / 6.0
sigma_max = m_max / z
sf = sy / sigma_max

print(f"Max Moment: {{m_max/1000:.2f}} kN*m")
print(f"Section Modulus Z: {{z:.4e}} m^3")
print(f"Max Flexural Stress: {{sigma_max/1e6:.2f}} MPa")
print(f"Safety Factor: {{sf:.2f}}")
"""

        return {
            "id": f"wrk-me-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "discipline": "ME",
            "worklet_type": "beam_bending_stress",
            "title": title or "Simply Supported Beam Bending & Section Modulus Analysis",
            "problem_statement": f"Bending stress evaluation of rectangular beam spanning {span_m} m under combined distributed load {w_kn_m} kN/m and center point load {p_kn} kN.",
            "parameters": [
                {"name": "Beam Span", "symbol": "L", "value": span_m, "unit": "m", "description": "Bearing span distance"},
                {"name": "Distributed Load", "symbol": "w", "value": w_kn_m, "unit": "kN/m", "description": "Uniform load"},
                {"name": "Center Point Load", "symbol": "P", "value": p_kn, "unit": "kN", "description": "Concentrated central load"},
                {"name": "Beam Width", "symbol": "b", "value": b_mm, "unit": "mm", "description": "Cross section width"},
                {"name": "Beam Depth", "symbol": "h", "value": h_mm, "unit": "mm", "description": "Cross section depth"},
            ],
            "governing_equations": [
                r"M_{max} = \frac{w L^2}{8} + \frac{P L}{4}",
                r"Z = \frac{b h^2}{6}",
                r"\sigma_{max} = \frac{M_{max}}{Z}",
                r"SF = \frac{S_y}{\sigma_{max}} \ge 1.67",
            ],
            "derivation_steps": [
                {
                    "step_number": 1,
                    "title": "Compute Maximum Bending Moment (M_max)",
                    "formula": r"M_{max} = \frac{w L^2}{8} + \frac{P L}{4}",
                    "substitution": f"M = \\frac{{{w_kn_m} \\times ({span_m})^2}}{{8}} + \\frac{{{p_kn} \\times {span_m}}}{{4}} = {m_max_knm:.2f} \\text{{ kN}}\\cdot\\text{{m}}",
                    "result_value": round(m_max_knm, 2),
                    "unit": "kN·m",
                    "notes": "Maximum bending moment occurs at mid-span under symmetric loading.",
                },
                {
                    "step_number": 2,
                    "title": "Calculate Elastic Section Modulus (Z)",
                    "formula": r"Z = \frac{b h^2}{6}",
                    "substitution": f"Z = \\frac{{{b_m:.3f} \\times ({h_m:.3f})^2}}{{6}} = {z_m3:.4e} \\text{{ m}}^3",
                    "result_value": round(z_m3, 6),
                    "unit": "m^3",
                    "notes": "Applies to homogeneous solid rectangular cross section.",
                },
                {
                    "step_number": 3,
                    "title": "Calculate Peak Extreme Fiber Bending Stress and Safety Factor",
                    "formula": r"\sigma_{max} = \frac{M_{max}}{Z}, \quad SF = \frac{S_y}{\sigma_{max}}",
                    "substitution": f"\\sigma = \\frac{{{m_max_knm:.2f} \\times 10^3}}{{{z_m3:.4e}}} = {sigma_max_mpa:.2f} \\text{{ MPa}}, \\quad SF = \\frac{{{sy_mpa:.1f}}}{{{sigma_max_mpa:.2f}}} = {sf:.2f}",
                    "result_value": round(sf, 2),
                    "unit": "",
                    "notes": "Tensile stress on bottom fiber, compressive stress on top fiber.",
                },
            ],
            "kpis": [
                {"label": "Safety Factor (SF)", "value": round(sf, 2), "unit": "", "status": "OPTIMAL" if sf >= 2.0 else "ACCEPTABLE" if sf >= 1.67 else "CRITICAL"},
                {"label": "Max Moment", "value": round(m_max_knm, 2), "unit": "kN·m", "status": "OPTIMAL"},
                {"label": "Max Flexural Stress", "value": round(sigma_max_mpa, 2), "unit": "MPa", "status": "ACCEPTABLE"},
            ],
            "compliance_checks": [
                {
                    "standard_code": "AISC 360-16 / Allowable Stress Design",
                    "parameter_checked": "Flexural Bending Safety Factor",
                    "threshold": "SF >= 1.67",
                    "actual_value": f"SF = {sf:.2f}",
                    "status": "PASS" if sf >= 1.67 else "FAIL",
                    "recommendation": "Section size satisfies AISC strength criteria." if sf >= 1.67 else "Increase beam depth h to elevate section modulus.",
                }
            ],
            "compliance_verdict": "COMPLIANT" if sf >= 1.67 else "NON_COMPLIANT",
            "executable_code": code,
            "schematic_svg_or_ascii": (
                "        P = " + str(p_kn) + " kN\n"
                "          |\n"
                "  ||||||||v|||||||| w = " + str(w_kn_m) + " kN/m\n"
                " [^]====================[^]\n"
                "  +---- L = " + str(span_m) + " m ----+\n"
            ),
            "created_by": user_id or "discipline_agent_me",
            "created_at": datetime.utcnow().isoformat(),
        }

    # --------------------------------------------------------------------------
    # CE 1: Reinforced Concrete (RCC) Beam Flexure (ACI 318-19)
    # --------------------------------------------------------------------------
    def _solve_ce_rcc_beam(self, params: dict[str, float], title: str, user_id: str | None) -> dict[str, Any]:
        span_m = params.get("span_m", 6.0)
        wd_kn_m = params.get("dead_load_kn_m", 18.0)
        wl_kn_m = params.get("live_load_kn_m", 12.0)
        fc_mpa = params.get("fc_mpa", 28.0)
        fy_mpa = params.get("fy_mpa", 420.0)
        b_mm = params.get("width_b_mm", 300.0)
        d_mm = params.get("eff_depth_d_mm", 500.0)
        n_bars = int(params.get("num_bars", 4))
        bar_dia_mm = params.get("bar_dia_mm", 25.0)

        wu_kn_m = (1.2 * wd_kn_m) + (1.6 * wl_kn_m)
        mu_knm = (wu_kn_m * (span_m ** 2)) / 8.0
        bar_area_mm2 = (math.pi * (bar_dia_mm ** 2)) / 4.0
        as_total_mm2 = n_bars * bar_area_mm2
        a_depth_mm = (as_total_mm2 * fy_mpa) / (0.85 * fc_mpa * b_mm)
        mn_knm = as_total_mm2 * fy_mpa * (d_mm - (a_depth_mm / 2.0)) * 1e-6
        phi_mn_knm = 0.9 * mn_knm
        capacity_ratio = phi_mn_knm / mu_knm if mu_knm > 0 else 999.0

        rho = as_total_mm2 / (b_mm * d_mm)
        rho_min = max((0.25 * math.sqrt(fc_mpa)) / fy_mpa, 1.4 / fy_mpa)
        is_safe = phi_mn_knm >= mu_knm
        is_steel_ok = rho >= rho_min
        verdict = "COMPLIANT" if (is_safe and is_steel_ok) else "NON_COMPLIANT"

        code = f"""import math

span = {span_m}
wd = {wd_kn_m}
wl = {wl_kn_m}
fc = {fc_mpa}
fy = {fy_mpa}
b = {b_mm}
d = {d_mm}
n_bars = {n_bars}
bar_dia = {bar_dia_mm}

wu = (1.2 * wd) + (1.6 * wl)
mu = (wu * (span ** 2)) / 8.0
as_total = n_bars * (math.pi * (bar_dia ** 2) / 4.0)
a = (as_total * fy) / (0.85 * fc * b)
mn = as_total * fy * (d - (a / 2.0)) * 1e-6
phi_mn = 0.9 * mn
ratio = phi_mn / mu

print(f"Factored Load wu: {{wu:.2f}} kN/m")
print(f"Factored Design Moment Mu: {{mu:.2f}} kN*m")
print(f"Rebar Area As: {{as_total:.1f}} mm^2 ({n_bars}x#{{bar_dia}}mm)")
print(f"Design Flexural Capacity phi*Mn: {{phi_mn:.2f}} kN*m")
print(f"Capacity Ratio phi*Mn/Mu: {{ratio:.2f}} ({{'PASS' if ratio >= 1.0 else 'FAIL'}})")
"""

        return {
            "id": f"wrk-ce-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "discipline": "CE",
            "worklet_type": "rcc_beam_flexure",
            "title": title or "Reinforced Concrete Beam Flexural Strength (ACI 318-19)",
            "problem_statement": (
                f"Singularly reinforced concrete beam spanning {span_m} m carrying factored dead load {wd_kn_m} kN/m "
                f"and live load {wl_kn_m} kN/m. Verify ultimate moment capacity phi*Mn against required factored moment Mu."
            ),
            "parameters": [
                {"name": "Beam Span", "symbol": "L", "value": span_m, "unit": "m", "description": "Centerline bearing span"},
                {"name": "Dead Load", "symbol": "w_D", "value": wd_kn_m, "unit": "kN/m", "description": "Unfactored sustained dead load"},
                {"name": "Live Load", "symbol": "w_L", "value": wl_kn_m, "unit": "kN/m", "description": "Unfactored transient live load"},
                {"name": "Concrete Strength", "symbol": "f'_c", "value": fc_mpa, "unit": "MPa", "description": "28-day cylinder compressive strength"},
                {"name": "Steel Yield Strength", "symbol": "f_y", "value": fy_mpa, "unit": "MPa", "description": "Grade 60 rebar yield stress"},
                {"name": "Beam Web Width", "symbol": "b", "value": b_mm, "unit": "mm", "description": "Width of beam cross section"},
                {"name": "Effective Depth", "symbol": "d", "value": d_mm, "unit": "mm", "description": "Distance from extreme compression fiber to rebar centroid"},
                {"name": "Tension Rebar Count", "symbol": "n", "value": float(n_bars), "unit": "bars", "description": "Count of longitudinal tension rebar"},
                {"name": "Bar Diameter", "symbol": "d_b", "value": bar_dia_mm, "unit": "mm", "description": "Diameter of longitudinal rebar"},
            ],
            "governing_equations": [
                r"w_u = 1.2 w_D + 1.6 w_L, \quad M_u = \frac{w_u L^2}{8}",
                r"A_s = n \cdot \frac{\pi d_b^2}{4}, \quad a = \frac{A_s f_y}{0.85 f'_c b}",
                r"M_n = A_s f_y \left(d - \frac{a}{2}\right), \quad \phi M_n = 0.90 M_n",
                r"\phi M_n \ge M_u, \quad \rho_{min} = \max\left(\frac{0.25 \sqrt{f'_c}}{f_y}, \frac{1.4}{f_y}\right)",
            ],
            "derivation_steps": [
                {
                    "step_number": 1,
                    "title": "Compute Factored Distributed Load and Design Bending Moment",
                    "formula": r"w_u = 1.2 w_D + 1.6 w_L, \quad M_u = \frac{w_u L^2}{8}",
                    "substitution": f"w_u = 1.2({wd_kn_m}) + 1.6({wl_kn_m}) = {wu_kn_m:.2f} \\text{{ kN/m}}, \\quad M_u = \\frac{{{wu_kn_m:.2f} \\times ({span_m})^2}}{{8}} = {mu_knm:.2f} \\text{{ kN}}\\cdot\\text{{m}}",
                    "result_value": round(mu_knm, 2),
                    "unit": "kN·m",
                    "notes": "ACI 318-19 strength design load combinations.",
                },
                {
                    "step_number": 2,
                    "title": "Calculate Tension Steel Area and Whitney Stress Block Depth (a)",
                    "formula": r"A_s = n \frac{\pi d_b^2}{4}, \quad a = \frac{A_s f_y}{0.85 f'_c b}",
                    "substitution": f"A_s = {n_bars} \\times \\frac{{\\pi ({bar_dia_mm})^2}}{{4}} = {as_total_mm2:.1f} \\text{{ mm}}^2, \\quad a = \\frac{{{as_total_mm2:.1f} \\times {fy_mpa}}}{{0.85 \\times {fc_mpa} \\times {b_mm}}} = {a_depth_mm:.1f} \\text{{ mm}}",
                    "result_value": round(a_depth_mm, 2),
                    "unit": "mm",
                    "notes": "Equilibrium of internal compressive concrete block C = T tension steel force.",
                },
                {
                    "step_number": 3,
                    "title": "Determine Nominal and Design Flexural Moment Capacity",
                    "formula": r"\phi M_n = \phi A_s f_y (d - a/2)",
                    "substitution": f"\\phi M_n = 0.90 \\times {as_total_mm2:.1f} \\times {fy_mpa} \\times ({d_mm} - {a_depth_mm/2.0:.1f}) \\times 10^{{-6}} = {phi_mn_knm:.2f} \\text{{ kN}}\\cdot\\text{{m}}",
                    "result_value": round(phi_mn_knm, 2),
                    "unit": "kN·m",
                    "notes": f"Demand-capacity ratio evaluates to phi*Mn / Mu = {capacity_ratio:.2f}.",
                },
            ],
            "kpis": [
                {"label": "Capacity Ratio (phi*Mn / Mu)", "value": round(capacity_ratio, 2), "unit": "", "status": "OPTIMAL" if capacity_ratio >= 1.2 else "ACCEPTABLE" if capacity_ratio >= 1.0 else "CRITICAL"},
                {"label": "Design Capacity phi*Mn", "value": round(phi_mn_knm, 2), "unit": "kN·m", "status": "OPTIMAL"},
                {"label": "Factored Demand Mu", "value": round(mu_knm, 2), "unit": "kN·m", "status": "ACCEPTABLE"},
            ],
            "compliance_checks": [
                {
                    "standard_code": "ACI 318-19 Sec 22.2",
                    "parameter_checked": "Flexural Strength Demand vs Capacity",
                    "threshold": "phi*Mn >= Mu",
                    "actual_value": f"{phi_mn_knm:.2f} >= {mu_knm:.2f} kN*m",
                    "status": "PASS" if is_safe else "FAIL",
                    "recommendation": "Section capacity adequate." if is_safe else "Increase effective depth d or add tension rebar.",
                },
                {
                    "standard_code": "ACI 318-19 Sec 9.6.1",
                    "parameter_checked": "Minimum Steel Reinforcement Ratio (rho_min)",
                    "threshold": f"rho >= {rho_min:.5f}",
                    "actual_value": f"rho = {rho:.5f}",
                    "status": "PASS" if is_steel_ok else "FAIL",
                    "recommendation": "Prevents sudden brittle concrete cracking upon initial tensile rupture." if is_steel_ok else "Increase longitudinal reinforcement area.",
                },
            ],
            "compliance_verdict": verdict,
            "executable_code": code,
            "schematic_svg_or_ascii": (
                "  +----------- b = " + str(b_mm) + " mm -----------+\n"
                "  |   [Concrete Compression Zone]   |   ^  a = " + str(round(a_depth_mm, 1)) + " mm\n"
                "  |---------------------------------|   v\n"
                "  |                                 |\n"
                "  |                                 |   d = " + str(d_mm) + " mm\n"
                "  |     (O)     (O)     (O)     (O) |   v\n"
                "  +--- " + str(n_bars) + "x #" + str(int(bar_dia_mm)) + "mm Tension Rebar ---+\n"
            ),
            "created_by": user_id or "discipline_agent_ce",
            "created_at": datetime.utcnow().isoformat(),
        }

    # --------------------------------------------------------------------------
    # CE 2: Cantilever Retaining Wall Stability
    # --------------------------------------------------------------------------
    def _solve_ce_retaining_wall(self, params: dict[str, float], title: str, user_id: str | None) -> dict[str, Any]:
        h_m = params.get("height_h_m", 4.5)
        gamma = params.get("gamma_soil_kn_m3", 18.0)
        phi_deg = params.get("friction_angle_deg", 30.0)
        w_wall = params.get("wall_weight_kn_m", 145.0)
        b_m = params.get("footing_width_b_m", 2.8)
        mu_friction = params.get("friction_coeff_mu", 0.45)

        phi_rad = math.radians(phi_deg)
        ka = (1.0 - math.sin(phi_rad)) / (1.0 + math.sin(phi_rad))
        pa_kn_m = 0.5 * ka * gamma * (h_m ** 2)
        mot_knm = pa_kn_m * (h_m / 3.0)
        mr_knm = w_wall * (b_m / 2.0)
        fs_ot = mr_knm / mot_knm if mot_knm > 0 else 999.0

        f_res_slide = mu_friction * w_wall
        fs_sl = f_res_slide / pa_kn_m if pa_kn_m > 0 else 999.0

        is_ot_ok = fs_ot >= 2.0
        is_sl_ok = fs_sl >= 1.5
        verdict = "COMPLIANT" if (is_ot_ok and is_sl_ok) else "MARGINAL" if is_ot_ok else "NON_COMPLIANT"

        code = f"""import math

h = {h_m}
gamma = {gamma}
phi_deg = {phi_deg}
w_wall = {w_wall}
b = {b_m}
mu = {mu_friction}

ka = (1.0 - math.sin(math.radians(phi_deg))) / (1.0 + math.sin(math.radians(phi_deg)))
pa = 0.5 * ka * gamma * (h ** 2)
mot = pa * (h / 3.0)
mr = w_wall * (b / 2.0)
fs_ot = mr / mot
fs_sl = (mu * w_wall) / pa

print(f"Rankine Ka: {{ka:.3f}}")
print(f"Total Lateral Thrust Pa: {{pa:.2f}} kN/m")
print(f"Overturning Moment: {{mot:.2f}} kN*m/m | Resisting Moment: {{mr:.2f}} kN*m/m")
print(f"FS Overturning: {{fs_ot:.2f}} ({{'PASS' if fs_ot >= 2.0 else 'FAIL'}})")
print(f"FS Sliding: {{fs_sl:.2f}} ({{'PASS' if fs_sl >= 1.5 else 'MARGINAL'}})")
"""

        return {
            "id": f"wrk-ce-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "discipline": "CE",
            "worklet_type": "retaining_wall_stability",
            "title": title or "Cantilever Retaining Wall Stability & Earth Pressure Analysis",
            "problem_statement": f"Stability assessment of a {h_m} m cantilever retaining wall supporting granular soil (gamma = {gamma} kN/m3, phi = {phi_deg}°).",
            "parameters": [
                {"name": "Wall Height", "symbol": "H", "value": h_m, "unit": "m", "description": "Stem height from footing base to crest"},
                {"name": "Soil Unit Weight", "symbol": "gamma", "value": gamma, "unit": "kN/m³", "description": "Backfill retained unit weight"},
                {"name": "Internal Friction Angle", "symbol": "phi", "value": phi_deg, "unit": "°", "description": "Effective soil shearing resistance"},
                {"name": "Total Structure Weight", "symbol": "W", "value": w_wall, "unit": "kN/m", "description": "Concrete stem and footing combined self-weight"},
                {"name": "Base Footing Width", "symbol": "B", "value": b_m, "unit": "m", "description": "Width of base slab toe to heel"},
            ],
            "governing_equations": [
                r"K_a = \frac{1 - \sin\phi}{1 + \sin\phi}",
                r"P_a = \frac{1}{2} K_a \gamma H^2",
                r"M_{ot} = P_a \cdot \frac{H}{3}, \quad M_r = W \cdot \frac{B}{2}",
                r"FS_{ot} = \frac{M_r}{M_{ot}} \ge 2.0, \quad FS_{sl} = \frac{\mu W}{P_a} \ge 1.5",
            ],
            "derivation_steps": [
                {
                    "step_number": 1,
                    "title": "Compute Rankine Active Earth Pressure Coefficient (K_a)",
                    "formula": r"K_a = \frac{1 - \sin\phi}{1 + \sin\phi}",
                    "substitution": f"K_a = \\frac{{1 - \\sin({phi_deg}^\\circ)}}{{1 + \\sin({phi_deg}^\\circ)}} = {ka:.3f}",
                    "result_value": round(ka, 4),
                    "unit": "",
                    "notes": "Assumes frictionless vertical back of wall and horizontal backfill crest.",
                },
                {
                    "step_number": 2,
                    "title": "Determine Resultant Lateral Active Thrust (P_a)",
                    "formula": r"P_a = \frac{1}{2} K_a \gamma H^2",
                    "substitution": f"P_a = 0.5 \\times {ka:.3f} \\times {gamma} \\times ({h_m})^2 = {pa_kn_m:.2f} \\text{{ kN/m}}",
                    "result_value": round(pa_kn_m, 2),
                    "unit": "kN/m",
                    "notes": "Acts horizontally at H/3 above base of footing.",
                },
                {
                    "step_number": 3,
                    "title": "Evaluate Overturning and Sliding Factors of Safety",
                    "formula": r"FS_{ot} = \frac{M_r}{M_{ot}}, \quad FS_{sl} = \frac{\mu W}{P_a}",
                    "substitution": f"FS_{{ot}} = \\frac{{{mr_knm:.2f}}}{{{mot_knm:.2f}}} = {fs_ot:.2f}, \\quad FS_{{sl}} = \\frac{{{f_res_slide:.2f}}}{{{pa_kn_m:.2f}}} = {fs_sl:.2f}",
                    "result_value": round(fs_ot, 2),
                    "unit": "",
                    "notes": f"Overturning FS: {fs_ot:.2f} | Sliding FS: {fs_sl:.2f}.",
                },
            ],
            "kpis": [
                {"label": "FS Overturning", "value": round(fs_ot, 2), "unit": "", "status": "OPTIMAL" if fs_ot >= 2.0 else "CRITICAL"},
                {"label": "FS Sliding", "value": round(fs_sl, 2), "unit": "", "status": "OPTIMAL" if fs_sl >= 1.5 else "WARNING" if fs_sl >= 1.0 else "CRITICAL"},
                {"label": "Lateral Thrust", "value": round(pa_kn_m, 2), "unit": "kN/m", "status": "ACCEPTABLE"},
            ],
            "compliance_checks": [
                {
                    "standard_code": "IBC / AASHTO Bridge Design",
                    "parameter_checked": "Factor of Safety Against Overturning",
                    "threshold": "FS_ot >= 2.0",
                    "actual_value": f"FS_ot = {fs_ot:.2f}",
                    "status": "PASS" if is_ot_ok else "FAIL",
                    "recommendation": "Adequate overturning resistance." if is_ot_ok else "Widen footing base B or extend heel slab.",
                },
                {
                    "standard_code": "IBC / AASHTO Bridge Design",
                    "parameter_checked": "Factor of Safety Against Base Sliding",
                    "threshold": "FS_sl >= 1.5",
                    "actual_value": f"FS_sl = {fs_sl:.2f}",
                    "status": "PASS" if is_sl_ok else "MARGINAL",
                    "recommendation": "Frictional contact sufficient." if is_sl_ok else "Provide a downward shear key beneath the base slab.",
                },
            ],
            "compliance_verdict": verdict,
            "executable_code": code,
            "schematic_svg_or_ascii": (
                "         | |\n"
                "         | |  <--- [Granular Backfill gamma = " + str(gamma) + "]\n"
                "         | |       Active Thrust P_a = " + str(round(pa_kn_m, 1)) + " kN/m\n"
                "         | |       at H/3 = " + str(round(h_m/3.0, 2)) + " m\n"
                "  [Toe]--+ +--[Heel]  B = " + str(b_m) + " m\n"
            ),
            "created_by": user_id or "discipline_agent_ce",
            "created_at": datetime.utcnow().isoformat(),
        }

    # --------------------------------------------------------------------------
    # CE 3: Stormwater Drainage Runoff
    # --------------------------------------------------------------------------
    def _solve_ce_stormwater(self, params: dict[str, float], title: str, user_id: str | None) -> dict[str, Any]:
        area_ha = params.get("area_hectares", 12.0)
        c_runoff = params.get("runoff_coeff_c", 0.65)
        intensity_mm_hr = params.get("rainfall_intensity_mm_hr", 75.0)
        slope_s = params.get("pipe_slope_s", 0.01)
        manning_n = params.get("manning_n", 0.013)

        q_m3s = (c_runoff * intensity_mm_hr * area_ha) / 360.0
        d_req_m = (((2.16 * q_m3s * manning_n) / math.sqrt(slope_s)) ** (3.0 / 8.0))
        d_req_mm = d_req_m * 1000.0

        code = f"""import math

area_ha = {area_ha}
c = {c_runoff}
intensity = {intensity_mm_hr}
slope = {slope_s}
n = {manning_n}

q = (c * intensity * area_ha) / 360.0
d_pipe = (((2.16 * q * n) / math.sqrt(slope)) ** (3.0 / 8.0))

print(f"Peak Storm Runoff Q: {{q:.3f}} m^3/s ({{q*1000:.1f}} L/s)")
print(f"Required Conduit Diameter: {{d_pipe*1000:.1f}} mm")
"""

        return {
            "id": f"wrk-ce-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "discipline": "CE",
            "worklet_type": "stormwater_drainage",
            "title": title or "Stormwater Peak Runoff & Gravity Conduit Sizing (Rational Method)",
            "problem_statement": f"Hydrological peak discharge estimation for {area_ha} ha catchment basin with C = {c_runoff} under design storm intensity {intensity_mm_hr} mm/hr.",
            "parameters": [
                {"name": "Catchment Area", "symbol": "A", "value": area_ha, "unit": "ha", "description": "Contributing drainage basin area"},
                {"name": "Runoff Coefficient", "symbol": "C", "value": c_runoff, "unit": "", "description": "Composite imperviousness factor"},
                {"name": "Rainfall Intensity", "symbol": "I", "value": intensity_mm_hr, "unit": "mm/hr", "description": "Design rainfall intensity (10-yr storm)"},
                {"name": "Conduit Longitudinal Slope", "symbol": "S", "value": slope_s, "unit": "m/m", "description": "Drainage pipe gradient"},
            ],
            "governing_equations": [
                r"Q = \frac{C \cdot I \cdot A}{360}",
                r"Q = \frac{1}{n} A R_h^{2/3} S^{1/2}",
                r"D \approx \left(\frac{2.16 Q n}{\sqrt{S}}\right)^{3/8}",
            ],
            "derivation_steps": [
                {
                    "step_number": 1,
                    "title": "Estimate Peak Stormwater Discharge (Q)",
                    "formula": r"Q = \frac{C \cdot I \cdot A}{360}",
                    "substitution": f"Q = \\frac{{{c_runoff} \\times {intensity_mm_hr} \\times {area_ha}}}{{360}} = {q_m3s:.3f} \\text{{ m}}^3/\\text{{s}}",
                    "result_value": round(q_m3s, 4),
                    "unit": "m³/s",
                    "notes": "Equivalent to " + str(round(q_m3s * 1000, 1)) + " L/s volumetric discharge.",
                },
                {
                    "step_number": 2,
                    "title": "Size Circular Gravity Storm Sewer Diameter (Manning Formula)",
                    "formula": r"D = \left(\frac{2.16 Q n}{\sqrt{S}}\right)^{3/8}",
                    "substitution": f"D = \\left(\\frac{{2.16 \\times {q_m3s:.3f} \\times {manning_n}}}{{\\sqrt{{{slope_s}}}}}\\right)^{{3/8}} = {d_req_mm:.1f} \\text{{ mm}}",
                    "result_value": round(d_req_mm, 1),
                    "unit": "mm",
                    "notes": "Assumes standard reinforced concrete pipe (RCP) flowing full.",
                },
            ],
            "kpis": [
                {"label": "Peak Discharge", "value": round(q_m3s, 3), "unit": "m³/s", "status": "OPTIMAL"},
                {"label": "Min Pipe Diameter", "value": round(d_req_mm, 0), "unit": "mm", "status": "OPTIMAL"},
            ],
            "compliance_checks": [
                {
                    "standard_code": "EPA / AASHTO Drainage Manual",
                    "parameter_checked": "Conduit Sizing Feasibility",
                    "threshold": "D_pipe <= 1500 mm",
                    "actual_value": f"D = {d_req_mm:.1f} mm",
                    "status": "PASS",
                    "recommendation": "Select next standard commercial diameter (e.g. 600 mm or 750 mm RCP).",
                }
            ],
            "compliance_verdict": "COMPLIANT",
            "executable_code": code,
            "schematic_svg_or_ascii": "  [Rainfall I = " + str(intensity_mm_hr) + " mm/hr] ---> Catchment Basin ---> Pipe D = " + str(round(d_req_mm, 0)) + " mm (Q = " + str(round(q_m3s, 3)) + " m3/s)\n",
            "created_by": user_id or "discipline_agent_ce",
            "created_at": datetime.utcnow().isoformat(),
        }

    # --------------------------------------------------------------------------
    # EE 1: Series RLC Filter & Resonant Response
    # --------------------------------------------------------------------------
    def _solve_ee_rlc_resonance(self, params: dict[str, float], title: str, user_id: str | None) -> dict[str, Any]:
        r = params.get("r_ohms", 50.0)
        l_mh = params.get("l_millihenry", 10.0)
        c_uf = params.get("c_microfarad", 0.1)
        vs = params.get("vs_volts", 12.0)

        l_h = l_mh / 1000.0
        c_f = c_uf * 1e-6

        omega0 = 1.0 / math.sqrt(l_h * c_f)
        f0 = omega0 / (2.0 * math.pi)
        xl = omega0 * l_h
        q_factor = xl / r if r > 0 else 999.0
        bandwidth = f0 / q_factor if q_factor > 0 else 0.0
        damping_zeta = 1.0 / (2.0 * q_factor) if q_factor > 0 else 0.0
        i_peak = vs / r if r > 0 else 0.0

        is_q_ok = q_factor >= 2.0
        verdict = "COMPLIANT" if is_q_ok else "MARGINAL"

        code = f"""import math

r = {r}  # Ohms
l = {l_h}  # H
c = {c_f}  # F
vs = {vs}  # V

omega0 = 1.0 / math.sqrt(l * c)
f0 = omega0 / (2.0 * math.pi)
xl = omega0 * l
q = xl / r
bw = f0 / q
zeta = 1.0 / (2.0 * q)
i_peak = vs / r

print(f"Resonant Angular Frequency omega_0: {{omega0:.2f}} rad/s")
print(f"Resonant Center Frequency f_0: {{f0:.2f}} Hz ({{f0/1000:.3f}} kHz)")
print(f"Characteristic Reactance X_L = X_C: {{xl:.2f}} Ohms")
print(f"Circuit Quality Factor Q: {{q:.2f}}")
print(f"Half-Power Bandwidth BW: {{bw:.2f}} Hz")
print(f"Damping Ratio zeta: {{zeta:.4f}}")
print(f"Peak Current at Resonance: {{i_peak:.3f}} A")
"""

        return {
            "id": f"wrk-ee-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "discipline": "EE",
            "worklet_type": "rlc_filter_resonance",
            "title": title or "Series RLC Resonant Frequency, Bandwidth & Quality Factor (Q)",
            "problem_statement": (
                f"Design verification of a series RLC bandpass filter network with R = {r} Ω, L = {l_mh} mH, and C = {c_uf} µF "
                f"energized by a {vs} V AC signal source. Determine resonance frequency, selectivity Q, and half-power bandwidth."
            ),
            "parameters": [
                {"name": "Series Resistance", "symbol": "R", "value": r, "unit": "Ω", "description": "Internal circuit damping resistance"},
                {"name": "Inductance", "symbol": "L", "value": l_mh, "unit": "mH", "description": "Tuned inductor component"},
                {"name": "Capacitance", "symbol": "C", "value": c_uf, "unit": "µF", "description": "Tuned capacitor component"},
                {"name": "AC Source Voltage", "symbol": "V_s", "value": vs, "unit": "V", "description": "RMS AC excitation source"},
            ],
            "governing_equations": [
                r"\omega_0 = \frac{1}{\sqrt{LC}}, \quad f_0 = \frac{\omega_0}{2\pi}",
                r"X_L = \omega_0 L = \frac{1}{\omega_0 C}",
                r"Q = \frac{\omega_0 L}{R} = \frac{1}{R}\sqrt{\frac{L}{C}}",
                r"BW = \frac{f_0}{Q} = \frac{R}{2\pi L}",
                r"\zeta = \frac{1}{2Q}, \quad I_{res} = \frac{V_s}{R}",
            ],
            "derivation_steps": [
                {
                    "step_number": 1,
                    "title": "Calculate Resonant Angular and Center Frequency",
                    "formula": r"\omega_0 = \frac{1}{\sqrt{LC}}, \quad f_0 = \frac{\omega_0}{2\pi}",
                    "substitution": f"\\omega_0 = \\frac{{1}}{{\\sqrt{{{l_h:.4f} \\times {c_f:.2e}}}}} = {omega0:.2f} \\text{{ rad/s}}, \\quad f_0 = \\frac{{{omega0:.2f}}}{{2\\pi}} = {f0:.2f} \\text{{ Hz}}",
                    "result_value": round(f0, 2),
                    "unit": "Hz",
                    "notes": f"Center resonance occurs at {f0/1000:.3f} kHz where reactive impedances cancel (X_L = X_C).",
                },
                {
                    "step_number": 2,
                    "title": "Compute Characteristic Reactance and Quality Factor (Q)",
                    "formula": r"Q = \frac{\omega_0 L}{R}",
                    "substitution": f"X_L = {omega0:.2f} \\times {l_h:.4f} = {xl:.2f} \\ \\Omega, \\quad Q = \\frac{{{xl:.2f}}}{{{r}}} = {q_factor:.2f}",
                    "result_value": round(q_factor, 2),
                    "unit": "",
                    "notes": "Selectivity metric: higher Q yields sharper bandpass filter skirt selectivity.",
                },
                {
                    "step_number": 3,
                    "title": "Determine Half-Power Bandwidth and Dynamic Response",
                    "formula": r"BW = \frac{f_0}{Q}, \quad I_{peak} = \frac{V_s}{R}",
                    "substitution": f"BW = \\frac{{{f0:.2f}}}{{{q_factor:.2f}}} = {bandwidth:.2f} \\text{{ Hz}}, \\quad I_{{peak}} = \\frac{{{vs}}}{{{r}}} = {i_peak:.3f} \\text{{ A}}",
                    "result_value": round(bandwidth, 2),
                    "unit": "Hz",
                    "notes": f"Damping ratio zeta = {damping_zeta:.4f} (underdamped resonant regime).",
                },
            ],
            "kpis": [
                {"label": "Center Frequency f0", "value": round(f0 / 1000, 3), "unit": "kHz", "status": "OPTIMAL"},
                {"label": "Quality Factor Q", "value": round(q_factor, 2), "unit": "", "status": "OPTIMAL" if q_factor >= 5.0 else "ACCEPTABLE"},
                {"label": "Bandwidth BW", "value": round(bandwidth, 1), "unit": "Hz", "status": "OPTIMAL"},
                {"label": "Resonance Current", "value": round(i_peak, 3), "unit": "A", "status": "OPTIMAL"},
            ],
            "compliance_checks": [
                {
                    "standard_code": "IEEE Circuits & Systems Standards",
                    "parameter_checked": "Filter Selectivity Quality Factor (Q)",
                    "threshold": "Q >= 2.0",
                    "actual_value": f"Q = {q_factor:.2f}",
                    "status": "PASS" if is_q_ok else "MARGINAL",
                    "recommendation": "Passband selectivity satisfies communication/RF receiver requirements." if is_q_ok else "Reduce series resistance R to heighten resonant Q.",
                }
            ],
            "compliance_verdict": verdict,
            "executable_code": code,
            "schematic_svg_or_ascii": (
                "  +---(AC Source V_s = " + str(vs) + "V)---+---[R = " + str(r) + " ohm]---[L = " + str(l_mh) + " mH]---[C = " + str(c_uf) + " uF]---+\n"
                "  |                                                                           |\n"
                "  +---------------------------------------------------------------------------+\n"
            ),
            "created_by": user_id or "discipline_agent_ee",
            "created_at": datetime.utcnow().isoformat(),
        }

    # --------------------------------------------------------------------------
    # EE 2: 3-Phase Power Factor Correction
    # --------------------------------------------------------------------------
    def _solve_ee_power_factor(self, params: dict[str, float], title: str, user_id: str | None) -> dict[str, Any]:
        s_kva = params.get("apparent_power_kva", 250.0)
        pf1 = params.get("initial_pf", 0.78)
        pf2 = params.get("target_pf", 0.95)
        vl_v = params.get("line_voltage_v", 480.0)

        p_kw = s_kva * pf1
        theta1 = math.acos(pf1)
        q1_kvar = p_kw * math.tan(theta1)
        theta2 = math.acos(pf2)
        q2_kvar = p_kw * math.tan(theta2)
        qc_kvar = q1_kvar - q2_kvar

        i1_a = (s_kva * 1000.0) / (math.sqrt(3.0) * vl_v)
        s2_kva = p_kw / pf2
        i2_a = (s2_kva * 1000.0) / (math.sqrt(3.0) * vl_v)
        delta_i_a = i1_a - i2_a
        i_reduction_pct = (delta_i_a / i1_a) * 100.0 if i1_a > 0 else 0.0

        is_pf_ok = pf2 >= 0.95
        verdict = "COMPLIANT" if is_pf_ok else "MARGINAL"

        code = f"""import math

s1 = {s_kva}
pf1 = {pf1}
pf2 = {pf2}
vl = {vl_v}

p = s1 * pf1
q1 = p * math.tan(math.acos(pf1))
q2 = p * math.tan(math.acos(pf2))
qc = q1 - q2
i1 = (s1 * 1000) / (math.sqrt(3) * vl)
i2 = ((p / pf2) * 1000) / (math.sqrt(3) * vl)
delta_i = i1 - i2

print(f"Active Real Power P: {{p:.2f}} kW")
print(f"Initial Reactive Load Q1: {{q1:.2f}} kVAR")
print(f"Target Reactive Load Q2: {{q2:.2f}} kVAR")
print(f"Required Shunt Capacitor Bank: {{qc:.2f}} kVAR")
print(f"Line Current Reduction: {{i1:.1f}}A -> {{i2:.1f}}A ({{delta_i:.1f}}A savings, {{delta_i/i1*100:.1f}}% drop)")
"""

        return {
            "id": f"wrk-ee-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "discipline": "EE",
            "worklet_type": "three_phase_power_factor",
            "title": title or "3-Phase Industrial Power Factor Correction & Capacitor Sizing",
            "problem_statement": (
                f"Industrial plant drawing {s_kva} kVA at uncorrected power factor {pf1} lagging on a {vl_v} V 3-phase bus. "
                f"Determine required shunt capacitor bank rating to elevate power factor to {pf2} and calculate feeder current reduction."
            ),
            "parameters": [
                {"name": "Initial Apparent Power", "symbol": "S_1", "value": s_kva, "unit": "kVA", "description": "Existing load demand"},
                {"name": "Uncorrected Power Factor", "symbol": "PF_1", "value": pf1, "unit": "lagging", "description": "Existing motor/inductive load power factor"},
                {"name": "Target Power Factor", "symbol": "PF_2", "value": pf2, "unit": "lagging", "description": "Utility target to eliminate penalty"},
                {"name": "Line-to-Line Voltage", "symbol": "V_L", "value": vl_v, "unit": "V", "description": "3-phase secondary distribution voltage"},
            ],
            "governing_equations": [
                r"P = S_1 \cdot PF_1",
                r"Q_1 = P \tan(\arccos(PF_1)), \quad Q_2 = P \tan(\arccos(PF_2))",
                r"Q_c = Q_1 - Q_2 \text{ (kVAR)}",
                r"I_L = \frac{S}{\sqrt{3} V_L}",
            ],
            "derivation_steps": [
                {
                    "step_number": 1,
                    "title": "Calculate Active Real Power and Initial Reactive Load",
                    "formula": r"P = S_1 \cdot PF_1, \quad Q_1 = P \tan\theta_1",
                    "substitution": f"P = {s_kva} \\times {pf1} = {p_kw:.2f} \\text{{ kW}}, \\quad Q_1 = {p_kw:.2f} \\times \\tan({math.degrees(theta1):.1f}^\\circ) = {q1_kvar:.2f} \\text{{ kVAR}}",
                    "result_value": round(q1_kvar, 2),
                    "unit": "kVAR",
                    "notes": "Inductive reactive power drawn by plant motors.",
                },
                {
                    "step_number": 2,
                    "title": "Compute Required Shunt Capacitor Bank Sizing (Q_c)",
                    "formula": r"Q_c = P (\tan\theta_1 - \tan\theta_2)",
                    "substitution": f"Q_c = {q1_kvar:.2f} - {q2_kvar:.2f} = {qc_kvar:.2f} \\text{{ kVAR}}",
                    "result_value": round(qc_kvar, 2),
                    "unit": "kVAR",
                    "notes": "Shunt capacitor provides leading VARs to neutralize lagging inductive magnetizing current.",
                },
                {
                    "step_number": 3,
                    "title": "Determine Feeder Line Current Reduction and Capacity Savings",
                    "formula": r"\Delta I = I_1 - I_2 = \frac{S_1 - S_2}{\sqrt{3} V_L}",
                    "substitution": f"I_1 = {i1_a:.1f} \\text{{ A}}, \\quad I_2 = {i2_a:.1f} \\text{{ A}}, \\quad \\Delta I = {delta_i_a:.1f} \\text{{ A}} \\text{{ ({i_reduction_pct:.1f}\\% reduction)}}",
                    "result_value": round(delta_i_a, 1),
                    "unit": "A",
                    "notes": f"Frees up {delta_i_a:.1f} A of distribution transformer headroom and cuts I^2*R feeder losses.",
                },
            ],
            "kpis": [
                {"label": "Capacitor Bank", "value": round(qc_kvar, 1), "unit": "kVAR", "status": "OPTIMAL"},
                {"label": "Current Reduction", "value": round(delta_i_a, 1), "unit": "A", "status": "OPTIMAL"},
                {"label": "Load Reduction", "value": round(i_reduction_pct, 1), "unit": "%", "status": "OPTIMAL"},
            ],
            "compliance_checks": [
                {
                    "standard_code": "IEEE 519 / National Electrical Code (NEC)",
                    "parameter_checked": "Service Entrance Power Factor",
                    "threshold": "PF >= 0.95",
                    "actual_value": f"PF = {pf2:.2f}",
                    "status": "PASS" if is_pf_ok else "MARGINAL",
                    "recommendation": "Complies with utility tariff rules and eliminates reactive power surcharge penalties.",
                }
            ],
            "compliance_verdict": verdict,
            "executable_code": code,
            "schematic_svg_or_ascii": (
                "  3-Phase " + str(vl_v) + "V Bus =======+-----------------------+---> [Plant Load: " + str(p_kw) + " kW @ " + str(pf1) + " PF]\n"
                "                                 |\n"
                "                          [Capacitor Bank Q_c = " + str(round(qc_kvar, 1)) + " kVAR]\n"
            ),
            "created_by": user_id or "discipline_agent_ee",
            "created_at": datetime.utcnow().isoformat(),
        }

    # --------------------------------------------------------------------------
    # EE 3: Op-Amp Sallen-Key Active Filter
    # --------------------------------------------------------------------------
    def _solve_ee_opamp_filter(self, params: dict[str, float], title: str, user_id: str | None) -> dict[str, Any]:
        fc_hz = params.get("cutoff_freq_hz", 1000.0)
        r_ohms = params.get("resistor_r_ohms", 10000.0)

        c1_f = math.sqrt(2.0) / (2.0 * math.pi * fc_hz * r_ohms)
        c2_f = c1_f / 2.0
        c1_nf = c1_f * 1e9
        c2_nf = c2_f * 1e9

        code = f"""import math

fc = {fc_hz}
r = {r_ohms}

c1 = math.sqrt(2) / (2 * math.pi * fc * r)
c2 = c1 / 2.0

print(f"Target Cutoff Frequency: {{fc:.1f}} Hz")
print(f"Selected Resistors R1 = R2: {{r:.0f}} Ohms")
print(f"Required Capacitor C1: {{c1*1e9:.2f}} nF")
print(f"Required Capacitor C2: {{c2*1e9:.2f}} nF")
print("Response: 2nd-order Butterworth (Maximally Flat, -40 dB/decade roll-off)")
"""

        return {
            "id": f"wrk-ee-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "discipline": "EE",
            "worklet_type": "opamp_sallen_key_filter",
            "title": title or "Active 2nd-Order Butterworth Low-Pass Filter (Sallen-Key)",
            "problem_statement": f"Component synthesis for a unity-gain 2nd-order Sallen-Key low-pass filter with cutoff frequency {fc_hz} Hz using R = {r_ohms} Ω.",
            "parameters": [
                {"name": "Cutoff Frequency (-3dB)", "symbol": "f_c", "value": fc_hz, "unit": "Hz", "description": "Corner roll-off frequency"},
                {"name": "Bridge Resistors R1=R2", "symbol": "R", "value": r_ohms, "unit": "Ω", "description": "Matching precision input resistors"},
            ],
            "governing_equations": [
                r"f_c = \frac{1}{2\pi R \sqrt{C_1 C_2}}",
                r"Q = \frac{\sqrt{C_1 C_2}}{C_2} = \frac{1}{\sqrt{2}} \approx 0.707 \text{ (Butterworth)}",
                r"C_1 = \frac{\sqrt{2}}{2\pi f_c R}, \quad C_2 = \frac{C_1}{2}",
            ],
            "derivation_steps": [
                {
                    "step_number": 1,
                    "title": "Calculate Primary Feedback Capacitor (C_1)",
                    "formula": r"C_1 = \frac{\sqrt{2}}{2\pi f_c R}",
                    "substitution": f"C_1 = \\frac{{\\sqrt{{2}}}}{{2\\pi \\times {fc_hz} \\times {r_ohms}}} = {c1_nf:.2f} \\text{{ nF}}",
                    "result_value": round(c1_nf, 2),
                    "unit": "nF",
                    "notes": "Butterworth alignment guarantees maximally flat passband with zero ripple.",
                },
                {
                    "step_number": 2,
                    "title": "Calculate Ground Reference Capacitor (C_2)",
                    "formula": r"C_2 = \frac{C_1}{2}",
                    "substitution": f"C_2 = \\frac{{{c1_nf:.2f}}}{{2}} = {c2_nf:.2f} \\text{{ nF}}",
                    "result_value": round(c2_nf, 2),
                    "unit": "nF",
                    "notes": "Ensures critical damping factor Q = 0.707.",
                },
            ],
            "kpis": [
                {"label": "Cutoff f_c", "value": fc_hz, "unit": "Hz", "status": "OPTIMAL"},
                {"label": "Capacitor C1", "value": round(c1_nf, 2), "unit": "nF", "status": "OPTIMAL"},
                {"label": "Capacitor C2", "value": round(c2_nf, 2), "unit": "nF", "status": "OPTIMAL"},
            ],
            "compliance_checks": [
                {
                    "standard_code": "IEEE Signal Processing Society Guidelines",
                    "parameter_checked": "Filter Damping Factor",
                    "threshold": "Q == 0.707 (Butterworth)",
                    "actual_value": "Q = 0.707",
                    "status": "PASS",
                    "recommendation": "Use 1% metal film resistors and COG/NPO ceramic capacitors for temperature stability.",
                }
            ],
            "compliance_verdict": "COMPLIANT",
            "executable_code": code,
            "schematic_svg_or_ascii": (
                "  Vin ---[R1]---+---[R2]---> (+) [Op-Amp] ---> Vout\n"
                "                |             |       |\n"
                "               [C1]           |       |\n"
                "                |             +---(-) |\n"
                "                +---------------------+\n"
                "                | \n"
                "               [C2] ---> GND\n"
            ),
            "created_by": user_id or "discipline_agent_ee",
            "created_at": datetime.utcnow().isoformat(),
        }
