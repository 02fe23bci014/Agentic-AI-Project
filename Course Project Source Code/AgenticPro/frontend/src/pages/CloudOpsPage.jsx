import { useState, useEffect } from 'react';
import { api } from '../services/api';

const PRESET_INCIDENTS = [
  {
    title: 'Kubernetes OOMKilled (Exit Code 137)',
    service_name: 'payment-gateway',
    environment: 'production',
    deployment_target: 'kubernetes',
    incident_type: 'OOMKilled',
    raw_logs: `[2026-11-13T10:14:02Z] Starting payment-gateway v2.4.0 on port 8000
[2026-11-13T10:14:05Z] Warmup completed: 240MB / 256MB allocated
[2026-11-13T10:14:07Z] Inbound transaction burst: 1,200 req/sec
[2026-11-13T10:14:08Z] memory cgroup out of memory: Kill process 142 (python) score 982 or sacrifice child
[2026-11-13T10:14:08Z] Killed process 142 (python) total-vm:492816kB, anon-rss:261884kB
[2026-11-13T10:14:09Z] Container payment-gateway terminated with exit code 137 (OOMKilled)`,
    deployment_config: `apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-gateway
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: payment-gateway
        image: internal-registry.corp/payment:v2.4.0
        resources:
          limits:
            memory: "256Mi"
            cpu: "500m"
          requests:
            memory: "128Mi"
            cpu: "250m"`,
  },
  {
    title: 'CrashLoopBackOff: Liveness Probe Timeout',
    service_name: 'checkout-service',
    environment: 'production',
    deployment_target: 'kubernetes',
    incident_type: 'CrashLoopBackOff',
    raw_logs: `[2026-11-13T09:30:00Z] Booting checkout-service...
[2026-11-13T09:30:02Z] Connecting to PostgreSQL cluster at postgres.db:5432...
[2026-11-13T09:30:03Z] Warning: Liveness probe failed: HTTP probe failed with statuscode: 503
[2026-11-13T09:30:05Z] Warning: Liveness probe failed: Get "http://10.244.2.14:8000/health": dial tcp 10.244.2.14:8000: connect: connection refused
[2026-11-13T09:30:06Z] Container checkout failed liveness probe, will be restarted
[2026-11-13T09:30:08Z] Back-off restarting failed container checkout in pod checkout-service-7f8d69788f-5xqk4`,
    deployment_config: `livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 2
  periodSeconds: 5
  failureThreshold: 2`,
  },
  {
    title: 'Socket Port Collision ([Errno 98] Address in use)',
    service_name: 'api-edge-proxy',
    environment: 'staging',
    deployment_target: 'kubernetes',
    incident_type: 'PortConflict',
    raw_logs: `[2026-11-13T08:12:11Z] Initializing edge proxy listener on 0.0.0.0:8080
[2026-11-13T08:12:12Z] Traceback (most recent call last):
  File "proxy/server.py", line 45, in bind_listener
    sock.bind(('0.0.0.0', 8080))
OSError: [Errno 98] Address already in use
[2026-11-13T08:12:12Z] Fatal error: failed to start proxy daemon. Exiting with status 1`,
    deployment_config: `ports:
  - containerPort: 8080
    hostPort: 8080`,
  },
  {
    title: 'Missing Production Secret (KeyError: DATABASE_URL)',
    service_name: 'auth-service',
    environment: 'production',
    deployment_target: 'kubernetes',
    incident_type: 'ConfigMissing',
    raw_logs: `[2026-11-13T07:45:00Z] Loading application settings...
[2026-11-13T07:45:01Z] Traceback (most recent call last):
  File "backend/config/settings.py", line 18, in <module>
    database_url = os.environ['DATABASE_URL']
  File "os.py", line 679, in __getitem__
KeyError: 'DATABASE_URL'
[2026-11-13T07:45:01Z] Container terminated immediately on startup.`,
    deployment_config: `env:
  - name: APP_ENV
    value: "production"`,
  },
];

