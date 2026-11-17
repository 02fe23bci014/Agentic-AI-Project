import { useState, useEffect } from 'react';
import { api } from '../services/api';

const PRESET_REQUIREMENTS = [
  {
    title: 'Token Bucket Rate Limiter with Concurrency Locks',
    project_name: 'Token Bucket Rate Limiter',
    framework: 'fastapi',
    architecture_style: 'clean_architecture',
    requirement_text: `Design and implement a high-throughput Token Bucket Rate Limiter service.
- Individual client pools with configurable max_capacity (default 10 tokens) and continuous refill rate (default 2 tokens/sec).
- Thread-safe token consumption using threading.Lock.
- Returns True if request quota is available and consumed; False if quota is depleted.
- Support key isolation so distinct clients have independent token buckets.`,
  },
  {
    title: 'Thread-Safe LRU Cache with TTL Expiration',
    project_name: 'In-Memory Cache with TTL',
    framework: 'fastapi',
    architecture_style: 'clean_architecture',
    requirement_text: `Build an in-memory caching engine with Least-Recently-Used (LRU) eviction and TTL support.
- Configurable capacity (default 100 items) and default TTL (default 3600 seconds).
- Evicts the least recently accessed item when capacity is exceeded upon insertion.
- Expired items must return None and be pruned.
- Thread-safe read and write operations.`,
  },
  {
    title: 'Decoupled Pub-Sub Event Bus with Error Isolation',
    project_name: 'Event-Driven Notification Bus',
    framework: 'fastapi',
    architecture_style: 'modular_monolith',
    requirement_text: `Construct a lightweight, thread-safe publish/subscribe Event Bus.
- Services can subscribe callback handlers to named event topics (e.g. 'user.created', 'order.paid').
- Dispatches messages synchronously to all registered topic subscribers.
- Handler failures must be isolated so one crashing handler does not interrupt delivery to other subscribers.
- Returns total count of successfully delivered events.`,
  },
  {
    title: 'Transactional Order & Inventory Coordinator',
    project_name: 'Order Lifecycle Service',
    framework: 'fastapi',
    architecture_style: 'clean_architecture',
    requirement_text: `Implement a modular order management service.
- Allows clients to create order records with unique item IDs, validate non-empty payload strings, and track status.
- Provides state transition methods (e.g. 'active' -> 'completed').
- Throws appropriate ValueError on empty inputs and KeyError on missing IDs.
- Includes thorough unit tests for normal execution, boundary inputs, and state updates.`,
  },
];

