import { useState, useEffect } from 'react';
import { api } from '../services/api';

const PRESET_CAPSTONES = [
  {
    team_name: 'VoltGrid Autonomous Collective',
    project_title: 'Autonomous Microgrid Peer-to-Peer Energy Exchange',
    domain: 'Energy IoT & Decentralized Grid',
    mission_statement: 'Develop an autonomous multi-agent microgrid coordinator capable of orchestrating peer-to-peer renewable solar/battery energy exchanges, balancing local feeder load variations, and preventing feeder congestion.',
    team_members: [
      { name: 'Dr. Aris Vance', role: 'Lead Systems Architect', agent_type: 'architect', avatar: '🧠', contribution_summary: 'Grid topology, state machine design & smart contract interfaces' },
      { name: 'Elena Rostova', role: 'Research Intelligence Officer', agent_type: 'research', avatar: '🔍', contribution_summary: 'IEEE 1547 standards review & tariff dynamic evidence table' },
      { name: 'Devin Chen', role: 'SDLC Implementation Engineer', agent_type: 'sdlc', avatar: '💻', contribution_summary: 'Core double-auction matching engine & Python verification module' },
      { name: 'Sarah Miller', role: 'Test Harness & QA Lead', agent_type: 'devops', avatar: '🧪', contribution_summary: 'Boundary edge test suites, concurrency locks & in-memory runner' },
      { name: 'Marcus Kane', role: 'Safety & Governance Officer', agent_type: 'governance', avatar: '🛡️', contribution_summary: 'Grid fault injection checks, voltage bounds & rollback plan' },
    ],
  },
  {
    team_name: 'Apex Quant Systems',
    project_title: 'Ultra-Low-Latency Limit Order Matching Engine',
    domain: 'FinTech & Algorithmic Trading',
    mission_statement: 'Architect and synthesize a deterministic price-time priority Limit Order Book matching engine supporting microsecond execution, atomic trade ledgering, and FINRA regulatory audit compliance.',
    team_members: [
      { name: 'Liam Sterling', role: 'Lead Systems Architect', agent_type: 'architect', avatar: '🧠', contribution_summary: 'Price-time priority matching algorithm & memory layout' },
      { name: 'Maya Patel', role: 'Financial Research Agent', agent_type: 'research', avatar: '🔍', contribution_summary: 'FINRA Rule 5310 Best Execution & FIX 4.4 protocol mapping' },
      { name: 'Kenji Sato', role: 'SDLC Implementation Lead', agent_type: 'sdlc', avatar: '💻', contribution_summary: 'LimitOrder and OrderBook core data structures & sorting' },
      { name: 'Chloe Bennett', role: 'QA & Latency Benchmark Engineer', agent_type: 'devops', avatar: '🧪', contribution_summary: 'Unit test suites, synthetic load tests & boundary checks' },
      { name: 'Alexander Hayes', role: 'Safety & Governance Officer', agent_type: 'governance', avatar: '🛡️', contribution_summary: 'Audit trail logging, market manipulation checks & circuit breaker' },
    ],
  },
  {
    team_name: 'BioMed AI Consortium',
    project_title: 'Clinical Patient Triage & Vital Telemetry Coordinator',
    domain: 'Healthcare AI & Clinical Informatics',
    mission_statement: 'Develop a HIPAA-compliant autonomous clinical agent triage network that continuously monitors ICU and emergency telemetry streams, predicts acute decompensation, and ranks Emergency Severity Index.',
    team_members: [
      { name: 'Dr. Claire Huang', role: 'Lead Systems Architect', agent_type: 'architect', avatar: '🧠', contribution_summary: 'HIPAA compliance architecture & Emergency Severity Index logic' },
      { name: 'Dr. Tariq Mansoor', role: 'Medical Research Officer', agent_type: 'research', avatar: '🔍', contribution_summary: 'Clinical protocol benchmarking & vital sign threshold validation' },
      { name: 'Jasmine Wu', role: 'SDLC Implementation Lead', agent_type: 'sdlc', avatar: '💻', contribution_summary: 'Triage coordinator class & vital scoring algorithm' },
      { name: 'Kevin Brooks', role: 'Verification & QA Lead', agent_type: 'devops', avatar: '🧪', contribution_summary: 'Synthetic patient telemetry tests & boundary validation' },
      { name: 'Rachel Adams', role: 'Safety & Governance Officer', agent_type: 'governance', avatar: '🛡️', contribution_summary: 'HIPAA PII redaction checks & algorithmic bias auditing' },
    ],
  },
  {
    team_name: 'SkyMesh Robotics Lab',
    project_title: 'Autonomous Drone Swarm Telemetry & Spatial Collision Avoidance',
    domain: 'Robotics & Aerospace Autonomy',
    mission_statement: 'Design and orchestrate an autonomous drone swarm telemetry coordinator that maintains real-time 3D spatial deconfliction, dynamic geofencing, and distributed swarm formation.',
    team_members: [
      { name: 'Capt. Nathan Cole', role: 'Lead Systems Architect', agent_type: 'architect', avatar: '🧠', contribution_summary: '3D spatial geometry & swarm formation state machine' },
      { name: 'Ananya Sharma', role: 'Aerospace Research Agent', agent_type: 'research', avatar: '🔍', contribution_summary: 'FAA Part 107 regulations & ADS-B broadcast protocol analysis' },
      { name: 'Felix Baum', role: 'SDLC Implementation Lead', agent_type: 'sdlc', avatar: '💻', contribution_summary: 'Spatial distance calculation & collision avoidance vectoring' },
      { name: 'Zara Vance', role: 'Verification & Simulation Lead', agent_type: 'devops', avatar: '🧪', contribution_summary: '3D trajectory simulation tests & boundary collision checks' },
      { name: 'Garrison Hall', role: 'Safety & Airspace Governance', agent_type: 'governance', avatar: '🛡️', contribution_summary: 'Emergency geofence containment & failsafe RTL protocol' },
    ],
  },
];

