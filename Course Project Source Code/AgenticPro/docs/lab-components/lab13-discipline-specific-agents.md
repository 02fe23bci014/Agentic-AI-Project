# Lab 13: Discipline-Specific Agents (ME / CE / EE Domain Worklet)

The **Discipline-Specific Agent** provides specialized analytical engineering calculations, mathematical derivations with step-by-step substitutions, code compliance verification, and executable Python simulation scripts across three major engineering disciplines:
1. **Mechanical Engineering (ME)**
2. **Civil Engineering (CE)**
3. **Electrical Engineering (EE)**

## Key Capabilities

1. **Mechanical Engineering (ME) Worklets**:
   - **Shaft Torsional Shear Stress & Angular Deflection**: Computes polar moment of inertia ($J = \frac{\pi d^4}{32}$), maximum peripheral shear stress ($\tau = \frac{Tr}{J}$), torsional twist rate ($\theta/L$), Von Mises shear yield strength ($\tau_y = 0.577 S_y$), and compliance with ASME B106.1M standards.
   - **Carnot & Rankine Thermal Cycles**: Evaluates boiler heat addition, thermodynamic Carnot theoretical limit ($\eta_{carnot} = 1 - T_C/T_H$), practical Rankine efficiency, net electrical power output ($W_{net}$), and waste heat rejection in accordance with ASME PTC 46.
   - **Simply Supported Beam Bending**: Analyzes combined distributed and concentrated point loading, maximum bending moments ($M_{max}$), section moduli ($Z = bh^2/6$), flexural stresses, and AISC 360-16 Allowable Stress Design safety factors.

2. **Civil Engineering (CE) Worklets**:
   - **Reinforced Concrete (RCC) Beam Flexural Strength**: Solves ACI 318-19 ultimate moment capacity ($\phi M_n$), equivalent rectangular Whitney stress block depth ($a$), required tension rebar area ($A_s$), and minimum/maximum steel reinforcement ratios ($\rho_{min} \le \rho \le \rho_{max}$).
   - **Cantilever Retaining Wall Stability**: Analyzes Rankine active lateral earth pressure coefficients ($K_a$), total active thrust ($P_a$), overturning moments ($M_{ot}$), stabilizing moments ($M_r$), and checks factors of safety against overturning ($FS_{ot} \ge 2.0$) and base sliding ($FS_{sl} \ge 1.5$).
   - **Stormwater Peak Runoff & Gravity Sewer Sizing**: Applies the Rational Method ($Q = CIA/360$) and Manning's hydraulic equation to size stormwater conduits ($D \propto (Qn/\sqrt{S})^{3/8}$) conforming to EPA/AASHTO drainage standards.

3. **Electrical Engineering (EE) Worklets**:
   - **Series/Parallel RLC Resonant Tank Circuits**: Calculates angular resonance ($\omega_0 = 1/\sqrt{LC}$), resonant frequency ($f_0$), characteristic impedance, quality factor ($Q = \omega_0 L / R$), half-power bandwidth ($BW$), and damping ratios ($\zeta$).
   - **3-Phase Industrial Power Factor Correction**: Sizes shunt capacitor banks ($Q_c = P(\tan\theta_1 - \tan\theta_2)$ in $kVAR$) to eliminate reactive power tariffs, reduce line current, and achieve IEEE 519 / NEC compliance ($PF \ge 0.95$).
   - **Active Sallen-Key Low-Pass Filters**: Synthesizes component values ($R_1, R_2, C_1, C_2$) for 2nd-order Butterworth filters with maximally flat passband response and $-40 \text{ dB/decade}$ roll-off.

4. **Executable Code Simulation & Verification**:
   - Every worklet synthesizes a standalone Python script verifying calculations in-memory.
   - Students and faculty can execute or modify simulation code in the interactive sandbox runner.

5. **Multi-Agent Swarm Integration**:
   - Orchestrated via `create_discipline_specific_swarm_agent()`.

## Architecture

- **Models**: `backend/models/discipline.py` (`ParameterItem`, `DerivationStep`, `ComplianceCheck`, `EngineeringKPI`, `DisciplineWorkletArtifact`, `WorkletSolveRequest`, `WorkletRunCodeRequest`, `DisciplineExportRequest`)
- **Tools**: `backend/tools/discipline_tool.py` (`DisciplineTool`: Python code executor, Markdown and JSON reporting)
- **Skills**: `backend/skills/discipline_agents/`
  - `prompt_builder.py`: LLM prompt generator.
  - `validator.py`: Pydantic structural validator.
  - `synthesizer.py`: High-fidelity deterministic solver for ME, CE, and EE worklets with exact formulas and derivation steps.
  - `skill.py`: Rapid 0.5s network reachability probe with domain fallback.
- **Agent**: `backend/agents/discipline_agent.py` (`DisciplineSpecificAgent`)
- **Database**: SQLite `discipline_worklets` table in `database/evaluations.db`.
- **API Routes**: `backend/api/discipline_routes.py` (mounted at `/api/discipline`)

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/discipline/solve` | Synthesize and solve discipline-specific engineering worklet (ME/CE/EE) |
| `GET` | `/api/discipline/worklets` | List historical worklets (filterable by `?discipline=` and `?worklet_type=`) |
| `GET` | `/api/discipline/worklets/{id}` | Retrieve full worklet artifact details |
| `POST` | `/api/discipline/worklets/{id}/run-code` | Execute or re-run Python simulation code in sandbox |
| `DELETE` | `/api/discipline/worklets/{id}` | Permanently delete a worklet record |
| `POST` | `/api/discipline/export` | Export engineering calculation report in Markdown or JSON |