export default function SDLCFactoryPage({ currentUser }) {
  // Requirement Input Form
  const [projectName, setProjectName] = useState(PRESET_REQUIREMENTS[0].project_name);
  const [framework, setFramework] = useState(PRESET_REQUIREMENTS[0].framework);
  const [architectureStyle, setArchitectureStyle] = useState(PRESET_REQUIREMENTS[0].architecture_style);
  const [requirementText, setRequirementText] = useState(PRESET_REQUIREMENTS[0].requirement_text);
  const [autoExecuteTests, setAutoExecuteTests] = useState(true);

  // Active Artifact State
  const [artifact, setArtifact] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('code'); // 'code' | 'tests' | 'architecture' | 'stories' | 'docs'

  // Code Viewer State
  const [selectedFileIndex, setSelectedFileIndex] = useState(0);
  const [copyCodeSuccess, setCopyCodeSuccess] = useState('');

  // Re-run Tests State
  const [runningTests, setRunningTests] = useState(false);

  // Projects History State
  const [savedProjects, setSavedProjects] = useState([]);
  const [loadingProjects, setLoadingProjects] = useState(false);

  useEffect(() => {
    loadSavedProjects();
  }, []);

  const loadSavedProjects = async () => {
    setLoadingProjects(true);
    try {
      const data = await api.getSDLCProjects();
      setSavedProjects(data || []);
    } catch (err) {
      console.warn('Failed to fetch SDLC projects:', err);
    } finally {
      setLoadingProjects(false);
    }
  };

  const handleApplyPreset = (preset) => {
    setProjectName(preset.project_name);
    setFramework(preset.framework);
    setArchitectureStyle(preset.architecture_style);
    setRequirementText(preset.requirement_text);
  };

  const handleLaunchPipeline = async () => {
    if (!projectName.trim() || !requirementText.trim()) {
      setError('Please provide a project name and requirement specification.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const result = await api.runSDLCPipeline({
        project_name: projectName.trim(),
        requirement_text: requirementText.trim(),
        target_language: 'python',
        framework,
        architecture_style: architectureStyle,
        auto_execute_tests: autoExecuteTests,
        user_id: currentUser?.username || 'sdlc-architect',
      });
      setArtifact(result);
      setSelectedFileIndex(0);
      setActiveTab('code');
      loadSavedProjects();
    } catch (err) {
      setError(err.message || 'SDLC Pipeline execution failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadProject = async (projectId) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getSDLCProject(projectId);
      setArtifact(data);
      setProjectName(data.project_name);
      setRequirementText(data.requirement_text);
      setSelectedFileIndex(0);
      setActiveTab('code');
    } catch (err) {
      setError(err.message || 'Failed to load project artifact.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteProject = async (e, projectId) => {
    e.stopPropagation();
    if (!window.confirm('Delete this generated project artifact?')) return;
    try {
      await api.deleteSDLCProject(projectId);
      setSavedProjects((prev) => prev.filter((p) => p.id !== projectId));
      if (artifact?.id === projectId) {
        setArtifact(null);
      }
    } catch (err) {
      alert(`Could not delete project: ${err.message}`);
    }
  };

  const handleRerunTests = async () => {
    if (!artifact) return;
    setRunningTests(true);
    try {
      const testRun = await api.runSDLCTests(artifact.id);
      setArtifact((prev) => ({
        ...prev,
        test_run: testRun,
        status: testRun.failed === 0 ? 'completed' : 'tests_failed',
      }));
      loadSavedProjects();
    } catch (err) {
      alert(`Test runner error: ${err.message}`);
    } finally {
      setRunningTests(false);
    }
  };

  const handleCopyFileContent = () => {
    const file = artifact?.code_files?.[selectedFileIndex];
    if (!file) return;
    navigator.clipboard.writeText(file.content);
    setCopyCodeSuccess('Copied code to clipboard!');
    setTimeout(() => setCopyCodeSuccess(''), 2500);
  };

  const handleDownloadZip = () => {
    if (!artifact) return;
    window.location.href = api.getSDLCZipUrl(artifact.id);
  };

  const selectedFile = artifact?.code_files?.[selectedFileIndex];

  return (
    <div className="page-content sdlc-page">
      {/* Top Banner */}
      <div className="welcome-banner sdlc-banner">
        <div className="welcome-text">
          <div className="eyebrow">Lab Component 11</div>
          <h1>Agentic SDLC Factory · Requirement → Tested Implementation</h1>
          <p>
            Autonomous end-to-end software factory pipeline. Translates specifications into user stories,
            domain architecture, clean-architecture implementations, and executes automated test verification suites.
          </p>
        </div>
        <div className="welcome-stats">
          <div className="welcome-stat-pill">
            <span className="pill-num">{savedProjects.length}</span>
            <span className="pill-label">Projects Built</span>
          </div>
          <div className="welcome-stat-pill">
            <span className="pill-num">
              {artifact?.test_run?.passed ?? savedProjects.reduce((acc, p) => acc + (p.status === 'completed' ? 1 : 0), 0)}
            </span>
            <span className="pill-label">Verified Tests</span>
          </div>
        </div>
      </div>

      {/* Main Grid: Left Pipeline Input & Workspace, Right Archive */}
      <div className="sdlc-layout-grid">
        <div className="sdlc-main-column">
          {/* Requirement Ingestion Card */}
          <div className="panel sdlc-input-panel">
            <div className="panel-heading">
              <div>
                <span className="eyebrow">Software Specification</span>
                <h3>Project Requirements & Target Configuration</h3>
              </div>
              <span className="status-tag active">Autonomous SDLC Factory</span>
            </div>

            {/* Presets Chips */}
            <div className="sdlc-presets-wrapper">
              <span className="samples-label">Load Requirement Archetypes:</span>
              <div className="sdlc-chips-row">
                {PRESET_REQUIREMENTS.map((preset, idx) => (
                  <button
                    key={idx}
                    type="button"
                    className="sample-chip preset-chip"
                    onClick={() => handleApplyPreset(preset)}
                  >
                    🚀 {preset.title}
                  </button>
                ))}
              </div>
            </div>

            {/* Metadata Inputs */}
            <div className="sdlc-config-grid">
              <div className="config-item">
                <label className="config-label">Project Name</label>
                <input
                  type="text"
                  className="modern-text-input"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  placeholder="e.g. Token Bucket Rate Limiter"
                />
              </div>

              <div className="config-item">
                <label className="config-label">Architecture Pattern</label>
                <select
                  className="modern-select"
                  value={architectureStyle}
                  onChange={(e) => setArchitectureStyle(e.target.value)}
                >
                  <option value="clean_architecture">Clean Architecture (Ports & Adapters)</option>
                  <option value="modular_monolith">Modular Monolith</option>
                  <option value="domain_driven_design">Domain-Driven Design (DDD)</option>
                </select>
              </div>

              <div className="config-item">
                <label className="config-label">Framework</label>
                <select
                  className="modern-select"
                  value={framework}
                  onChange={(e) => setFramework(e.target.value)}
                >
                  <option value="fastapi">FastAPI (High-Performance Async)</option>
                  <option value="flask">Flask (Lightweight REST)</option>
                  <option value="standard-lib">Python Standard Library (Zero-Dependency)</option>
                </select>
              </div>
            </div>

            {/* Requirement Text */}
            <div className="requirement-input-wrapper">
              <label className="config-label">Requirements, Invariants & User Stories</label>
              <textarea
                className="code-textarea requirement-textarea"
                rows={6}
                value={requirementText}
                onChange={(e) => setRequirementText(e.target.value)}
                placeholder="Describe your software requirements, domain entities, constraints, and business logic..."
              />
            </div>

            <div className="sdlc-actions-bar">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={autoExecuteTests}
                  onChange={(e) => setAutoExecuteTests(e.target.checked)}
                />
                <span>Auto-execute generated unit test suite in isolated sandbox</span>
              </label>

              <button
                type="button"
                className="primary-button launch-pipeline-btn"
                onClick={handleLaunchPipeline}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner-inline" /> Operating SDLC Factory...
                  </>
                ) : (
                  'Launch Autonomous SDLC Factory →'
                )}
              </button>
            </div>

            {error && (
              <div className="alert-box alert-error">
                <strong>Pipeline Error:</strong> {error}
              </div>
            )}
          </div>

          {/* SDLC Pipeline Execution Progress Steps */}
          {artifact && (
            <div className="sdlc-pipeline-stepper">
              <div className="pipeline-step step-done">
                <span className="step-icon">✓</span>
                <div className="step-content">
                  <strong>Requirements</strong>
                  <small>{artifact.user_stories.length} User Stories</small>
                </div>
              </div>
              <div className="stepper-arrow">→</div>
              <div className="pipeline-step step-done">
                <span className="step-icon">✓</span>
                <div className="step-content">
                  <strong>Architecture</strong>
                  <small>{artifact.architecture.components.length} Components</small>
                </div>
              </div>
              <div className="stepper-arrow">→</div>
              <div className="pipeline-step step-done">
                <span className="step-icon">✓</span>
                <div className="step-content">
                  <strong>Implementation</strong>
                  <small>{artifact.code_files.length} Files Generated</small>
                </div>
              </div>
              <div className="stepper-arrow">→</div>
              <div className={`pipeline-step ${artifact.test_run.failed === 0 ? 'step-done' : 'step-warn'}`}>
                <span className="step-icon">{artifact.test_run.failed === 0 ? '✓' : '✗'}</span>
                <div className="step-content">
                  <strong>Automated Tests</strong>
                  <small>{artifact.test_run.passed}/{artifact.test_run.total} Passed ({artifact.test_run.coverage_pct}%)</small>
                </div>
              </div>
              <div className="stepper-arrow">→</div>
              <div className="pipeline-step step-done">
                <span className="step-icon">📦</span>
                <div className="step-content">
                  <strong>Package & ZIP</strong>
                  <small>Verified Artifact</small>
                </div>
              </div>
            </div>
          )}

          {/* Project Deliverable Workspace */}
          {artifact && (
            <div className="sdlc-workspace-wrapper">
              {/* Header Actions */}
              <div className="workspace-header-card panel">
                <div>
                  <div className="workspace-meta-tags">
                    <span className="status-badge-pill status-remediated">
                      {artifact.status.toUpperCase()}
                    </span>
                    <span className="lang-pill">{artifact.target_language.toUpperCase()}</span>
                    <span className="framework-pill">{artifact.framework}</span>
                    <span className="arch-pill">{artifact.architecture_style}</span>
                  </div>
                  <h2>{artifact.project_name}</h2>
                </div>

                <div className="workspace-actions">
                  <button
                    type="button"
                    className="secondary-button"
                    onClick={handleRerunTests}
                    disabled={runningTests}
                  >
                    {runningTests ? 'Running Tests...' : '⚡ Re-Run Test Suite'}
                  </button>
                  <button
                    type="button"
                    className="primary-button download-zip-btn"
                    onClick={handleDownloadZip}
                  >
                    ⬇ Download Project (.ZIP)
                  </button>
                </div>
              </div>

              {/* Navigation Tabs */}
              <div className="results-top-nav">
                <div className="results-tabs">
                  <button
                    type="button"
                    className={`tab-btn ${activeTab === 'code' ? 'tab-active' : ''}`}
                    onClick={() => setActiveTab('code')}
                  >
                    💻 Source & Tests ({artifact.code_files.length})
                  </button>
                  <button
                    type="button"
                    className={`tab-btn ${activeTab === 'tests' ? 'tab-active' : ''}`}
                    onClick={() => setActiveTab('tests')}
                  >
                    🧪 Verification Console ({artifact.test_run.passed}/{artifact.test_run.total})
                  </button>
                  <button
                    type="button"
                    className={`tab-btn ${activeTab === 'architecture' ? 'tab-active' : ''}`}
                    onClick={() => setActiveTab('architecture')}
                  >
                    📐 Architecture & Design
                  </button>
                  <button
                    type="button"
                    className={`tab-btn ${activeTab === 'stories' ? 'tab-active' : ''}`}
                    onClick={() => setActiveTab('stories')}
                  >
                    📋 User Stories ({artifact.user_stories.length})
                  </button>
                  <button
                    type="button"
                    className={`tab-btn ${activeTab === 'docs' ? 'tab-active' : ''}`}
                    onClick={() => setActiveTab('docs')}
                  >
                    📖 Documentation (README)
                  </button>
                </div>
              </div>

              {/* Tab 1: Code Viewer */}
              {activeTab === 'code' && (
                <div className="code-viewer-container panel">
                  {/* File Tabs */}
                  <div className="file-tabs-strip">
                    {artifact.code_files.map((file, idx) => {
                      const isActive = selectedFileIndex === idx;
                      const isTest = file.file_type === 'test';
                      return (
                        <button
                          key={file.filepath}
                          type="button"
                          className={`file-tab ${isActive ? 'file-tab-active' : ''}`}
                          onClick={() => setSelectedFileIndex(idx)}
                        >
                          <span className="file-icon">{isTest ? '🧪' : '📄'}</span>
                          <span className="file-name">{file.filepath}</span>
                        </button>
                      );
                    })}
                  </div>

                  {selectedFile && (
                    <div className="code-display-body">
                      <div className="code-meta-bar">
                        <span className="code-path">{selectedFile.filepath}</span>
                        <div className="code-actions">
                          {copyCodeSuccess && <span className="copy-success-tag">{copyCodeSuccess}</span>}
                          <button
                            type="button"
                            className="copy-btn-mini"
                            onClick={handleCopyFileContent}
                          >
                            Copy Code
                          </button>
                        </div>
                      </div>
                      <pre className="code-editor-pre">
                        <code>{selectedFile.content}</code>
                      </pre>
                    </div>
                  )}
                </div>
              )}

              {/* Tab 2: Test Suite & Console */}
              {activeTab === 'tests' && (
                <div className="tests-tab-content">
                  {/* Metrics Bar */}
                  <div className="test-metrics-grid">
                    <div className="metric-stat-card panel">
                      <span className="metric-label">Pass Rate</span>
                      <strong className="metric-val text-success">
                        {artifact.test_run.total > 0
                          ? Math.round((artifact.test_run.passed / artifact.test_run.total) * 100)
                          : 100}%
                      </strong>
                    </div>
                    <div className="metric-stat-card panel">
                      <span className="metric-label">Passed Tests</span>
                      <strong className="metric-val text-success">{artifact.test_run.passed}</strong>
                    </div>
                    <div className="metric-stat-card panel">
                      <span className="metric-label">Failed Tests</span>
                      <strong className={`metric-val ${artifact.test_run.failed > 0 ? 'text-danger' : ''}`}>
                        {artifact.test_run.failed}
                      </strong>
                    </div>
                    <div className="metric-stat-card panel">
                      <span className="metric-label">Branch Coverage</span>
                      <strong className="metric-val">{artifact.test_run.coverage_pct}%</strong>
                    </div>
                  </div>

                  {/* Individual Test Cases */}
                  {artifact.test_run.test_details?.length > 0 && (
                    <div className="panel test-items-card">
                      <div className="panel-heading">
                        <h3>Executed Test Cases</h3>
                      </div>
                      <div className="test-items-list">
                        {artifact.test_run.test_details.map((t, idx) => (
                          <div key={idx} className={`test-row-item test-${t.status}`}>
                            <div className="test-item-left">
                              <span className={`status-icon-dot ${t.status}`} />
                              <strong className="test-name-text">{t.test_name}</strong>
                            </div>
                            <div className="test-item-right">
                              <span className="duration-tag">{t.execution_time_ms}ms</span>
                              <span className={`test-status-pill pill-${t.status}`}>
                                {t.status.toUpperCase()}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Terminal Console Logs */}
                  <div className="panel verification-output-panel">
                    <div className="terminal-header">
                      <span className="terminal-dot red" />
                      <span className="terminal-dot yellow" />
                      <span className="terminal-dot green" />
                      <span className="terminal-title">Test Runner Sandbox Console</span>
                    </div>
                    <pre className="terminal-content">{artifact.test_run.stdout_logs}</pre>
                  </div>
                </div>
              )}

              {/* Tab 3: Architecture & Design */}
              {activeTab === 'architecture' && (
                <div className="architecture-tab-content">
                  <div className="panel arch-card">
                    <span className="eyebrow">Architectural Strategy</span>
                    <h3>{artifact.architecture.architecture_style}</h3>
                    <p className="arch-overview-text">{artifact.architecture.system_overview}</p>
                  </div>

                  <div className="components-grid">
                    {(artifact.architecture.components || []).map((comp, idx) => (
                      <div key={idx} className="panel component-card">
                        <div className="comp-card-header">
                          <span className="comp-badge">MODULE {idx + 1}</span>
                          <h4>{comp.name}</h4>
                        </div>
                        <p className="comp-resp">{comp.responsibility}</p>
                        <div className="methods-wrapper">
                          <span className="methods-label">Interface Methods:</span>
                          <ul className="methods-list">
                            {comp.interface_methods.map((m, midx) => (
                              <li key={midx}>
                                <code>{m}</code>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Tab 4: User Stories */}
              {activeTab === 'stories' && (
                <div className="stories-tab-content">
                  {(artifact.user_stories || []).map((story) => (
                    <div key={story.id} className="panel story-card">
                      <div className="story-card-header">
                        <div className="story-id-title">
                          <span className="story-id-pill">{story.id}</span>
                          <h3>{story.title}</h3>
                        </div>
                        <span className="priority-pill">{story.priority} Priority</span>
                      </div>

                      <div className="story-persona-box">
                        <p><strong>As a</strong> {story.as_a},</p>
                        <p><strong>I want</strong> {story.i_want},</p>
                        <p><strong>So that</strong> {story.so_that}.</p>
                      </div>

                      <div className="criteria-section">
                        <span className="criteria-label">Acceptance Criteria (Verified by Test Suite):</span>
                        <ul className="criteria-list">
                          {story.acceptance_criteria.map((crit, cidx) => (
                            <li key={cidx}>
                              <span className="crit-check">✓</span>
                              <span>{crit}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Tab 5: Documentation */}
              {activeTab === 'docs' && (
                <div className="panel docs-tab-content">
                  <div className="docs-header">
                    <span className="eyebrow">Generated Project Documentation</span>
                    <h3>README.md</h3>
                  </div>
                  <pre className="docs-pre">
                    <code>{artifact.documentation_markdown}</code>
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Sidebar: Saved Projects History */}
        <aside className="sdlc-history-sidebar">
          <div className="panel history-panel">
            <div className="panel-heading">
              <div>
                <span className="eyebrow">SDLC Persistence</span>
                <h3>Project Archive</h3>
              </div>
              <button
                type="button"
                className="refresh-btn"
                onClick={loadSavedProjects}
                title="Refresh history"
              >
                ↻
              </button>
            </div>

            {loadingProjects ? (
              <div className="history-loading">
                <span className="spinner-inline" /> Loading projects...
              </div>
            ) : savedProjects.length === 0 ? (
              <div className="history-empty">
                <p>No SDLC projects generated yet. Launch your first project above!</p>
              </div>
            ) : (
              <div className="history-list">
                {savedProjects.map((p) => {
                  const isActive = artifact?.id === p.id;
                  const dateStr = p.created_at
                    ? new Date(p.created_at).toLocaleDateString()
                    : 'Recent';

                  return (
                    <div
                      key={p.id}
                      className={`history-card ${isActive ? 'history-card-active' : ''}`}
                      onClick={() => handleLoadProject(p.id)}
                    >
                      <div className="history-card-header">
                        <strong className="history-topic" title={p.project_name}>
                          {p.project_name}
                        </strong>
                        <button
                          type="button"
                          className="history-delete-btn"
                          title="Delete project"
                          onClick={(e) => handleDeleteProject(e, p.id)}
                        >
                          ✕
                        </button>
                      </div>
                      <div className="history-meta">
                        <span className={`status-badge-pill status-${p.status === 'completed' ? 'remediated' : 'diagnosed'}`}>
                          {p.status}
                        </span>
                        <span className="history-date">{dateStr}</span>
                      </div>
                      <div className="history-cat-meta">
                        <small className="cat-text">{p.target_language} · {p.framework}</small>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
}
