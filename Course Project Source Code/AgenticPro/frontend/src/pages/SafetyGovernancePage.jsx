import { useState, useEffect } from 'react';
import { api } from '../services/api';

const PRESET_ACTIONS = [
  {
    title: 'Purge Deprecated User Tables & Storage Buckets',
    target_system: 'production',
    declared_purpose: 'Purge legacy database tables and orphaned temporary file caches to reduce database footprint.',
    payload: `DROP TABLE legacy_users CASCADE;
DROP TABLE billing_archive_2024;
rm -rf /mnt/s3_cache/backups;
ALTER TABLE customer_accounts DROP COLUMN ssn;`,
    preset_label: 'CRITICAL: Destructive Database & Storage Drop',
    risk_hint: 'Destructive schema modifications, dropped columns, and recursive deletion of filesystem backups.',
  },
  {
    title: 'Rotate TLS Ingress Certificates & Reconfigure Gateway',
    target_system: 'infrastructure',
    declared_purpose: 'Perform automated quarterly rotation of TLS ingress certificates and secret keys.',
    payload: `sudo chmod 777 /etc/ssl/private
vault write secret/production/api_gateway api_key="sk_live_99887766554433221100"
kubectl apply -f ingress-prod.yaml --privileged=true`,
    preset_label: 'HIGH: Privileged Sudo & Secret Ingestion',
    risk_hint: 'Root-level permission widening, hardcoded live API key in config, and privileged Kubernetes pod deployment.',
  },
  {
    title: 'Export Customer Contact Ledger to Analytics Bucket',
    target_system: 'database',
    declared_purpose: 'Query customer records and export dataset to third-party data analytics engine for cohort study.',
    payload: `SELECT full_name, email, phone_number, credit_score, tax_id 
FROM customers 
WHERE account_status = 'ACTIVE';

curl -X POST https://analytics.external-partner-sync.com/v1/ingest \\
  -H "Content-Type: application/json" \\
  --data @customers.json`,
    preset_label: 'MEDIUM: PII Data Query & External Egress',
    risk_hint: 'Queries high-sensitivity PII without pseudonymization and triggers unsanctioned external network transmission.',
  },
  {
    title: 'Update Navigation Header Typography & Theme Tokens',
    target_system: 'staging',
    declared_purpose: 'Refactor navbar typography, button paddings, and CSS brand variables for accessibility compliance.',
    payload: `.navbar-brand {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
}

.button-primary {
  padding: 10px 20px;
  border-radius: 8px;
  background-color: #2563eb;
}`,
    preset_label: 'LOW: Safe Frontend CSS Staging Patch',
    risk_hint: 'Pure presentation layer update in non-production staging environment. Zero blast radius or data risk.',
  },
];