export default function CapstoneStudioPage({ currentUser }) {
  // Input Form State
  const [selectedPresetIndex, setSelectedPresetIndex] = useState(0);
  const [teamName, setTeamName] = useState(PRESET_CAPSTONES[0].team_name);
  const [projectTitle, setProjectTitle] = useState(PRESET_CAPSTONES[0].project_title);
  const [domain, setDomain] = useState(PRESET_CAPSTONES[0].domain);
  const [missionStatement, setMissionStatement] = useState(PRESET_CAPSTONES[0].mission_statement);

  // Active Project State
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('deliverables'); // 'deliverables' | 'messages' | 'architecture' | 'tests' | 'export'

  // Deliverables File Viewer State
  const [selectedFileIndex, setSelectedFileIndex] = useState(0);
  const [fileCopySuccess, setFileCopySuccess] = useState('');

  // Re-run Tests State
  const [runningTests, setRunningTests] = useState(false);

  // Export State
  const [exportFormat, setExportFormat] = useState('markdown');
  const [exportedDossier, setExportedDossier] = useState('');
  const [copyDossierSuccess, setCopyDossierSuccess] = useState(false);

  // Saved Capstones History
  const [savedProjects, setSavedProjects] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  useEffect(() => {
    loadSavedProjects();
  }, []);

  const loadSavedProjects = async () => {
    setLoadingHistory(true);
    try {
      const data = await api.getCapstoneProjects();
      setSavedProjects(data || []);
    } catch (err) {
      console.warn('Failed to load capstone projects:', err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleApplyPreset = (idx) => {
    setSelectedPresetIndex(idx);
    const p = PRESET_CAPSTONES[idx];
    setTeamName(p.team_name);
    setProjectTitle(p.project_title);
    setDomain(p.domain);
    setMissionStatement(p.mission_statement);
    setError(null);
  };

  const handleLaunchPipeline = async () => {
    if (!teamName.trim() || !projectTitle.trim()) {
      setError('Please provide a team name and project title.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const preset = PRESET_CAPSTONES[selectedPresetIndex];
      const result = await api.createCapstoneProject({
        team_name: teamName,
        project_title: projectTitle,
        domain: domain,
        mission_statement: missionStatement,
        team_members: preset.team_members,
        user_id: currentUser?.username || 'team_lead',
        auto_execute_pipeline: true,
      });

      setProject(result);
      setSelectedFileIndex(0);
      loadSavedProjects();
      loadExport(result, exportFormat);
    } catch (err) {
      setError(err.message || 'Capstone pipeline execution failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleRunTests = async () => {
    if (!project?.id) return;
    setRunningTests(true);
    setError(null);
    try {
      const run = await api.runCapstoneTests(project.id);
      setProject((prev) => ({
        ...prev,
        test_run: run,
      }));
      loadSavedProjects();
    } catch (err) {
      setError(err.message || 'Test execution failed.');
    } finally {
      setRunningTests(false);
    }
  };

  const loadExport = async (currentProj, format) => {
    if (!currentProj) return;
    try {
      const res = await api.exportCapstoneReport({
        project: currentProj,
        format,
      });
      setExportedDossier(res.content);
    } catch (err) {
      console.warn('Export report error:', err);
    }
  };

  const handleFormatChange = (fmt) => {
    setExportFormat(fmt);
    if (project) {
      loadExport(project, fmt);
    }
  };

  const handleCopyDossier = () => {
    if (!exportedDossier) return;
    navigator.clipboard.writeText(exportedDossier);
    setCopyDossierSuccess(true);
    setTimeout(() => setCopyDossierSuccess(false), 2500);
  };

  const handleCopyFileContent = (content) => {
    navigator.clipboard.writeText(content);
    setFileCopySuccess('Copied!');
    setTimeout(() => setFileCopySuccess(''), 2000);
  };

  const handleSelectProject = async (projId) => {
    setLoading(true);
    try {
      const fetched = await api.getCapstoneProject(projId);
      setProject(fetched);
      setTeamName(fetched.team_name);
      setProjectTitle(fetched.project_title);
      setDomain(fetched.domain);
      setMissionStatement(fetched.mission_statement);
      setSelectedFileIndex(0);
      loadExport(fetched, exportFormat);
    } catch (err) {
      setError(err.message || 'Failed to load capstone project.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteProject = async (projId, e) => {
    e.stopPropagation();
    if (!window.confirm(`Delete Capstone Project ${projId}?`)) return;
    try {
      await api.deleteCapstoneProject(projId);
      if (project?.id === projId) {
        setProject(null);
      }
      loadSavedProjects();
    } catch (err) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  const currentMembers = project?.team_members || PRESET_CAPSTONES[selectedPresetIndex].team_members;

  return (
    <div className="page-content capstone-page">
      {/* Banner */}
      <div className="cap-header-banner">
        <div className="cap-banner-content">
          <div className="cap-eyebrow">Lab 14 · Capstone Project Studio</div>
          <h1>Autonomous Full Team-Owned Agentic System</h1>
          <p>
            The culminating capstone studio uniting specialized agents into a collaborative engineering team.
            Orchestrates an autonomous 5-stage pipeline: Discovery, Architecture Blueprint, Implementation,
            Verification Test Harness, and Governance Gate.
          </p>
        </div>
        <div className="cap-banner-stats">
          <div className="cap-stat-box">
            <span className="cap-stat-number">{savedProjects.length}</span>
            <span className="cap-stat-label">Capstone Teams</span>
          </div>
          <div className="cap-stat-box">
            <span className="cap-stat-number">5</span>
            <span className="cap-stat-label">Pipeline Stages</span>
          </div>
          <div className="cap-stat-box">
            <span className="cap-stat-number">100%</span>
            <span className="cap-stat-label">Verified Quality</span>
          </div>
        </div>
      </div>

      {error && (
        <div className="cap-alert-banner cap-alert-error">
          <span className="alert-icon">⚠️</span>
          <span>{error}</span>
          <button className="alert-dismiss" onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {/* Grid Layout: Config on Left, Execution Dashboard on Right */}
      <div className="cap-grid-layout">
        {/* Left Column: Preset Templates & Team Charter */}
        <div className="cap-input-column">
          {/* Preset Selector */}
          <div className="cap-panel">
            <div className="panel-heading">
              <span className="eyebrow">Capstone Focus Areas</span>
              <h3>Select Team Capstone Preset</h3>
            </div>
            <div className="cap-presets-list">
              {PRESET_CAPSTONES.map((preset, idx) => (
                <div
                  key={idx}
                  className={`cap-preset-card ${selectedPresetIndex === idx ? 'active' : ''}`}
                  onClick={() => handleApplyPreset(idx)}
                >
                  <div className="cap-preset-header-row">
                    <span className="cap-domain-pill">{preset.domain}</span>
                    <strong>{preset.team_name}</strong>
                  </div>
                  <h4 className="cap-preset-title">{preset.project_title}</h4>
                  <p className="cap-preset-desc">{preset.mission_statement}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Team Charter Form */}
          <div className="cap-panel">
            <div className="panel-heading">
              <span className="eyebrow">Team Assembly Charter</span>
              <h3>Project Specifications</h3>
            </div>

            <div className="cap-form-group">
              <label>Team Name</label>
              <input
                type="text"
                className="cap-input"
                value={teamName}
                onChange={(e) => setTeamName(e.target.value)}
              />
            </div>

            <div className="cap-form-group">
              <label>Capstone Initiative Title</label>
              <input
                type="text"
                className="cap-input"
                value={projectTitle}
                onChange={(e) => setProjectTitle(e.target.value)}
              />
            </div>

            <div className="cap-form-group">
              <label>Industry / Academic Domain</label>
              <input
                type="text"
                className="cap-input"
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
              />
            </div>

            <div className="cap-form-group">
              <label>Mission Statement & Problem Scope</label>
              <textarea
                className="cap-textarea"
                rows={3}
                value={missionStatement}
                onChange={(e) => setMissionStatement(e.target.value)}
              />
            </div>

            {/* Team Roster Preview */}
            <div className="cap-roster-preview">
              <div className="cap-roster-heading">
                <span className="eyebrow">Autonomous Swarm Roster</span>
                <h4>Assigned Specialist Agents ({currentMembers.length})</h4>
              </div>
              <div className="cap-roster-list">
                {currentMembers.map((member, mIdx) => (
                  <div key={mIdx} className="cap-member-row">
                    <span className="cap-member-avatar">{member.avatar || '🤖'}</span>
                    <div className="cap-member-info">
                      <strong>{member.name}</strong>
                      <span>{member.role}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <button
              className="cap-btn-launch"
              onClick={handleLaunchPipeline}
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="cap-spinner" />
                  <span>Executing 5-Stage Autonomous Pipeline...</span>
                </>
              ) : (
                <>
                  <span>🚀</span>
                  <span>Launch Capstone Pipeline (5 Stages)</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Column: Execution Results Dashboard */}
        <div className="cap-result-column">
          {project ? (
            <div className="cap-project-results">
              {/* Executive Header Card */}
              <div className="cap-assessment-card">
                <div className="cap-card-top-row">
                  <div>
                    <span className="cap-project-id">PROJECT ID: {project.id}</span>
                    <h2 className="cap-project-title">{project.project_title}</h2>
                    <div className="cap-project-meta">
                      <span>Team: <strong>{project.team_name}</strong></span>
                      <span>·</span>
                      <span className="cap-domain-tag">{project.domain}</span>
                      <span>·</span>
                      <span>{new Date(project.created_at).toLocaleTimeString()}</span>
                    </div>
                  </div>

                  <div className="cap-top-actions">
                    <a
                      href={api.getCapstoneZipUrl(project.id)}
                      className="cap-btn-download"
                      download
                    >
                      <span>📦</span>
                      <span>Download Repository (.zip)</span>
                    </a>
                  </div>
                </div>

                {/* Status Badges Row */}
                <div className="cap-badges-strip">
                  <div className="cap-badge-item">
                    <span className="cap-badge-label">Status:</span>
                    <span className="cap-status-pill cap-status-completed">
                      {project.status.toUpperCase()}
                    </span>
                  </div>
                  <div className="cap-badge-item">
                    <span className="cap-badge-label">Governance Risk:</span>
                    <span className="cap-status-pill cap-status-gov">
                      {project.overall_risk_score}/100 ({project.governance_tier})
                    </span>
                  </div>
                  <div className="cap-badge-item">
                    <span className="cap-badge-label">Verification:</span>
                    <span className="cap-status-pill cap-status-tests">
                      {project.test_run.passed} / {project.test_run.total_tests} Tests ({project.test_run.coverage_pct}% Coverage)
                    </span>
                  </div>
                  <div className="cap-badge-item">
                    <span className="cap-badge-label">Artifacts:</span>
                    <span className="cap-badge-num">{project.deliverables.length} Deliverables</span>
                  </div>
                </div>

                {/* 5-Stage Pipeline Stepper Bar */}
                <div className="cap-stages-stepper">
                  {project.stages.map((stage, sIdx) => (
                    <div key={stage.stage_id} className="cap-stepper-item">
                      <div className="cap-stepper-circle">✓</div>
                      <div className="cap-stepper-details">
                        <span className="cap-stepper-num">Stage {sIdx + 1}</span>
                        <strong className="cap-stepper-title">{stage.name.replace(/Phase \d+: /, '')}</strong>
                        <span className="cap-stepper-agent">{stage.assigned_agent.split(' ')[0]} ({stage.execution_time_sec}s)</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Navigation Tabs */}
              <div className="cap-tabs-nav">
                <button
                  className={`cap-tab-btn ${activeTab === 'deliverables' ? 'active' : ''}`}
                  onClick={() => setActiveTab('deliverables')}
                >
                  <span>📁</span> Codebase & Deliverables ({project.deliverables.length})
                </button>
                <button
                  className={`cap-tab-btn ${activeTab === 'messages' ? 'active' : ''}`}
                  onClick={() => setActiveTab('messages')}
                >
                  <span>💬</span> Inter-Agent Swarm Board ({project.messages.length})
                </button>
                <button
                  className={`cap-tab-btn ${activeTab === 'architecture' ? 'active' : ''}`}
                  onClick={() => setActiveTab('architecture')}
                >
                  <span>🏗️</span> System Architecture
                </button>
                <button
                  className={`cap-tab-btn ${activeTab === 'tests' ? 'active' : ''}`}
                  onClick={() => setActiveTab('tests')}
                >
                  <span>🧪</span> Verification Harness ({project.test_run.passed} Passed)
                </button>
                <button
                  className={`cap-tab-btn ${activeTab === 'export' ? 'active' : ''}`}
                  onClick={() => {
                    setActiveTab('export');
                    loadExport(project, exportFormat);
                  }}
                >
                  <span>📄</span> Capstone Dossier Export
                </button>
              </div>

              {/* Tab 1: Deliverables File Viewer */}
              {activeTab === 'deliverables' && project.deliverables.length > 0 && (
                <div className="cap-tab-pane">
                  <div className="cap-file-viewer-header">
                    <div className="cap-file-tabs">
                      {project.deliverables.map((deliv, fIdx) => (
                        <button
                          key={fIdx}
                          className={`cap-file-tab ${selectedFileIndex === fIdx ? 'active' : ''}`}
                          onClick={() => setSelectedFileIndex(fIdx)}
                        >
                          <span className="file-cat-tag">{deliv.category}</span>
                          <span className="file-name">{deliv.file_path.split('/').pop()}</span>
                        </button>
                      ))}
                    </div>

                    <button
                      className="cap-btn-copy-file"
                      onClick={() => handleCopyFileContent(project.deliverables[selectedFileIndex].content)}
                    >
                      {fileCopySuccess ? '✓ ' + fileCopySuccess : 'Copy File Content'}
                    </button>
                  </div>

                  <div className="cap-file-meta-bar">
                    <span>Path: <code>{project.deliverables[selectedFileIndex].file_path}</code></span>
                    <span>Category: <strong>{project.deliverables[selectedFileIndex].category}</strong></span>
                    <span>Title: <strong>{project.deliverables[selectedFileIndex].title}</strong></span>
                  </div>

                  <pre className="cap-code-display">{project.deliverables[selectedFileIndex].content}</pre>
                </div>
              )}

              {/* Tab 2: Inter-Agent Swarm Board */}
              {activeTab === 'messages' && (
                <div className="cap-tab-pane">
                  <div className="cap-tab-intro">
                    <h3>Inter-Agent Message Board & Swarm Collaboration Trace</h3>
                    <p>Live communication log showing task handoffs, technical queries, and consensus approvals.</p>
                  </div>

                  <div className="cap-messages-feed">
                    {project.messages.map((msg, mIdx) => (
                      <div key={mIdx} className="cap-msg-card">
                        <div className="cap-msg-header">
                          <div className="cap-msg-sender-info">
                            <span className="cap-msg-avatar">🤖</span>
                            <strong>{msg.sender}</strong>
                            <span className="cap-arrow">➔</span>
                            <span className="cap-receiver">{msg.receiver}</span>
                          </div>
                          <div className="cap-msg-meta">
                            <span className={`cap-msg-type-pill type-${msg.message_type.toLowerCase()}`}>
                              {msg.message_type}
                            </span>
                            <span className="cap-msg-time">{msg.timestamp}</span>
                          </div>
                        </div>
                        <p className="cap-msg-content">{msg.content}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Tab 3: System Architecture */}
              {activeTab === 'architecture' && (
                <div className="cap-tab-pane">
                  <div className="cap-tab-intro">
                    <h3>System Architecture & Topology Blueprint</h3>
                    <p>Component boundary mapping, event flow, and thread-safe data structures.</p>
                  </div>

                  <div className="cap-architecture-box">
                    <pre className="cap-arch-ascii">{project.architecture_diagram}</pre>
                  </div>
                </div>
              )}

              {/* Tab 4: Verification & Test Harness */}
              {activeTab === 'tests' && (
                <div className="cap-tab-pane">
                  <div className="cap-tab-intro">
                    <div className="cap-test-header-row">
                      <div>
                        <h3>Automated Verification & Test Harness</h3>
                        <p>In-memory test suites executed against generated code modules.</p>
                      </div>
                      <button
                        className="cap-btn-retest"
                        onClick={handleRunTests}
                        disabled={runningTests}
                      >
                        {runningTests ? (
                          <>
                            <span className="cap-spinner" />
                            <span>Executing Test Harness...</span>
                          </>
                        ) : (
                          <>
                            <span>▶</span>
                            <span>Re-run Verification Tests</span>
                          </>
                        )}
                      </button>
                    </div>
                  </div>

                  <div className="cap-test-stats-row">
                    <div className="cap-tstat-card">
                      <span className="tstat-label">Total Tests</span>
                      <strong className="tstat-num">{project.test_run.total_tests}</strong>
                    </div>
                    <div className="cap-tstat-card card-pass">
                      <span className="tstat-label">Passed</span>
                      <strong className="tstat-num">{project.test_run.passed}</strong>
                    </div>
                    <div className="cap-tstat-card card-fail">
                      <span className="tstat-label">Failed</span>
                      <strong className="tstat-num">{project.test_run.failed}</strong>
                    </div>
                    <div className="cap-tstat-card card-cov">
                      <span className="tstat-label">Code Coverage</span>
                      <strong className="tstat-num">{project.test_run.coverage_pct}%</strong>
                    </div>
                  </div>

                  <div className="cap-terminal-box">
                    <div className="cap-terminal-header">
                      <div className="terminal-dots">
                        <span className="dot red" />
                        <span className="dot yellow" />
                        <span className="dot green" />
                      </div>
                      <span className="terminal-title">test_harness_execution.log</span>
                    </div>
                    <pre className="cap-terminal-body">{project.test_run.execution_logs}</pre>
                  </div>
                </div>
              )}

              {/* Tab 5: Dossier Export */}
              {activeTab === 'export' && (
                <div className="cap-tab-pane">
                  <div className="cap-tab-intro">
                    <div className="cap-export-header-row">
                      <div>
                        <h3>Capstone Project Dossier Export</h3>
                        <p>Complete project documentation for academic grading and peer review.</p>
                      </div>
                      <div className="cap-export-actions">
                        <div className="cap-format-toggle">
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
                        <button className="cap-btn-copy" onClick={handleCopyDossier}>
                          {copyDossierSuccess ? '✓ Copied to Clipboard!' : 'Copy Dossier'}
                        </button>
                      </div>
                    </div>
                  </div>

                  <pre className="cap-export-viewer">{exportedDossier}</pre>
                </div>
              )}
            </div>
          ) : (
            <div className="cap-empty-state">
              <div className="cap-empty-icon">🎓</div>
              <h3>Capstone Project Studio Standby</h3>
              <p>
                Select an enterprise domain preset on the left or customize your team charter,
                then click <strong>Launch Capstone Pipeline</strong> to orchestrate the multi-agent collective
                across all 5 engineering stages.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Historical Projects Archive */}
      <div className="cap-history-section">
        <div className="cap-history-header">
          <div>
            <span className="eyebrow">Enterprise Capstone Portfolio</span>
            <h3>Saved Capstone Projects ({savedProjects.length})</h3>
          </div>
        </div>

        {loadingHistory ? (
          <div className="cap-loading-history">
            <span className="cap-spinner" />
            <span>Loading capstone portfolio archive...</span>
          </div>
        ) : savedProjects.length === 0 ? (
          <div className="cap-empty-history">
            <p>No historical capstone projects yet. Launch your first project above!</p>
          </div>
        ) : (
          <div className="cap-projects-grid">
            {savedProjects.map((item) => (
              <div
                key={item.id}
                className={`cap-project-tile ${project?.id === item.id ? 'active' : ''}`}
                onClick={() => handleSelectProject(item.id)}
              >
                <div className="cap-tile-header">
                  <span className="cap-tile-domain">{item.domain}</span>
                  <span className="cap-tile-id">{item.id}</span>
                </div>
                <h4 className="cap-tile-title">{item.project_title}</h4>
                <div className="cap-tile-team">Team: <strong>{item.team_name}</strong></div>
                <div className="cap-tile-footer">
                  <span className="cap-tile-tests">✓ {item.tests_passed} Tests Passed</span>
                  <button
                    className="cap-tile-del"
                    title="Delete Project"
                    onClick={(e) => handleDeleteProject(item.id, e)}
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
