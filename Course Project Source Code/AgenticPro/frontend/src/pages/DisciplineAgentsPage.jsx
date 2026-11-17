import { useState, useEffect } from 'react';
import { api } from '../services/api';

const DOMAIN_PRESETS = {
  ME: [
    {
      worklet_type: 'shaft_torsion_stress',
      title: 'Solid Drive Shaft Torsion & Angular Deflection',
      description: 'Calculate polar moment J, torsional shear stress tau, angular twist theta, and ASME B106.1M safety factor.',
      parameters: {
        torque: 1200.0,
        diameter_mm: 50.0,
        length_m: 1.5,
        yield_strength_mpa: 250.0,
        shear_modulus_gpa: 79.3,
      },
      fields: [
        { key: 'torque', label: 'Applied Operating Torque', unit: 'N·m', step: 50 },
        { key: 'diameter_mm', label: 'Shaft Outer Diameter', unit: 'mm', step: 1 },
        { key: 'length_m', label: 'Shaft Span Length', unit: 'm', step: 0.1 },
        { key: 'yield_strength_mpa', label: 'Material Yield Point (Sy)', unit: 'MPa', step: 10 },
        { key: 'shear_modulus_gpa', label: 'Shear Modulus (G)', unit: 'GPa', step: 1 },
      ],
    },
    {
      worklet_type: 'carnot_rankine_heat_engine',
      title: 'Carnot Limit & Superheated Rankine Cycle Efficiency',
      description: 'Evaluate thermodynamic Second Law limit, practical Rankine efficiency, and net electrical work output.',
      parameters: {
        th_temp_c: 550.0,
        tc_temp_c: 35.0,
        heat_input_qh_mw: 50.0,
      },
      fields: [
        { key: 'th_temp_c', label: 'Boiler Superheat Temp (TH)', unit: '°C', step: 10 },
        { key: 'tc_temp_c', label: 'Condenser Rejection Temp (TC)', unit: '°C', step: 1 },
        { key: 'heat_input_qh_mw', label: 'Boiler Heat Addition (QH)', unit: 'MW', step: 5 },
      ],
    },
    {
      worklet_type: 'beam_bending_stress',
      title: 'Simply Supported Beam Bending & Section Modulus',
      description: 'Analyze combined distributed and point loading, maximum bending moment, and AISC flexural safety factor.',
      parameters: {
        span_m: 4.0,
        distributed_load_kn_m: 15.0,
        point_load_kn: 20.0,
        yield_strength_mpa: 250.0,
        beam_width_mm: 150.0,
        beam_depth_mm: 300.0,
      },
      fields: [
        { key: 'span_m', label: 'Bearing Span (L)', unit: 'm', step: 0.5 },
        { key: 'distributed_load_kn_m', label: 'Uniform Distributed Load (w)', unit: 'kN/m', step: 1 },
        { key: 'point_load_kn', label: 'Center Point Load (P)', unit: 'kN', step: 5 },
        { key: 'beam_width_mm', label: 'Cross Section Width (b)', unit: 'mm', step: 10 },
        { key: 'beam_depth_mm', label: 'Cross Section Depth (h)', unit: 'mm', step: 10 },
        { key: 'yield_strength_mpa', label: 'Material Yield (Sy)', unit: 'MPa', step: 10 },
      ],
    },
  ],
  CE: [
    {
      worklet_type: 'rcc_beam_flexure',
      title: 'Reinforced Concrete Beam Flexural Capacity (ACI 318-19)',
      description: 'Determine Whitney stress block depth, nominal moment Mn, factored capacity phi*Mn, and steel ratio limits.',
      parameters: {
        span_m: 6.0,
        dead_load_kn_m: 18.0,
        live_load_kn_m: 12.0,
        fc_mpa: 28.0,
        fy_mpa: 420.0,
        width_b_mm: 300.0,
        eff_depth_d_mm: 500.0,
        num_bars: 4,
        bar_dia_mm: 25.0,
      },
      fields: [
        { key: 'span_m', label: 'Beam Span (L)', unit: 'm', step: 0.5 },
        { key: 'dead_load_kn_m', label: 'Unfactored Dead Load (wD)', unit: 'kN/m', step: 1 },
        { key: 'live_load_kn_m', label: 'Unfactored Live Load (wL)', unit: 'kN/m', step: 1 },
        { key: 'fc_mpa', label: 'Concrete Strength (fc)', unit: 'MPa', step: 2 },
        { key: 'fy_mpa', label: 'Rebar Yield Strength (fy)', unit: 'MPa', step: 20 },
        { key: 'width_b_mm', label: 'Beam Web Width (b)', unit: 'mm', step: 25 },
        { key: 'eff_depth_d_mm', label: 'Effective Depth (d)', unit: 'mm', step: 25 },
        { key: 'num_bars', label: 'Tension Rebar Count', unit: 'bars', step: 1 },
        { key: 'bar_dia_mm', label: 'Rebar Diameter (db)', unit: 'mm', step: 1 },
      ],
    },
    {
      worklet_type: 'retaining_wall_stability',
      title: 'Cantilever Retaining Wall Overturning & Sliding Stability',
      description: 'Compute Rankine active earth pressure Ka, lateral thrust Pa, and overturning/sliding safety factors.',
      parameters: {
        height_h_m: 4.5,
        gamma_soil_kn_m3: 18.0,
        friction_angle_deg: 30.0,
        wall_weight_kn_m: 145.0,
        footing_width_b_m: 2.8,
        friction_coeff_mu: 0.45,
      },
      fields: [
        { key: 'height_h_m', label: 'Stem Height (H)', unit: 'm', step: 0.5 },
        { key: 'gamma_soil_kn_m3', label: 'Soil Unit Weight (gamma)', unit: 'kN/m³', step: 0.5 },
        { key: 'friction_angle_deg', label: 'Internal Friction Angle (phi)', unit: '°', step: 1 },
        { key: 'wall_weight_kn_m', label: 'Total Wall Self-Weight (W)', unit: 'kN/m', step: 5 },
        { key: 'footing_width_b_m', label: 'Footing Base Width (B)', unit: 'm', step: 0.1 },
        { key: 'friction_coeff_mu', label: 'Base Friction Coeff (mu)', unit: '', step: 0.05 },
      ],
    },
    {
      worklet_type: 'stormwater_drainage',
      title: 'Stormwater Peak Runoff & Gravity Sewer Conduit Sizing',
      description: 'Estimate Rational Method peak runoff Q and size concrete storm drainage conduit using Manning equation.',
      parameters: {
        area_hectares: 12.0,
        runoff_coeff_c: 0.65,
        rainfall_intensity_mm_hr: 75.0,
        pipe_slope_s: 0.01,
        manning_n: 0.013,
      },
      fields: [
        { key: 'area_hectares', label: 'Catchment Area (A)', unit: 'ha', step: 1 },
        { key: 'runoff_coeff_c', label: 'Runoff Coefficient (C)', unit: '', step: 0.05 },
        { key: 'rainfall_intensity_mm_hr', label: 'Rainfall Intensity (I)', unit: 'mm/hr', step: 5 },
        { key: 'pipe_slope_s', label: 'Conduit Slope (S)', unit: 'm/m', step: 0.002 },
      ],
    },
  ],
  EE: [
    {
      worklet_type: 'rlc_filter_resonance',
      title: 'Series RLC Resonant Tank Circuit & Quality Factor (Q)',
      description: 'Compute resonant frequency f0, characteristic reactance XL, Q factor, half-power bandwidth, and damping ratio.',
      parameters: {
        r_ohms: 50.0,
        l_millihenry: 10.0,
        c_microfarad: 0.1,
        vs_volts: 12.0,
      },
      fields: [
        { key: 'r_ohms', label: 'Series Resistance (R)', unit: 'Ω', step: 5 },
        { key: 'l_millihenry', label: 'Inductance (L)', unit: 'mH', step: 1 },
        { key: 'c_microfarad', label: 'Capacitance (C)', unit: 'µF', step: 0.02 },
        { key: 'vs_volts', label: 'Source Voltage (Vs)', unit: 'V', step: 1 },
      ],
    },
    {
      worklet_type: 'three_phase_power_factor',
      title: '3-Phase Industrial Power Factor Correction & Capacitor Sizing',
      description: 'Calculate required shunt capacitor bank in kVAR to raise plant power factor to 0.95 and cut feeder line current.',
      parameters: {
        apparent_power_kva: 250.0,
        initial_pf: 0.78,
        target_pf: 0.95,
        line_voltage_v: 480.0,
      },
      fields: [
        { key: 'apparent_power_kva', label: 'Initial Apparent Power (S1)', unit: 'kVA', step: 10 },
        { key: 'initial_pf', label: 'Uncorrected Power Factor (PF1)', unit: 'lagging', step: 0.02 },
        { key: 'target_pf', label: 'Target Power Factor (PF2)', unit: 'lagging', step: 0.01 },
        { key: 'line_voltage_v', label: '3-Phase Bus Voltage (VL)', unit: 'V', step: 10 },
      ],
    },
    {
      worklet_type: 'opamp_sallen_key_filter',
      title: 'Active 2nd-Order Sallen-Key Low-Pass Filter (Butterworth)',
      description: 'Synthesize precision feedback capacitor values for unity-gain 2nd-order Butterworth low-pass filter.',
      parameters: {
        cutoff_freq_hz: 1000.0,
        resistor_r_ohms: 10000.0,
      },
      fields: [
        { key: 'cutoff_freq_hz', label: 'Cutoff Frequency (-3dB fc)', unit: 'Hz', step: 100 },
        { key: 'resistor_r_ohms', label: 'Bridge Resistors R1 = R2', unit: 'Ω', step: 500 },
      ],
    },
  ],
};