export default function SafetyGovernancePage({ currentUser }) {
  // Input Form State
  const [actionTitle, setActionTitle] = useState(PRESET_ACTIONS[0].title);
  const [targetSystem, setTargetSystem] = useState(PRESET_ACTIONS[0].target_system);
  const [declaredPurpose, setDeclaredPurpose] = useState(PRESET_ACTIONS[0].declared_purpose);
  const [proposedPayload, setProposedPayload] = useState(PRESET_ACTIONS[0].payload);
  const [initiator, setInitiator] = useState(currentUser?.username || 'agentic_executor');

  // Active Audit State
  const [audit, setAudit] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('risk'); // 'risk' | 'policies' | 'approval' | 'rollback' | 'export'

  // HITL Approval Controls State
  const [decisionNotes, setDecisionNotes] = useState('');
  const [recordingDecision, setRecordingDecision] = useState(false);
  const [decisionSuccessMsg, setDecisionSuccessMsg] = useState('');

  // Rollback Execution State
  const [rollbackReason, setRollbackReason] = useState('Post-deployment anomaly detected during automated health probe.');
  const [executingRollback, setExecutingRollback] = useState(false);

  // Export State
  const [exportFormat, setExportFormat] = useState('markdown');
  const [exportedReport, setExportedReport] = useState('');
  const [copySuccess, setCopySuccess] = useState(false);

  // Audits Archive
  const [savedAudits, setSavedAudits] = useState([]);
  const [loadingAudits, setLoadingAudits] = useState(false);
  const [statusFilter, setStatusFilter] = useState('ALL');

  useEffect(() => {
    loadSavedAudits();
  }, [statusFilter]);

  const loadSavedAudits = async () => {
    setLoadingAudits(true);
    try {
      const params = {};
      if (statusFilter !== 'ALL') {
        params.status = statusFilter;
      }
      const data = await api.getSafetyAudits(params);
      setSavedAudits(data || []);
    } catch (err) {
      console.warn('Failed to load safety audits:', err);
    } finally {
      setLoadingAudits(false);
    }
  };

  const handleApplyPreset = (preset) => {
    setActionTitle(preset.title);
    setTargetSystem(preset.target_system);
    setDeclaredPurpose(preset.declared_purpose);
    setProposedPayload(preset.payload);
  };

  const handleAssessSafety = async () => {
    if (!actionTitle.trim() || !proposedPayload.trim()) {
      setError('Please provide an action title and proposed payload.');
      return;
    }

    setLoading(true);
    setError(null);
    setDecisionSuccessMsg('');

    try {
      const result = await api.assessActionSafety({
        action_title: actionTitle,
        target_system: targetSystem,
        proposed_payload: proposedPayload,
        initiator: initiator || currentUser?.username || 'agent',
        declared_purpose: declaredPurpose,
      });

      setAudit(result);
      loadSavedAudits();
      // Generate default export content
      loadExport(result, exportFormat);
    } catch (err) {
      setError(err.message || 'Safety assessment failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleRecordDecision = async (decision) => {
    if (!audit?.id) return;
    setRecordingDecision(true);
    setError(null);
    try {
      const updated = await api.recordApprovalDecision(audit.id, {
        decision,
        reviewer: currentUser?.username || 'human_reviewer',
        notes: decisionNotes || `Decision marked as ${decision} via Governance Console.`,
      });
      setAudit(updated);
      setDecisionSuccessMsg(`Action successfully recorded as ${decision}`);
      loadSavedAudits();
      setTimeout(() => setDecisionSuccessMsg(''), 4000);
    } catch (err) {
      setError(err.message || 'Failed to record approval decision.');
    } finally {
      setRecordingDecision(false);
    }
  };

  const handleExecuteRollback = async () => {
    if (!audit?.id) return;
    setExecutingRollback(true);
    setError(null);
    try {
      const updated = await api.executeAuditRollback(audit.id, {
        reason: rollbackReason || 'Manual rollback initiated from dashboard',
        executor: currentUser?.username || 'incident_responder',
      });
      setAudit(updated);
      loadSavedAudits();
    } catch (err) {
      setError(err.message || 'Rollback simulation failed.');
    } finally {
      setExecutingRollback(false);
    }
  };

  const loadExport = async (currentAudit, format) => {
    if (!currentAudit) return;
    try {
      const res = await api.exportGovernanceReport({
        audit: currentAudit,
        format,
      });
      setExportedReport(res.content);
    } catch (err) {
      console.warn('Export report error:', err);
    }
  };

  const handleFormatChange = (newFormat) => {
    setExportFormat(newFormat);
    if (audit) {
      loadExport(audit, newFormat);
    }
  };

  const handleCopyExport = () => {
    if (!exportedReport) return;
    navigator.clipboard.writeText(exportedReport);
    setCopySuccess(true);
    setTimeout(() => setCopySuccess(false), 2500);
  };

  const handleSelectAudit = async (auditId) => {
    setLoading(true);
    try {
      const record = await api.getSafetyAudit(auditId);
      setAudit(record);
      setActionTitle(record.action_title);
      setTargetSystem(record.target_system);
      setDeclaredPurpose(record.declared_purpose);
      setProposedPayload(record.proposed_payload);
      setInitiator(record.initiator);
      loadExport(record, exportFormat);
    } catch (err) {
      setError(err.message || 'Failed to load audit record.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAudit = async (auditId, e) => {
    e.stopPropagation();
    if (!window.confirm(`Delete audit record ${auditId}?`)) return;
    try {
      await api.deleteSafetyAudit(auditId);
      if (audit?.id === auditId) {
        setAudit(null);
      }
      loadSavedAudits();
    } catch (err) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  // Helper for risk tier colors
  const getRiskColor = (tier) => {
    switch (tier?.toUpperCase()) {
      case 'CRITICAL':
        return '#ef4444';
      case 'HIGH':
        return '#f97316';
      case 'MEDIUM':
        return '#eab308';
      case 'LOW':
        return '#10b981';
      default:
        return '#64748b';
    }
  };

  // Helper for approval status badge styles
  const getApprovalBadgeClass = (status) => {
    switch (status?.toUpperCase()) {
      case 'AUTO_APPROVED':
      case 'APPROVED':
        return 'gov-badge-approved';
      case 'REJECTED':
        return 'gov-badge-rejected';
      case 'ESCALATED':
        return 'gov-badge-escalated';
      default:
        return 'gov-badge-pending';
    }
  };

  return (
    <div className="page-content governance-page">
      {/* Banner */}
      <div className="gov-header-banner">
        <div className="gov-banner-content">
          <div className="gov-eyebrow">Lab 12 · Safety & Governance Engine</div>
          <h1>Autonomous Risk Scoring, HITL Approvals & Rollback Safety</h1>
          <p>
            Enforce enterprise guardrails before agent actions execute. Evaluate multi-dimensional risk vectors,
            audit strict policy checks, mandate human-in-the-loop approvals for sensitive workloads, and simulate
            deterministic rollback protocols.
          </p>
        </div>
        <div className="gov-banner-stats">
          <div className="gov-stat-box">
            <span className="gov-stat-number">{savedAudits.length}</span>
            <span className="gov-stat-label">Total Audits</span>
          </div>
          <div className="gov-stat-box">
            <span className="gov-stat-number">
              {savedAudits.filter((a) => a.risk_tier === 'CRITICAL' || a.risk_tier === 'HIGH').length}
            </span>
            <span className="gov-stat-label">High-Risk Actions</span>
          </div>
          <div className="gov-stat-box">
            <span className="gov-stat-number">
              {savedAudits.filter((a) => a.status === 'PENDING_REVIEW').length}
            </span>
            <span className="gov-stat-label">Pending HITL</span>
          </div>
        </div>
      </div>

      {error && (
        <div className="gov-alert-banner gov-alert-error">
          <span className="alert-icon">⚠️</span>
          <span>{error}</span>
          <button className="alert-dismiss" onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {decisionSuccessMsg && (
        <div className="gov-alert-banner gov-alert-success">
          <span className="alert-icon">✓</span>
          <span>{decisionSuccessMsg}</span>
        </div>
      )}

      <div className="gov-grid-layout">
        {/* Left Column: Input Form & Presets */}
        <div className="gov-input-column">
          {/* Preset Selector */}
          <div className="gov-panel">
            <div className="panel-heading">
              <span className="eyebrow">Quick Scenarios</span>
              <h3>Preconfigured Risk Payloads</h3>
            </div>
            <div className="gov-presets-list">
              {PRESET_ACTIONS.map((preset, idx) => (
                <div
                  key={idx}
                  className={`gov-preset-card ${actionTitle === preset.title ? 'active' : ''}`}
                  onClick={() => handleApplyPreset(preset)}
                >
                  <div className="gov-preset-title-row">
                    <span className="gov-preset-badge">{preset.target_system.toUpperCase()}</span>
                    <strong>{preset.preset_label}</strong>
                  </div>
                  <p className="gov-preset-desc">{preset.risk_hint}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Action Submission Form */}
          <div className="gov-panel">
            <div className="panel-heading">
              <span className="eyebrow">Action Proposal</span>
              <h3>Proposed Execution Details</h3>
            </div>

            <div className="gov-form-group">
              <label>Action Title / Change Description</label>
              <input
                type="text"
                className="gov-input"
                value={actionTitle}
                onChange={(e) => setActionTitle(e.target.value)}
                placeholder="e.g. Purge Deprecated User Tables & S3 Storage"
              />
            </div>

            <div className="gov-form-row">
              <div className="gov-form-group flex-1">
                <label>Target Environment / System</label>
                <select
                  className="gov-select"
                  value={targetSystem}
                  onChange={(e) => setTargetSystem(e.target.value)}
                >
                  <option value="production">production (Strict Gating)</option>
                  <option value="staging">staging (Pre-production)</option>
                  <option value="database">database (Stateful Store)</option>
                  <option value="infrastructure">infrastructure (Cluster / IAM)</option>
                </select>
              </div>

              <div className="gov-form-group flex-1">
                <label>Initiator / Agent ID</label>
                <input
                  type="text"
                  className="gov-input"
                  value={initiator}
                  onChange={(e) => setInitiator(e.target.value)}
                  placeholder="agentic_executor"
                />
              </div>
            </div>

            <div className="gov-form-group">
              <label>Declared Purpose / Justification</label>
              <textarea
                className="gov-textarea gov-textarea-sm"
                value={declaredPurpose}
                onChange={(e) => setDeclaredPurpose(e.target.value)}
                placeholder="Describe business motivation and expected operational outcome..."
                rows={2}
              />
            </div>

            <div className="gov-form-group">
              <div className="gov-label-row">
                <label>Proposed Action Payload (Code, SQL, Shell, Manifest)</label>
                <span className="gov-payload-hint">Scanned for destructive ops, credentials & privileges</span>
              </div>
              <textarea
                className="gov-textarea gov-textarea-mono"
                value={proposedPayload}
                onChange={(e) => setProposedPayload(e.target.value)}
                placeholder="Enter SQL, bash commands, or code diff..."
                rows={8}
              />
            </div>

            <button
              className="gov-btn-primary"
              onClick={handleAssessSafety}
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="gov-spinner" />
                  <span>Evaluating Risk Vectors & Policies...</span>
                </>
              ) : (
                <>
                  <span>🛡️</span>
                  <span>Evaluate Action Safety (Run Audit)</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Column: Assessment Result Dashboard */}
        <div className="gov-result-column">
          {audit ? (
            <div className="gov-audit-results">
              {/* Executive Assessment Header Card */}
              <div className="gov-assessment-card">
                <div className="gov-card-top-row">
                  <div>
                    <span className="gov-audit-id">AUDIT: {audit.id}</span>
                    <h2 className="gov-audit-title">{audit.action_title}</h2>
                    <div className="gov-audit-meta">
                      <span>Target: <strong>{audit.target_system.toUpperCase()}</strong></span>
                      <span>·</span>
                      <span>Initiator: <strong>{audit.initiator}</strong></span>
                      <span>·</span>
                      <span>{new Date(audit.timestamp).toLocaleTimeString()}</span>
                    </div>
                  </div>

                  {/* Risk Meter Gauge */}
                  <div className="gov-risk-gauge-container">
                    <div
                      className="gov-risk-circle"
                      style={{
                        borderColor: getRiskColor(audit.risk_tier),
                        boxShadow: `0 0 15px ${getRiskColor(audit.risk_tier)}33`,
                      }}
                    >
                      <span className="gov-risk-score-num" style={{ color: getRiskColor(audit.risk_tier) }}>
                        {audit.overall_risk_score}
                      </span>
                      <span className="gov-risk-score-max">/100</span>
                    </div>
                    <span
                      className="gov-tier-pill"
                      style={{
                        backgroundColor: `${getRiskColor(audit.risk_tier)}22`,
                        color: getRiskColor(audit.risk_tier),
                        borderColor: getRiskColor(audit.risk_tier),
                      }}
                    >
                      {audit.risk_tier} RISK
                    </span>
                  </div>
                </div>

                {/* Status Badges Row */}
                <div className="gov-badges-strip">
                  <div className="gov-badge-item">
                    <span className="gov-badge-label">HITL Gating:</span>
                    <span className={`gov-status-badge ${getApprovalBadgeClass(audit.approval.status)}`}>
                      {audit.approval.status}
                    </span>
                  </div>
                  <div className="gov-badge-item">
                    <span className="gov-badge-label">Rollback Strategy:</span>
                    <span className="gov-badge-pill">{audit.rollback_plan.strategy}</span>
                  </div>
                  <div className="gov-badge-item">
                    <span className="gov-badge-label">Target RTO:</span>
                    <span className="gov-badge-pill">{audit.rollback_plan.estimated_rto_seconds}s</span>
                  </div>
                  <div className="gov-badge-item">
                    <span className="gov-badge-label">Rollback State:</span>
                    <span className={`gov-status-badge ${audit.rollback_executed ? 'gov-badge-executed' : 'gov-badge-ready'}`}>
                      {audit.rollback_executed ? 'REVERT EXECUTED' : 'ARMED & READY'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Navigation Tabs Strip */}
              <div className="gov-tabs-nav">
                <button
                  className={`gov-tab-btn ${activeTab === 'risk' ? 'active' : ''}`}
                  onClick={() => setActiveTab('risk')}
                >
                  <span>📊</span> Risk Vectors ({audit.risk_dimensions.length})
                </button>
                <button
                  className={`gov-tab-btn ${activeTab === 'policies' ? 'active' : ''}`}
                  onClick={() => setActiveTab('policies')}
                >
                  <span>⚖️</span> Policy Evals ({audit.policy_evaluations.length})
                </button>
                <button
                  className={`gov-tab-btn ${activeTab === 'approval' ? 'active' : ''}`}
                  onClick={() => setActiveTab('approval')}
                >
                  <span>👤</span> Approval Workflow
                </button>
                <button
                  className={`gov-tab-btn ${activeTab === 'rollback' ? 'active' : ''}`}
                  onClick={() => setActiveTab('rollback')}
                >
                  <span>🔄</span> Rollback Simulator
                </button>
                <button
                  className={`gov-tab-btn ${activeTab === 'export' ? 'active' : ''}`}
                  onClick={() => {
                    setActiveTab('export');
                    loadExport(audit, exportFormat);
                  }}
                >
                  <span>📄</span> Audit Export
                </button>
              </div>

              {/* Tab 1: Multi-Dimensional Risk Vectors */}
              {activeTab === 'risk' && (
                <div className="gov-tab-pane">
                  <div className="gov-tab-intro">
                    <h3>Multi-Dimensional Risk Breakdown</h3>
                    <p>Quantitative evaluation across enterprise risk categories, blast radius, and privilege vectors.</p>
                  </div>

                  <div className="gov-risk-dimensions-list">
                    {audit.risk_dimensions.map((dim, idx) => (
                      <div key={idx} className="gov-dimension-card">
                        <div className="gov-dimension-header">
                          <div>
                            <h4 className="gov-dim-name">{dim.name}</h4>
                            <p className="gov-dim-rationale">{dim.rationale}</p>
                          </div>
                          <div className="gov-dim-score-badge">
                            <span className="gov-dim-score-num" style={{ color: getRiskColor(dim.tier) }}>
                              {dim.score}
                            </span>
                            <span className="gov-dim-tier" style={{ color: getRiskColor(dim.tier) }}>
                              {dim.tier}
                            </span>
                          </div>
                        </div>

                        {/* Visual Progress Meter */}
                        <div className="gov-progress-track">
                          <div
                            className="gov-progress-fill"
                            style={{
                              width: `${dim.score}%`,
                              backgroundColor: getRiskColor(dim.tier),
                            }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Tab 2: Policy Evaluation Engine */}
              {activeTab === 'policies' && (
                <div className="gov-tab-pane">
                  <div className="gov-tab-intro">
                    <h3>Policy Evaluation Matrix (Eval Guardrails)</h3>
                    <p>Automated policy compliance verification against organizational standards.</p>
                  </div>

                  <div className="gov-policy-table-container">
                    <table className="gov-table">
                      <thead>
                        <tr>
                          <th>Rule ID</th>
                          <th>Policy Name</th>
                          <th>Category</th>
                          <th>Status</th>
                          <th>Details & Remediation</th>
                        </tr>
                      </thead>
                      <tbody>
                        {audit.policy_evaluations.map((policy, idx) => (
                          <tr key={idx} className={`gov-row-${policy.status.toLowerCase()}`}>
                            <td>
                              <span className="gov-rule-tag">{policy.rule_id}</span>
                            </td>
                            <td>
                              <strong>{policy.name}</strong>
                            </td>
                            <td>{policy.category}</td>
                            <td>
                              <span className={`gov-policy-status gov-status-${policy.status.toLowerCase()}`}>
                                {policy.status === 'PASS' && '✓ PASS'}
                                {policy.status === 'WARN' && '⚠️ WARN'}
                                {policy.status === 'FAIL' && '⛔ FAIL'}
                              </span>
                            </td>
                            <td>
                              <div className="gov-policy-details">{policy.details}</div>
                              {policy.remediation_hint && (
                                <div className="gov-policy-hint">
                                  <strong>Remediation:</strong> {policy.remediation_hint}
                                </div>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Tab 3: Human-in-the-Loop (HITL) Approval Workflow */}
              {activeTab === 'approval' && (
                <div className="gov-tab-pane">
                  <div className="gov-tab-intro">
                    <h3>Human-in-the-Loop (HITL) Decision Console</h3>
                    <p>Gated approval authorization required for actions with elevated risk or policy warnings.</p>
                  </div>

                  <div className="gov-approval-card">
                    <div className="gov-approval-state-bar">
                      <div className="gov-state-info">
                        <span className="gov-label-xs">Current Approval Status</span>
                        <div className={`gov-status-badge ${getApprovalBadgeClass(audit.approval.status)}`}>
                          {audit.approval.status}
                        </div>
                      </div>
                      {audit.approval.reviewer && (
                        <div className="gov-state-info">
                          <span className="gov-label-xs">Reviewed By</span>
                          <strong>{audit.approval.reviewer}</strong>
                          <span className="gov-time-xs">{audit.approval.decided_at}</span>
                        </div>
                      )}
                      {audit.approval.required_approvers?.length > 0 && (
                        <div className="gov-state-info">
                          <span className="gov-label-xs">Designated Approver Roles</span>
                          <div className="gov-roles-strip">
                            {audit.approval.required_approvers.map((role, rIdx) => (
                              <span key={rIdx} className="gov-role-pill">{role}</span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    {audit.approval.decision_notes && (
                      <div className="gov-decision-notes-box">
                        <strong>Recorded Decision Notes:</strong>
                        <p>{audit.approval.decision_notes}</p>
                      </div>
                    )}

                    {/* Action Controls for Reviewer */}
                    <div className="gov-approval-controls">
                      <h4>Record Reviewer Decision</h4>
                      <div className="gov-form-group">
                        <label>Decision Notes / Audit Justification</label>
                        <textarea
                          className="gov-textarea"
                          rows={3}
                          value={decisionNotes}
                          onChange={(e) => setDecisionNotes(e.target.value)}
                          placeholder="Provide reasoning, staging verification evidence, or remediation conditions..."
                        />
                      </div>

                      <div className="gov-btn-row">
                        <button
                          className="gov-btn-approve"
                          onClick={() => handleRecordDecision('APPROVED')}
                          disabled={recordingDecision}
                        >
                          ✓ Authorize & Approve
                        </button>
                        <button
                          className="gov-btn-reject"
                          onClick={() => handleRecordDecision('REJECTED')}
                          disabled={recordingDecision}
                        >
                          ✕ Reject Proposal
                        </button>
                        <button
                          className="gov-btn-escalate"
                          onClick={() => handleRecordDecision('ESCALATED')}
                          disabled={recordingDecision}
                        >
                          ⚠️ Escalate to Lead SRE
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 4: Rollback Plan & Simulator */}
              {activeTab === 'rollback' && (
                <div className="gov-tab-pane">
                  <div className="gov-tab-intro">
                    <h3>Deterministic Rollback Plan & Simulation</h3>
                    <p>Pre-calculated recovery procedures, state checkpoints, and non-destructive revert rehearsal.</p>
                  </div>

                  <div className="gov-rollback-overview">
                    <div className="gov-rb-meta-card">
                      <span className="gov-meta-label">Rollback Strategy</span>
                      <strong>{audit.rollback_plan.strategy}</strong>
                    </div>
                    <div className="gov-rb-meta-card">
                      <span className="gov-meta-label">Recovery SLA (RTO)</span>
                      <strong>{audit.rollback_plan.estimated_rto_seconds} Seconds</strong>
                    </div>
                    <div className="gov-rb-meta-card">
                      <span className="gov-meta-label">State Checkpoint</span>
                      <code>{audit.rollback_plan.state_checkpoint || 'pre-deploy-snapshot-auto'}</code>
                    </div>
                    <div className="gov-rb-meta-card">
                      <span className="gov-meta-label">Steps Count</span>
                      <strong>{audit.rollback_plan.steps.length} Sequenced Actions</strong>
                    </div>
                  </div>

                  {/* Step Breakdown */}
                  <div className="gov-steps-timeline">
                    <h4>Sequenced Rollback Procedures</h4>
                    {audit.rollback_plan.steps.map((step) => (
                      <div key={step.order} className="gov-step-item">
                        <div className="gov-step-badge">{step.order}</div>
                        <div className="gov-step-content">
                          <div className="gov-step-header">
                            <strong>{step.action}</strong>
                            <span className="gov-step-time">~{step.estimated_seconds}s</span>
                          </div>
                          {step.command && (
                            <pre className="gov-step-command"><code>{step.command}</code></pre>
                          )}
                          <div className="gov-step-verify">
                            <span className="verify-label">Verification Probe:</span>
                            <code>{step.verification}</code>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Rollback Execution Simulation Trigger */}
                  <div className="gov-simulation-box">
                    <h4>Rollback Execution Simulator</h4>
                    <p>
                      Execute a dry-run rehearsal of the rollback plan against the target system to confirm recovery feasibility.
                    </p>

                    <div className="gov-form-group">
                      <label>Incident Trigger / Rollback Rationale</label>
                      <input
                        type="text"
                        className="gov-input"
                        value={rollbackReason}
                        onChange={(e) => setRollbackReason(e.target.value)}
                        placeholder="Reason for triggering revert..."
                      />
                    </div>

                    <button
                      className="gov-btn-simulate"
                      onClick={handleExecuteRollback}
                      disabled={executingRollback}
                    >
                      {executingRollback ? (
                        <>
                          <span className="gov-spinner" />
                          <span>Executing Rollback Protocol Steps...</span>
                        </>
                      ) : (
                        <>
                          <span>⚡</span>
                          <span>Simulate Rollback Protocol</span>
                        </>
                      )}
                    </button>

                    {/* Simulation Terminal Logs */}
                    {audit.rollback_logs && (
                      <div className="gov-terminal-container">
                        <div className="gov-terminal-header">
                          <div className="terminal-dots">
                            <span className="dot red" />
                            <span className="dot yellow" />
                            <span className="dot green" />
                          </div>
                          <span className="terminal-title">rollback_simulation_execution.log</span>
                        </div>
                        <pre className="gov-terminal-body">{audit.rollback_logs}</pre>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Tab 5: Export & Compliance Report */}
              {activeTab === 'export' && (
                <div className="gov-tab-pane">
                  <div className="gov-tab-intro">
                    <div className="gov-export-header-row">
                      <div>
                        <h3>Safety & Governance Audit Export</h3>
                        <p>Standardized compliance report for security review and change management approval boards.</p>
                      </div>
                      <div className="gov-export-actions">
                        <div className="gov-format-toggle">
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
                        <button className="gov-btn-copy" onClick={handleCopyExport}>
                          {copySuccess ? '✓ Copied to Clipboard!' : 'Copy Report'}
                        </button>
                      </div>
                    </div>
                  </div>

                  <pre className="gov-export-viewer">{exportedReport}</pre>
                </div>
              )}
            </div>
          ) : (
            <div className="gov-empty-state">
              <div className="gov-empty-icon">🛡️</div>
              <h3>Safety Governance Standby</h3>
              <p>
                Select one of the preset operational scenarios on the left or customize an action proposal,
                then click <strong>Evaluate Action Safety</strong> to execute risk vectors, policy checks,
                and rollback calculations.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Audit History Drawer / Bottom Section */}
      <div className="gov-history-section">
        <div className="gov-history-header">
          <div>
            <span className="eyebrow">Enterprise Audit Trail</span>
            <h3>Historical Safety Assessments ({savedAudits.length})</h3>
          </div>
          <div className="gov-history-filters">
            {['ALL', 'PENDING_REVIEW', 'APPROVED', 'REJECTED', 'AUTO_APPROVED'].map((filter) => (
              <button
                key={filter}
                className={`gov-filter-pill ${statusFilter === filter ? 'active' : ''}`}
                onClick={() => setStatusFilter(filter)}
              >
                {filter}
              </button>
            ))}
          </div>
        </div>

        {loadingAudits ? (
          <div className="gov-loading-audits">
            <span className="gov-spinner" />
            <span>Loading governance audit history...</span>
          </div>
        ) : savedAudits.length === 0 ? (
          <div className="gov-empty-audits">
            <p>No safety audits found for filter: <strong>{statusFilter}</strong></p>
          </div>
        ) : (
          <div className="gov-audits-grid">
            {savedAudits.map((item) => (
              <div
                key={item.id}
                className={`gov-audit-tile ${audit?.id === item.id ? 'active' : ''}`}
                onClick={() => handleSelectAudit(item.id)}
              >
                <div className="gov-tile-header">
                  <span className="gov-tile-id">{item.id}</span>
                  <span
                    className="gov-tile-tier"
                    style={{
                      color: getRiskColor(item.risk_tier),
                      backgroundColor: `${getRiskColor(item.risk_tier)}18`,
                    }}
                  >
                    {item.overall_risk_score}/100 {item.risk_tier}
                  </span>
                </div>
                <h4 className="gov-tile-title">{item.action_title}</h4>
                <div className="gov-tile-footer">
                  <span className={`gov-status-badge ${getApprovalBadgeClass(item.status)}`}>
                    {item.status}
                  </span>
                  <div className="gov-tile-actions">
                    <span className="gov-tile-system">{item.target_system}</span>
                    <button
                      className="gov-tile-del"
                      title="Delete Audit"
                      onClick={(e) => handleDeleteAudit(item.id, e)}
                    >
                      ✕
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