export default function CloudOpsPage({ currentUser }) {
  // Input Form State
  const [serviceName, setServiceName] = useState('payment-gateway');
  const [environment, setEnvironment] = useState('production');
  const [deploymentTarget, setDeploymentTarget] = useState('kubernetes');
  const [incidentType, setIncidentType] = useState('OOMKilled');
  const [rawLogs, setRawLogs] = useState(PRESET_INCIDENTS[0].raw_logs);
  const [deploymentConfig, setDeploymentConfig] = useState(PRESET_INCIDENTS[0].deployment_config);

  // Diagnostic Results State
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('remediation'); // 'remediation' | 'patches' | 'verification' | 'guardrails'

  // Remediation Execution State
  const [remediating, setRemediating] = useState(false);
  const [remediationResult, setRemediationResult] = useState(null);

  // Saved Incidents Archive
  const [savedIncidents, setSavedIncidents] = useState([]);
  const [loadingIncidents, setLoadingIncidents] = useState(false);

  // Post-Mortem Export Modal
  const [exportModalOpen, setExportModalOpen] = useState(false);
  const [exportFormat, setExportFormat] = useState('markdown');
  const [exportContent, setExportContent] = useState('');
  const [exportLoading, setExportLoading] = useState(false);
  const [copySuccess, setCopySuccess] = useState('');

  useEffect(() => {
    loadSavedIncidents();
  }, []);

  const loadSavedIncidents = async () => {
    setLoadingIncidents(true);
    try {
      const data = await api.getIncidents();
      setSavedIncidents(data || []);
    } catch (err) {
      console.warn('Failed to load incident history:', err);
    } finally {
      setLoadingIncidents(false);
    }
  };

  const handleApplyPreset = (preset) => {
    setServiceName(preset.service_name);
    setEnvironment(preset.environment);
    setDeploymentTarget(preset.deployment_target);
    setIncidentType(preset.incident_type);
    setRawLogs(preset.raw_logs);
    setDeploymentConfig(preset.deployment_config);
  };

  const handleDiagnose = async () => {
    if (!serviceName.trim() || !rawLogs.trim()) {
      setError('Service name and deployment crash logs are required.');
      return;
    }

    setLoading(true);
    setError(null);
    setRemediationResult(null);

    try {
      const result = await api.diagnoseDeployment({
        service_name: serviceName.trim(),
        environment,
        deployment_target: deploymentTarget,
        raw_logs: rawLogs.trim(),
        deployment_config: deploymentConfig?.trim() || null,
        incident_type: incidentType || null,
        user_id: currentUser?.username || 'sre-engineer',
      });
      setReport(result);
      setActiveTab('remediation');
      loadSavedIncidents();
    } catch (err) {
      setError(err.message || 'Diagnosis generation failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadIncident = async (incidentId) => {
    setLoading(true);
    setError(null);
    setRemediationResult(null);
    try {
      const data = await api.getIncident(incidentId);
      setReport(data);
      setServiceName(data.service_name);
      setEnvironment(data.environment);
      setDeploymentTarget(data.deployment_target);
      setActiveTab('remediation');
    } catch (err) {
      setError(err.message || 'Failed to load incident.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteIncident = async (e, incidentId) => {
    e.stopPropagation();
    if (!window.confirm('Delete this incident report?')) return;
    try {
      await api.deleteIncident(incidentId);
      setSavedIncidents((prev) => prev.filter((i) => i.id !== incidentId));
      if (report?.id === incidentId) {
        setReport(null);
        setRemediationResult(null);
      }
    } catch (err) {
      alert(`Could not delete incident: ${err.message}`);
    }
  };

  const handleApplyRemediation = async () => {
    if (!report) return;
    setRemediating(true);
    try {
      const res = await api.applyIncidentRemediation(report.id, { auto_restart: true });
      setRemediationResult(res);
      setReport((prev) => ({ ...prev, status: 'remediated' }));
      loadSavedIncidents();
    } catch (err) {
      alert(`Failed to apply remediation: ${err.message}`);
    } finally {
      setRemediating(false);
    }
  };

  const handleOpenExport = async (format) => {
    if (!report) return;
    setExportFormat(format);
    setExportLoading(true);
    setExportModalOpen(true);
    setCopySuccess('');

    try {
      const res = await api.exportPostmortem({
        report,
        format,
      });
      setExportContent(res.content || '');
    } catch (err) {
      setExportContent(`Export error: ${err.message}`);
    } finally {
      setExportLoading(false);
    }
  };

  const handleCopyExport = () => {
    if (!exportContent) return;
    navigator.clipboard.writeText(exportContent);
    setCopySuccess('Copied to clipboard!');
    setTimeout(() => setCopySuccess(''), 3000);
  };

  const handleDownloadMarkdown = () => {
    if (!exportContent) return;
    const blob = new Blob([exportContent], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `postmortem-${report?.service_name || 'incident'}.md`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="page-content cloud-ops-page">
      {/* Top Banner */}
      <div className="welcome-banner cloud-ops-banner">
        <div className="welcome-text">
          <div className="eyebrow">Lab Component 10</div>
          <h1>Cloud Operations Agent · Failed Deployment Diagnosis & Fix</h1>
          <p>
            Autonomous Site Reliability Engineering (SRE) and DevOps diagnosis.
            Ingests crash logs, determines Root Cause Analysis (RCA), generates unified diff patches,
            and simulates verified rolling redeployments.
          </p>
        </div>
        <div className="welcome-stats">
          <div className="welcome-stat-pill">
            <span className="pill-num">{savedIncidents.length}</span>
            <span className="pill-label">Logged Incidents</span>
          </div>
          <div className="welcome-stat-pill">
            <span className="pill-num">
              {savedIncidents.filter((i) => i.status === 'remediated').length}
            </span>
            <span className="pill-label">Remediated</span>
          </div>
        </div>
      </div>

      {/* Main Grid: Left Diagnostic Workspace, Right History */}
      <div className="cloud-ops-layout-grid">
        <div className="cloud-ops-main-column">
          {/* Incident Ingestion Card */}
          <div className="panel cloud-ops-input-panel">
            <div className="panel-heading">
              <div>
                <span className="eyebrow">Incident Ingestion</span>
                <h3>Deployment Failure & Crash Signature</h3>
              </div>
              <span className="status-tag active">Autonomous DevOps SRE</span>
            </div>

            {/* Presets Row */}
            <div className="preset-incidents-wrapper">
              <span className="samples-label">Load Simulated Cloud Failures:</span>
              <div className="preset-chips-row">
                {PRESET_INCIDENTS.map((preset, idx) => (
                  <button
                    key={idx}
                    type="button"
                    className="sample-chip preset-chip"
                    onClick={() => handleApplyPreset(preset)}
                  >
                    ⚡ {preset.title}
                  </button>
                ))}
              </div>
            </div>

            {/* Metadata Inputs */}
            <div className="cloud-ops-meta-row">
              <div className="config-item">
                <label className="config-label">Failing Service Name</label>
                <input
                  type="text"
                  className="modern-text-input"
                  value={serviceName}
                  onChange={(e) => setServiceName(e.target.value)}
                  placeholder="e.g. payment-gateway"
                />
              </div>

              <div className="config-item">
                <label className="config-label">Target Environment</label>
                <select
                  className="modern-select"
                  value={environment}
                  onChange={(e) => setEnvironment(e.target.value)}
                >
                  <option value="production">Production (Live)</option>
                  <option value="staging">Staging / Pre-Prod</option>
                  <option value="development">Development / Sandbox</option>
                </select>
              </div>

              <div className="config-item">
                <label className="config-label">Deployment Target</label>
                <select
                  className="modern-select"
                  value={deploymentTarget}
                  onChange={(e) => setDeploymentTarget(e.target.value)}
                >
                  <option value="kubernetes">Kubernetes (k8s)</option>
                  <option value="docker-compose">Docker Compose</option>
                  <option value="aws-ecs">AWS ECS / Fargate</option>
                  <option value="cloud-run">Google Cloud Run</option>
                </select>
              </div>

              <div className="config-item">
                <label className="config-label">Failure Hint (Optional)</label>
                <select
                  className="modern-select"
                  value={incidentType}
                  onChange={(e) => setIncidentType(e.target.value)}
                >
                  <option value="OOMKilled">OOMKilled (Exit Code 137)</option>
                  <option value="CrashLoopBackOff">CrashLoopBackOff / Probe Timeout</option>
                  <option value="PortConflict">Port Conflict (Address in Use)</option>
                  <option value="ConfigMissing">Missing Config / Secret</option>
                  <option value="Auto">Auto-Detect from Crash Logs</option>
                </select>
              </div>
            </div>

            {/* Log & Config Inputs */}
            <div className="log-input-grid">
              <div className="log-input-column">
                <label className="config-label">Raw Deployment Crash Logs & Stack Dumps</label>
                <textarea
                  className="code-textarea"
                  rows={8}
                  placeholder="Paste container logs, stderr, or CI/CD output here..."
                  value={rawLogs}
                  onChange={(e) => setRawLogs(e.target.value)}
                />
              </div>

              <div className="log-input-column">
                <label className="config-label">Current Configuration / Manifest (Optional)</label>
                <textarea
                  className="code-textarea"
                  rows={8}
                  placeholder="Paste current deployment.yaml, Dockerfile, or configmap..."
                  value={deploymentConfig}
                  onChange={(e) => setDeploymentConfig(e.target.value)}
                />
              </div>
            </div>

            <div className="action-submit-row">
              <button
                type="button"
                className="primary-button diagnose-btn"
                onClick={handleDiagnose}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner-inline" /> Diagnosing Incident...
                  </>
                ) : (
                  'Diagnose & Generate Remediation Fix →'
                )}
              </button>
            </div>

            {error && (
              <div className="alert-box alert-error">
                <strong>Diagnosis Error:</strong> {error}
              </div>
            )}
          </div>

          {/* Diagnostic Report Results */}
          {report && (
            <div className="diagnostic-results-wrapper">
              {/* Root Cause Analysis (RCA) Card */}
              <div className="panel rca-card">
                <div className="rca-header">
                  <div>
                    <div className="rca-meta-tags">
                      <span className={`severity-badge sev-${report.rca.severity.toLowerCase()}`}>
                        {report.rca.severity} SEVERITY
                      </span>
                      <span className="category-pill">{report.rca.error_category}</span>
                      <span className={`status-badge-pill status-${report.status}`}>
                        {report.status.toUpperCase()}
                      </span>
                    </div>
                    <h2 className="rca-title">Root Cause Analysis (RCA)</h2>
                  </div>

                  <div className="rca-actions">
                    <button
                      type="button"
                      className="primary-button apply-fix-btn"
                      onClick={handleApplyRemediation}
                      disabled={remediating || report.status === 'remediated'}
                    >
                      {remediating ? (
                        <>
                          <span className="spinner-inline" /> Verifying...
                        </>
                      ) : report.status === 'remediated' ? (
                        '✓ Remediation Applied & Verified'
                      ) : (
                        '⚡ Apply Automated Remediation'
                      )}
                    </button>
                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() => handleOpenExport('markdown')}
                    >
                      Export Post-Mortem
                    </button>
                  </div>
                </div>

                <p className="rca-summary-text">{report.rca.summary}</p>

                <div className="rca-details-grid">
                  <div className="rca-detail-box">
                    <span className="detail-label">Failing Service</span>
                    <strong className="detail-value">{report.rca.failing_service}</strong>
                  </div>
                  <div className="rca-detail-box">
                    <span className="detail-label">Triggering Signal / Signal</span>
                    <strong className="detail-value mono-val">{report.rca.triggering_event}</strong>
                  </div>
                  <div className="rca-detail-box">
                    <span className="detail-label">Affected Dependencies</span>
                    <div className="dep-tags-row">
                      {(report.rca.affected_dependencies || []).map((dep, i) => (
                        <span key={i} className="dep-tag">
                          {dep}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Remediation Applied Verification Terminal Output */}
              {remediationResult && (
                <div className="panel verification-output-panel">
                  <div className="terminal-header">
                    <span className="terminal-dot red" />
                    <span className="terminal-dot yellow" />
                    <span className="terminal-dot green" />
                    <span className="terminal-title">
                      Live Remediation Rollout & Probe Verification Log
                    </span>
                  </div>
                  <pre className="terminal-content">{remediationResult.verification_logs}</pre>
                </div>
              )}

              {/* Navigation Tabs for Details */}
              <div className="results-top-nav">
                <div className="results-tabs">
                  <button
                    type="button"
                    className={`tab-btn ${activeTab === 'remediation' ? 'tab-active' : ''}`}
                    onClick={() => setActiveTab('remediation')}
                  >
                    🛠️ Remediation Plan ({report.remediation_steps?.length || 0})
                  </button>
                  <button
                    type="button"
                    className={`tab-btn ${activeTab === 'patches' ? 'tab-active' : ''}`}
                    onClick={() => setActiveTab('patches')}
                  >
                    🔧 Patches & Unified Diffs ({report.patches?.length || 0})
                  </button>
                  <button
                    type="button"
                    className={`tab-btn ${activeTab === 'verification' ? 'tab-active' : ''}`}
                    onClick={() => setActiveTab('verification')}
                  >
                    ✅ Verification Probes ({report.verification_steps?.length || 0})
                  </button>
                  <button
                    type="button"
                    className={`tab-btn ${activeTab === 'guardrails' ? 'tab-active' : ''}`}
                    onClick={() => setActiveTab('guardrails')}
                  >
                    🛡️ Preventive Guardrails
                  </button>
                </div>
              </div>

              {/* Tab 1: Remediation Steps */}
              {activeTab === 'remediation' && (
                <div className="remediation-steps-list">
                  {(report.remediation_steps || []).map((step) => (
                    <div key={step.step_number} className="panel step-card">
                      <div className="step-card-header">
                        <div className="step-num-title">
                          <span className="step-number-badge">STEP {step.step_number}</span>
                          <h4 className="step-action-title">{step.action}</h4>
                        </div>
                        <div className="step-meta-pills">
                          <span className={`risk-pill risk-${step.risk_level.toLowerCase()}`}>
                            Risk: {step.risk_level}
                          </span>
                          {step.is_automated && (
                            <span className="automated-pill">⚡ Auto-Executable</span>
                          )}
                        </div>
                      </div>

                      <p className="step-explanation">{step.explanation}</p>

                      {step.command_or_snippet && (
                        <div className="command-box">
                          <pre className="command-pre">
                            <code>{step.command_or_snippet}</code>
                          </pre>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Tab 2: Patches and Unified Diffs */}
              {activeTab === 'patches' && (
                <div className="patches-list">
                  {(report.patches || []).map((patch, idx) => (
                    <div key={idx} className="panel patch-card">
                      <div className="patch-card-header">
                        <div>
                          <span className="eyebrow">Remediation Patch Artifact</span>
                          <h4>{patch.filename}</h4>
                        </div>
                        <span className="file-type-pill">{patch.file_type.toUpperCase()}</span>
                      </div>

                      {patch.diff_patch ? (
                        <div className="diff-view-box">
                          <div className="diff-label">Unified Diff Patch</div>
                          <pre className="diff-pre">
                            {patch.diff_patch.split('\n').map((line, lidx) => {
                              const isAdd = line.startsWith('+') && !line.startsWith('+++');
                              const isDel = line.startsWith('-') && !line.startsWith('---');
                              const isHeader = line.startsWith('@@') || line.startsWith('---') || line.startsWith('+++');
                              return (
                                <div
                                  key={lidx}
                                  className={`diff-line ${isAdd ? 'diff-add' : isDel ? 'diff-del' : isHeader ? 'diff-hdr' : ''}`}
                                >
                                  {line}
                                </div>
                              );
                            })}
                          </pre>
                        </div>
                      ) : (
                        <div className="split-patch-grid">
                          <div>
                            <span className="config-label">Original Snippet</span>
                            <pre className="code-pre">{patch.original_snippet}</pre>
                          </div>
                          <div>
                            <span className="config-label">Patched Snippet</span>
                            <pre className="code-pre patched-pre">{patch.patched_snippet}</pre>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Tab 3: Verification Probes */}
              {activeTab === 'verification' && (
                <div className="panel verification-card">
                  <div className="panel-heading">
                    <div>
                      <span className="eyebrow">Quality Gate</span>
                      <h3>Deployment Health & Stability Probes</h3>
                    </div>
                  </div>
                  <ul className="verification-checklist">
                    {(report.verification_steps || []).map((step, idx) => (
                      <li key={idx} className="check-item">
                        <span className="check-icon">✓</span>
                        <span className="check-text">{step}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Tab 4: Preventive Recommendations */}
              {activeTab === 'guardrails' && (
                <div className="panel guardrails-card">
                  <div className="panel-heading">
                    <div>
                      <span className="eyebrow">Continuous Reliability</span>
                      <h3>Preventive SRE Guardrails</h3>
                    </div>
                  </div>
                  <ul className="guardrails-list">
                    {(report.preventive_recommendations || []).map((rec, idx) => (
                      <li key={idx} className="guardrail-item">
                        <span className="guardrail-num">#{idx + 1}</span>
                        <span className="guardrail-text">{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Column: Saved Incident Reports History */}
        <aside className="cloud-ops-sidebar">
          <div className="panel history-panel">
            <div className="panel-heading">
              <div>
                <span className="eyebrow">Persistence</span>
                <h3>Incident History</h3>
              </div>
              <button
                type="button"
                className="refresh-btn"
                onClick={loadSavedIncidents}
                title="Refresh history"
              >
                ↻
              </button>
            </div>

            {loadingIncidents ? (
              <div className="history-loading">
                <span className="spinner-inline" /> Loading incidents...
              </div>
            ) : savedIncidents.length === 0 ? (
              <div className="history-empty">
                <p>No logged deployment failures yet. Diagnose a test failure above!</p>
              </div>
            ) : (
              <div className="history-list">
                {savedIncidents.map((inc) => {
                  const isActive = report?.id === inc.id;
                  const dateStr = inc.created_at
                    ? new Date(inc.created_at).toLocaleDateString()
                    : 'Recent';

                  return (
                    <div
                      key={inc.id}
                      className={`history-card ${isActive ? 'history-card-active' : ''}`}
                      onClick={() => handleLoadIncident(inc.id)}
                    >
                      <div className="history-card-header">
                        <strong className="history-topic" title={inc.service_name}>
                          {inc.service_name}
                        </strong>
                        <button
                          type="button"
                          className="history-delete-btn"
                          title="Delete incident"
                          onClick={(e) => handleDeleteIncident(e, inc.id)}
                        >
                          ✕
                        </button>
                      </div>
                      <div className="history-meta">
                        <span className={`status-badge-pill status-${inc.status}`}>
                          {inc.status}
                        </span>
                        <span className="history-date">{dateStr}</span>
                      </div>
                      <div className="history-cat-meta">
                        <small className="cat-text">{inc.error_category}</small>
                        <small className={`sev-text sev-${inc.severity.toLowerCase()}`}>
                          {inc.severity}
                        </small>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </aside>
      </div>

      {/* Export Post-Mortem Modal */}
      {exportModalOpen && (
        <div className="modal-backdrop" onClick={() => setExportModalOpen(false)}>
          <div className="modal-card export-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Export Post-Mortem Incident Report ({exportFormat.toUpperCase()})</h3>
              <button
                type="button"
                className="modal-close"
                onClick={() => setExportModalOpen(false)}
              >
                ✕
              </button>
            </div>

            <div className="modal-body">
              {exportLoading ? (
                <div className="loading-state">
                  <div className="spinner" />
                  <span>Generating post-mortem documentation...</span>
                </div>
              ) : (
                <div className="export-preview-container">
                  <textarea
                    readOnly
                    className="export-code-block"
                    value={exportContent}
                    rows={12}
                  />
                  {copySuccess && <div className="copy-toast">{copySuccess}</div>}
                </div>
              )}
            </div>

            <div className="modal-footer">
              {exportFormat === 'markdown' && (
                <button
                  type="button"
                  className="secondary-button"
                  onClick={handleDownloadMarkdown}
                  disabled={exportLoading}
                >
                  Download .MD
                </button>
              )}
              <button
                type="button"
                className="primary-button"
                onClick={handleCopyExport}
                disabled={exportLoading}
              >
                Copy to Clipboard
              </button>
              <button
                type="button"
                className="ghost-button"
                onClick={() => setExportModalOpen(false)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