export default function DisciplineAgentsPage({ currentUser }) {
  // Discipline Selector State
  const [activeDiscipline, setActiveDiscipline] = useState('ME'); // 'ME' | 'CE' | 'EE'
  const [selectedPresetIndex, setSelectedPresetIndex] = useState(0);

  // Form Parameters
  const [customTitle, setCustomTitle] = useState(DOMAIN_PRESETS.ME[0].title);
  const [parameters, setParameters] = useState(DOMAIN_PRESETS.ME[0].parameters);

  // Result Worklet State
  const [worklet, setWorklet] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('derivations'); // 'derivations' | 'compliance' | 'code' | 'schematic' | 'export'

  // Code Simulation Runner State
  const [customCode, setCustomCode] = useState('');
  const [runningCode, setRunningCode] = useState(false);

  // Export State
  const [exportFormat, setExportFormat] = useState('markdown');
  const [exportedContent, setExportedContent] = useState('');
  const [copySuccess, setCopySuccess] = useState(false);

  // History Worklets Archive
  const [savedWorklets, setSavedWorklets] = useState([]);
  const [loadingWorklets, setLoadingWorklets] = useState(false);
  const [historyFilter, setHistoryFilter] = useState('ALL');

  useEffect(() => {
    loadSavedWorklets();
  }, [historyFilter]);

  const loadSavedWorklets = async () => {
    setLoadingWorklets(true);
    try {
      const params = {};
      if (historyFilter !== 'ALL') {
        params.discipline = historyFilter;
      }
      const data = await api.getDisciplineWorklets(params);
      setSavedWorklets(data || []);
    } catch (err) {
      console.warn('Failed to load discipline worklets:', err);
    } finally {
      setLoadingWorklets(false);
    }
  };

  const handleDisciplineChange = (disc) => {
    setActiveDiscipline(disc);
    setSelectedPresetIndex(0);
    const defaultPreset = DOMAIN_PRESETS[disc][0];
    setCustomTitle(defaultPreset.title);
    setParameters({ ...defaultPreset.parameters });
    setError(null);
  };

  const handlePresetSelect = (idx) => {
    setSelectedPresetIndex(idx);
    const preset = DOMAIN_PRESETS[activeDiscipline][idx];
    setCustomTitle(preset.title);
    setParameters({ ...preset.parameters });
    setError(null);
  };

  const handleParamChange = (key, val) => {
    const num = parseFloat(val);
    setParameters((prev) => ({
      ...prev,
      [key]: isNaN(num) ? 0 : num,
    }));
  };

  const handleSolveWorklet = async () => {
    setLoading(true);
    setError(null);
    try {
      const preset = DOMAIN_PRESETS[activeDiscipline][selectedPresetIndex];
      const result = await api.solveDisciplineWorklet({
        discipline: activeDiscipline,
        worklet_type: preset.worklet_type,
        title: customTitle,
        parameters: parameters,
        user_id: currentUser?.username || 'engineer_user',
        run_code_simulation: true,
      });

      setWorklet(result);
      setCustomCode(result.executable_code);
      loadSavedWorklets();
      loadExport(result, exportFormat);
    } catch (err) {
      setError(err.message || 'Worklet solving failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleRunCode = async () => {
    if (!worklet?.id) return;
    setRunningCode(true);
    setError(null);
    try {
      const updated = await api.runDisciplineCode(worklet.id, {
        custom_code: customCode || worklet.executable_code,
      });
      setWorklet(updated);
      loadSavedWorklets();
    } catch (err) {
      setError(err.message || 'Code simulation execution failed.');
    } finally {
      setRunningCode(false);
    }
  };

  const loadExport = async (currentWorklet, format) => {
    if (!currentWorklet) return;
    try {
      const res = await api.exportDisciplineReport({
        worklet: currentWorklet,
        format,
      });
      setExportedContent(res.content);
    } catch (err) {
      console.warn('Export report error:', err);
    }
  };

  const handleFormatChange = (fmt) => {
    setExportFormat(fmt);
    if (worklet) {
      loadExport(worklet, fmt);
    }
  };

  const handleCopyExport = () => {
    if (!exportedContent) return;
    navigator.clipboard.writeText(exportedContent);
    setCopySuccess(true);
    setTimeout(() => setCopySuccess(false), 2500);
  };

  const handleSelectWorklet = async (workletId) => {
    setLoading(true);
    try {
      const fetched = await api.getDisciplineWorklet(workletId);
      setWorklet(fetched);
      setActiveDiscipline(fetched.discipline);
      setCustomTitle(fetched.title);
      setCustomCode(fetched.executable_code);

      // Re-populate parameters
      const paramMap = {};
      fetched.parameters.forEach((p) => {
        paramMap[p.name.toLowerCase().replace(/[^a-z0-9_]/g, '_')] = p.value;
      });
      setParameters(paramMap);
      loadExport(fetched, exportFormat);
    } catch (err) {
      setError(err.message || 'Failed to load worklet.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteWorklet = async (workletId, e) => {
    e.stopPropagation();
    if (!window.confirm(`Delete engineering worklet ${workletId}?`)) return;
    try {
      await api.deleteDisciplineWorklet(workletId);
      if (worklet?.id === workletId) {
        setWorklet(null);
      }
      loadSavedWorklets();
    } catch (err) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  const currentPreset = DOMAIN_PRESETS[activeDiscipline][selectedPresetIndex];

  return (
    <div className="page-content discipline-page">
      {/* Banner */}
      <div className="disc-header-banner">
        <div className="disc-banner-content">
          <div className="disc-eyebrow">Lab 13 · Discipline-Specific Engineering Agents</div>
          <h1>Mechanical, Civil & Electrical Engineering Worklet Engine</h1>
          <p>
            Automated physics and engineering solvers executing step-by-step mathematical derivations,
            regulatory compliance verification (ASME, ACI 318, AISC, IEEE, NEC), and executable Python simulation scripts.
          </p>
        </div>
        <div className="disc-banner-stats">
          <div className="disc-stat-box">
            <span className="disc-stat-number">{savedWorklets.length}</span>
            <span className="disc-stat-label">Saved Worklets</span>
          </div>
          <div className="disc-stat-box">
            <span className="disc-stat-number">
              {savedWorklets.filter((w) => w.discipline === 'ME').length}
            </span>
            <span className="disc-stat-label">Mechanical (ME)</span>
          </div>
          <div className="disc-stat-box">
            <span className="disc-stat-number">
              {savedWorklets.filter((w) => w.discipline === 'CE').length}
            </span>
            <span className="disc-stat-label">Civil (CE)</span>
          </div>
          <div className="disc-stat-box">
            <span className="disc-stat-number">
              {savedWorklets.filter((w) => w.discipline === 'EE').length}
            </span>
            <span className="disc-stat-label">Electrical (EE)</span>
          </div>
        </div>
      </div>

      {error && (
        <div className="disc-alert-banner disc-alert-error">
          <span className="alert-icon">⚠️</span>
          <span>{error}</span>
          <button className="alert-dismiss" onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {/* Main Discipline Switcher Bar */}
      <div className="disc-switcher-bar">
        <button
          className={`disc-switch-btn ${activeDiscipline === 'ME' ? 'active-me' : ''}`}
          onClick={() => handleDisciplineChange('ME')}
        >
          <span className="disc-icon">⚙️</span>
          <div className="disc-switch-text">
            <strong>Mechanical Engineering (ME)</strong>
            <span>Torsion, Heat Cycles, Beam Flexure</span>
          </div>
        </button>
        <button
          className={`disc-switch-btn ${activeDiscipline === 'CE' ? 'active-ce' : ''}`}
          onClick={() => handleDisciplineChange('CE')}
        >
          <span className="disc-icon">🏗️</span>
          <div className="disc-switch-text">
            <strong>Civil Engineering (CE)</strong>
            <span>RCC Beams, Retaining Walls, Drainage</span>
          </div>
        </button>
        <button
          className={`disc-switch-btn ${activeDiscipline === 'EE' ? 'active-ee' : ''}`}
          onClick={() => handleDisciplineChange('EE')}
        >
          <span className="disc-icon">⚡</span>
          <div className="disc-switch-text">
            <strong>Electrical Engineering (EE)</strong>
            <span>RLC Circuits, Power Factor, Sallen-Key</span>
          </div>
        </button>
      </div>

      {/* Grid Layout: Config on Left, Solved Results on Right */}
      <div className="disc-grid-layout">
        {/* Left Column: Preset Templates & Input Parameters */}
        <div className="disc-input-column">
          {/* Preset Selector */}
          <div className="disc-panel">
            <div className="panel-heading">
              <span className="eyebrow">{activeDiscipline} Domain Templates</span>
              <h3>Select Engineering Worklet</h3>
            </div>
            <div className="disc-presets-list">
              {DOMAIN_PRESETS[activeDiscipline].map((preset, idx) => (
                <div
                  key={idx}
                  className={`disc-preset-card ${selectedPresetIndex === idx ? 'active' : ''}`}
                  onClick={() => handlePresetSelect(idx)}
                >
                  <div className="disc-preset-title-row">
                    <span className={`disc-badge disc-badge-${activeDiscipline.toLowerCase()}`}>
                      {activeDiscipline}
                    </span>
                    <strong>{preset.title}</strong>
                  </div>
                  <p className="disc-preset-desc">{preset.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Parameter Customization Form */}
          <div className="disc-panel">
            <div className="panel-heading">
              <span className="eyebrow">Input Variables</span>
              <h3>Physical Dimensions & Boundary Conditions</h3>
            </div>

            <div className="disc-form-group">
              <label>Worklet Title</label>
              <input
                type="text"
                className="disc-input"
                value={customTitle}
                onChange={(e) => setCustomTitle(e.target.value)}
              />
            </div>

            <div className="disc-params-grid">
              {currentPreset.fields.map((field) => (
                <div key={field.key} className="disc-form-group">
                  <div className="disc-label-row">
                    <label>{field.label}</label>
                    <span className="disc-unit-tag">{field.unit}</span>
                  </div>
                  <input
                    type="number"
                    step={field.step || 1}
                    className="disc-input"
                    value={parameters[field.key] ?? ''}
                    onChange={(e) => handleParamChange(field.key, e.target.value)}
                  />
                </div>
              ))}
            </div>

            <button
              className="disc-btn-primary"
              onClick={handleSolveWorklet}
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="disc-spinner" />
                  <span>Synthesizing Analytical Derivations...</span>
                </>
              ) : (
                <>
                  <span>📐</span>
                  <span>Solve Engineering Worklet</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Column: Calculated Solution Dashboard */}
        <div className="disc-result-column">
          {worklet ? (
            <div className="disc-worklet-results">
              {/* Executive Header Card */}
              <div className="disc-assessment-card">
                <div className="disc-card-top-row">
                  <div>
                    <span className="disc-worklet-id">WORKLET: {worklet.id}</span>
                    <h2 className="disc-worklet-title">{worklet.title}</h2>
                    <div className="disc-worklet-meta">
                      <span className={`disc-discipline-tag disc-tag-${worklet.discipline.toLowerCase()}`}>
                        {worklet.discipline}
                      </span>
                      <span>·</span>
                      <span>Type: <code>{worklet.worklet_type}</code></span>
                      <span>·</span>
                      <span>{new Date(worklet.created_at).toLocaleTimeString()}</span>
                    </div>
                  </div>

                  <div className="disc-verdict-box">
                    <span className={`disc-verdict-badge disc-verdict-${worklet.compliance_verdict.toLowerCase()}`}>
                      {worklet.compliance_verdict}
                    </span>
                    <span className="disc-verdict-sub">Design Standard Status</span>
                  </div>
                </div>

                {/* KPI Metrics Strip */}
                <div className="disc-kpi-strip">
                  {worklet.kpis.map((kpi, idx) => (
                    <div key={idx} className="disc-kpi-card">
                      <span className="disc-kpi-label">{kpi.label}</span>
                      <div className="disc-kpi-value-row">
                        <strong className="disc-kpi-num">{kpi.value}</strong>
                        <span className="disc-kpi-unit">{kpi.unit}</span>
                      </div>
                      <span className={`disc-kpi-status status-${kpi.status.toLowerCase()}`}>
                        {kpi.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Navigation Tabs */}
              <div className="disc-tabs-nav">
                <button
                  className={`disc-tab-btn ${activeTab === 'derivations' ? 'active' : ''}`}
                  onClick={() => setActiveTab('derivations')}
                >
                  <span>📐</span> Analytical Derivations ({worklet.derivation_steps.length})
                </button>
                <button
                  className={`disc-tab-btn ${activeTab === 'compliance' ? 'active' : ''}`}
                  onClick={() => setActiveTab('compliance')}
                >
                  <span>📋</span> Code Compliance ({worklet.compliance_checks.length})
                </button>
                <button
                  className={`disc-tab-btn ${activeTab === 'code' ? 'active' : ''}`}
                  onClick={() => setActiveTab('code')}
                >
                  <span>💻</span> Python Simulation Script
                </button>
                <button
                  className={`disc-tab-btn ${activeTab === 'schematic' ? 'active' : ''}`}
                  onClick={() => setActiveTab('schematic')}
                >
                  <span>🔍</span> Schematic Model
                </button>
                <button
                  className={`disc-tab-btn ${activeTab === 'export' ? 'active' : ''}`}
                  onClick={() => {
                    setActiveTab('export');
                    loadExport(worklet, exportFormat);
                  }}
                >
                  <span>📄</span> Calculation Export
                </button>
              </div>

              {/* Tab 1: Analytical Derivations */}
              {activeTab === 'derivations' && (
                <div className="disc-tab-pane">
                  <div className="disc-tab-intro">
                    <h3>Step-by-Step Mathematical Derivations</h3>
                    <p>Analytical calculations with explicit variable substitution, intermediate checks, and units.</p>
                  </div>

                  <div className="disc-derivations-list">
                    {worklet.derivation_steps.map((step) => (
                      <div key={step.step_number} className="disc-step-card">
                        <div className="disc-step-badge">{step.step_number}</div>
                        <div className="disc-step-content">
                          <h4 className="disc-step-title">{step.title}</h4>
                          <div className="disc-math-box">
                            <span className="math-label">Governing Formula:</span>
                            <code className="math-formula">{step.formula}</code>
                          </div>
                          <div className="disc-math-box">
                            <span className="math-label">Numeric Substitution:</span>
                            <span className="math-sub">{step.substitution}</span>
                          </div>
                          <div className="disc-step-result-bar">
                            <span className="result-label">Step Result:</span>
                            <strong className="result-val">{step.result_value} {step.unit}</strong>
                          </div>
                          {step.notes && (
                            <p className="disc-step-note">
                              <strong>Engineering Note:</strong> {step.notes}
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Tab 2: Regulatory Code Compliance */}
              {activeTab === 'compliance' && (
                <div className="disc-tab-pane">
                  <div className="disc-tab-intro">
                    <h3>Engineering Code & Standard Compliance Matrix</h3>
                    <p>Safety factors and design limits verified against industry standards (ASME, ACI 318, AISC, IEEE, NEC).</p>
                  </div>

                  <div className="disc-table-container">
                    <table className="disc-table">
                      <thead>
                        <tr>
                          <th>Regulatory Standard</th>
                          <th>Evaluated Metric</th>
                          <th>Standard Threshold</th>
                          <th>Observed Value</th>
                          <th>Status</th>
                          <th>Recommendation</th>
                        </tr>
                      </thead>
                      <tbody>
                        {worklet.compliance_checks.map((chk, idx) => (
                          <tr key={idx} className={`disc-row-${chk.status.toLowerCase()}`}>
                            <td>
                              <span className="disc-code-pill">{chk.standard_code}</span>
                            </td>
                            <td><strong>{chk.parameter_checked}</strong></td>
                            <td><code>{chk.threshold}</code></td>
                            <td><strong>{chk.actual_value}</strong></td>
                            <td>
                              <span className={`disc-status-tag status-${chk.status.toLowerCase()}`}>
                                {chk.status === 'PASS' && '✓ PASS'}
                                {chk.status === 'MARGINAL' && '⚠️ MARGINAL'}
                                {chk.status === 'FAIL' && '⛔ FAIL'}
                              </span>
                            </td>
                            <td>{chk.recommendation || 'Standard requirement satisfied.'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Tab 3: Python Simulation & Sandbox */}
              {activeTab === 'code' && (
                <div className="disc-tab-pane">
                  <div className="disc-tab-intro">
                    <div className="disc-code-header-row">
                      <div>
                        <h3>Python Simulation & Verification Script</h3>
                        <p>Standalone numerical script using math and numpy to replicate analytical derivations in-memory.</p>
                      </div>
                      <button
                        className="disc-btn-run"
                        onClick={handleRunCode}
                        disabled={runningCode}
                      >
                        {runningCode ? (
                          <>
                            <span className="disc-spinner" />
                            <span>Executing in Sandbox...</span>
                          </>
                        ) : (
                          <>
                            <span>▶</span>
                            <span>Run Simulation in Sandbox</span>
                          </>
                        )}
                      </button>
                    </div>
                  </div>

                  <div className="disc-code-editor-box">
                    <textarea
                      className="disc-code-textarea"
                      rows={14}
                      value={customCode}
                      onChange={(e) => setCustomCode(e.target.value)}
                    />
                  </div>

                  {/* Terminal Output */}
                  {worklet.code_execution_stdout && (
                    <div className="disc-terminal-box">
                      <div className="disc-terminal-header">
                        <div className="terminal-dots">
                          <span className="dot red" />
                          <span className="dot yellow" />
                          <span className="dot green" />
                        </div>
                        <span className="terminal-title">simulation_verification.stdout</span>
                      </div>
                      <pre className="disc-terminal-body">{worklet.code_execution_stdout}</pre>
                    </div>
                  )}
                </div>
              )}

              {/* Tab 4: Schematic Model */}
              {activeTab === 'schematic' && (
                <div className="disc-tab-pane">
                  <div className="disc-tab-intro">
                    <h3>Engineering System Diagram & Schematic</h3>
                    <p>Schematic diagram depicting loads, supports, dimensions, or circuit topology.</p>
                  </div>

                  <div className="disc-schematic-container">
                    <pre className="disc-schematic-ascii">{worklet.schematic_svg_or_ascii}</pre>
                  </div>
                </div>
              )}

              {/* Tab 5: Export & Compliance Report */}
              {activeTab === 'export' && (
                <div className="disc-tab-pane">
                  <div className="disc-tab-intro">
                    <div className="disc-export-header-row">
                      <div>
                        <h3>Engineering Calculation Sheet Export</h3>
                        <p>Standardized calculation sheet for peer engineering review and academic submissions.</p>
                      </div>
                      <div className="disc-export-actions">
                        <div className="disc-format-toggle">
                          <button
                            className={`format-btn ${exportFormat === 'markdown' ? 'active' : ''}`}
                            onClick={() => handleFormatChange('markdown')}
                          >
                            Markdown
                          </button>
                          <button
                            className={`format-btn ${exportFormat === 'json' ? 'active' : ''}`}
                            onClick={() => handleFormatChange('json')}
                          >
                            JSON
                          </button>
                        </div>
                        <button className="disc-btn-copy" onClick={handleCopyExport}>
                          {copySuccess ? '✓ Copied to Clipboard!' : 'Copy Calculation Sheet'}
                        </button>
                      </div>
                    </div>
                  </div>

                  <pre className="disc-export-viewer">{exportedContent}</pre>
                </div>
              )}
            </div>
          ) : (
            <div className="disc-empty-state">
              <div className="disc-empty-icon">📐</div>
              <h3>Engineering Solver Standby</h3>
              <p>
                Choose an engineering discipline (<strong>Mechanical</strong>, <strong>Civil</strong>, or <strong>Electrical</strong>)
                and select a worklet template on the left. Customize parameter values and click{' '}
                <strong>Solve Engineering Worklet</strong> to generate formulas, derivations, and simulation code.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Historical Worklets Archive Section */}
      <div className="disc-history-section">
        <div className="disc-history-header">
          <div>
            <span className="eyebrow">Calculation Archive</span>
            <h3>Historical Engineering Worklets ({savedWorklets.length})</h3>
          </div>
          <div className="disc-history-filters">
            {['ALL', 'ME', 'CE', 'EE'].map((flt) => (
              <button
                key={flt}
                className={`disc-filter-pill ${historyFilter === flt ? 'active' : ''}`}
                onClick={() => setHistoryFilter(flt)}
              >
                {flt === 'ALL' ? 'All Disciplines' : flt}
              </button>
            ))}
          </div>
        </div>

        {loadingWorklets ? (
          <div className="disc-loading-worklets">
            <span className="disc-spinner" />
            <span>Loading engineering calculation archive...</span>
          </div>
        ) : savedWorklets.length === 0 ? (
          <div className="disc-empty-worklets">
            <p>No historical worklets found for discipline filter: <strong>{historyFilter}</strong></p>
          </div>
        ) : (
          <div className="disc-worklets-grid">
            {savedWorklets.map((item) => (
              <div
                key={item.id}
                className={`disc-worklet-tile ${worklet?.id === item.id ? 'active' : ''}`}
                onClick={() => handleSelectWorklet(item.id)}
              >
                <div className="disc-tile-header">
                  <span className={`disc-tile-disc disc-tag-${item.discipline.toLowerCase()}`}>
                    {item.discipline}
                  </span>
                  <span className="disc-tile-id">{item.id}</span>
                </div>
                <h4 className="disc-tile-title">{item.title}</h4>
                <div className="disc-tile-footer">
                  <span className={`disc-status-tag status-${item.compliance_verdict.toLowerCase()}`}>
                    {item.compliance_verdict}
                  </span>
                  <button
                    className="disc-tile-del"
                    title="Delete Worklet"
                    onClick={(e) => handleDeleteWorklet(item.id, e)}
                  >
                    ✕
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
