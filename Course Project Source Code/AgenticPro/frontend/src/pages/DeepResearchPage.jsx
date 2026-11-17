import { useState, useEffect } from 'react';
import { api } from '../services/api';

const SAMPLE_TOPICS = [
  'Docker Sandboxing vs Firecracker MicroVMs in Code Execution',
  'Distributed Consensus: Raft vs Multi-Paxos Latency & Correctness',
  'Vector Database Indexing: HNSW vs IVF Graph Traversal Tradeoffs',
  'B-Tree vs LSM-Tree Write Amplification & Storage Engines',
  'eBPF Observability & Kernel-Level Security Monitoring',
];

const PRESET_FOCUS_AREAS = [
  'Latency & Overhead',
  'Fault Tolerance',
  'Memory Footprint',
  'Security & Isolation',
  'Throughput Scaling',
  'Storage IOPS',
];

export default function DeepResearchPage({ currentUser }) {
  // Query Form State
  const [topic, setTopic] = useState('');
  const [depth, setDepth] = useState('deep');
  const [selectedFocus, setSelectedFocus] = useState(['Latency & Overhead', 'Fault Tolerance']);
  const [customFocus, setCustomFocus] = useState('');
  const [maxSources, setMaxSources] = useState(5);

  // Results State
  const [briefing, setBriefing] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('briefing'); // 'briefing' | 'evidence' | 'tradeoffs'

  // Evidence Table Search & Filter
  const [evidenceFilter, setEvidenceFilter] = useState('');
  const [credibilityFilter, setCredibilityFilter] = useState('ALL');

  // Export State
  const [exportModalOpen, setExportModalOpen] = useState(false);
  const [exportFormat, setExportFormat] = useState('markdown');
  const [exportContent, setExportContent] = useState('');
  const [exportLoading, setExportLoading] = useState(false);
  const [copySuccess, setCopySuccess] = useState('');

  // Saved Reports History
  const [savedReports, setSavedReports] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  useEffect(() => {
    loadSavedReports();
  }, []);

  const loadSavedReports = async () => {
    setLoadingHistory(true);
    try {
      const reports = await api.getResearchReports();
      setSavedReports(reports || []);
    } catch (err) {
      console.warn('Failed to fetch research reports:', err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleRunResearch = async (overrideTopic) => {
    const targetTopic = (overrideTopic || topic).trim();
    if (!targetTopic) {
      setError('Please provide a research topic or select one of the suggested inquiries.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const result = await api.runResearch({
        topic: targetTopic,
        depth: depth,
        focus_areas: selectedFocus,
        max_sources: parseInt(maxSources, 10),
        student_or_user_id: currentUser?.username || 'researcher',
      });
      setBriefing(result);
      setActiveTab('briefing');
      loadSavedReports();
    } catch (err) {
      setError(err.message || 'Research agent execution failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadReport = async (reportId) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getResearchReport(reportId);
      setBriefing(data);
      setTopic(data.topic || '');
      setActiveTab('briefing');
    } catch (err) {
      setError(err.message || 'Failed to load report.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteReport = async (e, reportId) => {
    e.stopPropagation();
    if (!window.confirm('Delete this research report?')) return;
    try {
      await api.deleteResearchReport(reportId);
      setSavedReports((prev) => prev.filter((r) => r.id !== reportId));
      if (briefing?.id === reportId) {
        setBriefing(null);
      }
    } catch (err) {
      alert(`Could not delete report: ${err.message}`);
    }
  };

  const toggleFocus = (item) => {
    setSelectedFocus((prev) =>
      prev.includes(item) ? prev.filter((f) => f !== item) : [...prev, item]
    );
  };

  const handleAddCustomFocus = (e) => {
    if (e.key === 'Enter' && customFocus.trim()) {
      e.preventDefault();
      if (!selectedFocus.includes(customFocus.trim())) {
        setSelectedFocus([...selectedFocus, customFocus.trim()]);
      }
      setCustomFocus('');
    }
  };

  const handleOpenExport = async (format) => {
    if (!briefing || !briefing.evidence_table) return;
    setExportFormat(format);
    setExportLoading(true);
    setExportModalOpen(true);
    setCopySuccess('');

    try {
      const res = await api.exportEvidence({
        evidence: briefing.evidence_table,
        format: format,
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

  const handleDownloadCsv = () => {
    if (!exportContent) return;
    const blob = new Blob([exportContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `evidence-${briefing?.id || 'export'}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Filter evidence
  const filteredEvidence = (briefing?.evidence_table || []).filter((item) => {
    const matchesText =
      !evidenceFilter ||
      item.claim?.toLowerCase().includes(evidenceFilter.toLowerCase()) ||
      item.source?.toLowerCase().includes(evidenceFilter.toLowerCase()) ||
      item.evidence_quote?.toLowerCase().includes(evidenceFilter.toLowerCase()) ||
      item.metric?.toLowerCase().includes(evidenceFilter.toLowerCase());

    const matchesCred =
      credibilityFilter === 'ALL' ||
      item.credibility?.toLowerCase() === credibilityFilter.toLowerCase();

    return matchesText && matchesCred;
  });

  return (
    <div className="page-content deep-research-page">
      {/* Top Banner */}
      <div className="welcome-banner research-banner">
        <div className="welcome-text">
          <div className="eyebrow">Lab Component 9</div>
          <h1>Deep Research Agent & Evidence Synthesis</h1>
          <p>
            Autonomous literature review, empirical evidence extraction, and executive technical briefings.
            Formulates verifiable claims, quantifies performance metrics, and compiles publication-grade evidence tables.
          </p>
        </div>
        <div className="welcome-stats">
          <div className="welcome-stat-pill">
            <span className="pill-num">{briefing?.evidence_table?.length || 0}</span>
            <span className="pill-label">Active Evidence</span>
          </div>
          <div className="welcome-stat-pill">
            <span className="pill-num">{savedReports.length}</span>
            <span className="pill-label">Saved Briefings</span>
          </div>
        </div>
      </div>

      {/* Main Grid: Left Inquiry Workspace, Right History Drawer */}
      <div className="research-layout-grid">
        {/* Left Column: Research Prompt & Content */}
        <div className="research-main-column">
          {/* Inquiry Input Card */}
          <div className="panel research-query-panel">
            <div className="panel-heading">
              <div>
                <span className="eyebrow">Technical Inquiry</span>
                <h3>Target Research Topic</h3>
              </div>
              <span className="status-tag active">Autonomous Agent</span>
            </div>

            <div className="research-input-row">
              <input
                type="text"
                className="research-topic-input"
                placeholder="e.g. Distributed Consensus: Raft vs Paxos Latency & Correctness..."
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleRunResearch()}
              />
              <button
                type="button"
                className="primary-button execute-research-btn"
                onClick={() => handleRunResearch()}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner-inline" /> Synthesizing...
                  </>
                ) : (
                  'Run Deep Research Agent →'
                )}
              </button>
            </div>

            {/* Quick Suggestions Chips */}
            <div className="sample-topics-wrapper">
              <span className="samples-label">Suggested Inquiry Topics:</span>
              <div className="sample-chips-row">
                {SAMPLE_TOPICS.map((sample, idx) => (
                  <button
                    key={idx}
                    type="button"
                    className="sample-chip"
                    onClick={() => {
                      setTopic(sample);
                      handleRunResearch(sample);
                    }}
                  >
                    {sample}
                  </button>
                ))}
              </div>
            </div>

            {/* Configuration Controls */}
            <div className="research-config-row">
              <div className="config-item">
                <label className="config-label">Inquiry Depth</label>
                <select
                  className="modern-select"
                  value={depth}
                  onChange={(e) => setDepth(e.target.value)}
                >
                  <option value="overview">Executive Overview (Fast)</option>
                  <option value="standard">Standard Engineering Briefing</option>
                  <option value="deep">Comprehensive Deep-Dive (Exhaustive)</option>
                </select>
              </div>

              <div className="config-item">
                <label className="config-label">Max Evidence Sources: {maxSources}</label>
                <input
                  type="range"
                  min="2"
                  max="10"
                  value={maxSources}
                  onChange={(e) => setMaxSources(e.target.value)}
                  className="range-slider"
                />
              </div>

              <div className="config-item full-width-item">
                <label className="config-label">Focus Areas & Facets</label>
                <div className="focus-tags-row">
                  {PRESET_FOCUS_AREAS.map((facet) => (
                    <button
                      key={facet}
                      type="button"
                      className={`focus-pill ${selectedFocus.includes(facet) ? 'focus-active' : ''}`}
                      onClick={() => toggleFocus(facet)}
                    >
                      {selectedFocus.includes(facet) ? '✓ ' : '+ '}
                      {facet}
                    </button>
                  ))}
                  <input
                    type="text"
                    className="custom-focus-input"
                    placeholder="Type custom focus & press Enter..."
                    value={customFocus}
                    onChange={(e) => setCustomFocus(e.target.value)}
                    onKeyDown={handleAddCustomFocus}
                  />
                </div>
              </div>
            </div>

            {error && (
              <div className="alert-box alert-error">
                <strong>Inquiry Error:</strong> {error}
              </div>
            )}
          </div>

          {/* Results Workspace */}
          {briefing && (
            <div className="research-results-container">
              {/* Navigation Tabs & Actions */}
              <div className="results-top-nav">
                <div className="results-tabs">
                  <button
                    type="button"
                    className={`tab-btn ${activeTab === 'briefing' ? 'tab-active' : ''}`}
                    onClick={() => setActiveTab('briefing')}
                  >
                    📄 Topic Briefing
                  </button>
                  <button
                    type="button"
                    className={`tab-btn ${activeTab === 'evidence' ? 'tab-active' : ''}`}
                    onClick={() => setActiveTab('evidence')}
                  >
                    📊 Evidence Table ({briefing.evidence_table?.length || 0})
                  </button>
                  <button
                    type="button"
                    className={`tab-btn ${activeTab === 'tradeoffs' ? 'tab-active' : ''}`}
                    onClick={() => setActiveTab('tradeoffs')}
                  >
                    ⚖️ Tradeoffs & Comparisons
                  </button>
                </div>

                <div className="export-actions-row">
                  <span className="export-label">Export Evidence:</span>
                  <button
                    type="button"
                    className="action-btn-pill"
                    onClick={() => handleOpenExport('markdown')}
                  >
                    Markdown
                  </button>
                  <button
                    type="button"
                    className="action-btn-pill"
                    onClick={() => handleOpenExport('csv')}
                  >
                    CSV
                  </button>
                  <button
                    type="button"
                    className="action-btn-pill"
                    onClick={() => handleOpenExport('json')}
                  >
                    JSON
                  </button>
                </div>
              </div>

              {/* Tab 1: AI Topic Briefing */}
              {activeTab === 'briefing' && (
                <div className="briefing-tab-content">
                  {/* Executive Summary */}
                  <div className="panel briefing-card">
                    <div className="briefing-card-header">
                      <span className="eyebrow">Executive Summary</span>
                      <span className="report-id-tag">ID: {briefing.id}</span>
                    </div>
                    <p className="executive-summary-text">{briefing.executive_summary}</p>
                  </div>

                  {/* Key Findings */}
                  <div className="panel briefing-card">
                    <div className="briefing-card-header">
                      <span className="eyebrow">Systematic Findings</span>
                      <h3>Key Technical Conclusions</h3>
                    </div>
                    <div className="findings-grid">
                      {(briefing.key_findings || []).map((finding, idx) => (
                        <div className="finding-item" key={idx}>
                          <span className="finding-badge">#{idx + 1}</span>
                          <p className="finding-text">{finding}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Technical Analysis */}
                  <div className="panel briefing-card">
                    <div className="briefing-card-header">
                      <span className="eyebrow">Architectural Deep-Dive</span>
                      <h3>Detailed Technical Analysis</h3>
                    </div>
                    <div className="technical-prose">
                      {briefing.technical_analysis.split('\n\n').map((paragraph, i) => (
                        <p key={i}>{paragraph}</p>
                      ))}
                    </div>
                  </div>

                  {/* Engineering Recommendations & References */}
                  <div className="recommendations-references-grid">
                    <div className="panel briefing-card">
                      <div className="briefing-card-header">
                        <span className="eyebrow">Best Practices</span>
                        <h3>Actionable Recommendations</h3>
                      </div>
                      <ul className="recommendations-list">
                        {(briefing.recommendations || []).map((rec, i) => (
                          <li key={i}>{rec}</li>
                        ))}
                      </ul>
                    </div>

                    <div className="panel briefing-card">
                      <div className="briefing-card-header">
                        <span className="eyebrow">Literature & Standards</span>
                        <h3>Academic References</h3>
                      </div>
                      <ul className="references-list">
                        {(briefing.references || []).map((ref, i) => (
                          <li key={i}>
                            <span className="citation-marker">[{i + 1}]</span>
                            <span className="citation-text">{ref}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 2: Structured Evidence Table */}
              {activeTab === 'evidence' && (
                <div className="evidence-tab-content panel">
                  <div className="evidence-table-toolbar">
                    <div className="search-filter-box">
                      <input
                        type="text"
                        className="search-input"
                        placeholder="Search evidence claims, sources, quotes, metrics..."
                        value={evidenceFilter}
                        onChange={(e) => setEvidenceFilter(e.target.value)}
                      />
                    </div>

                    <div className="credibility-filter-pills">
                      {['ALL', 'Peer-Reviewed', 'Benchmark', 'Industry Spec'].map((tier) => (
                        <button
                          key={tier}
                          type="button"
                          className={`tier-pill ${credibilityFilter === tier ? 'tier-active' : ''}`}
                          onClick={() => setCredibilityFilter(tier)}
                        >
                          {tier}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="table-responsive">
                    <table className="modern-table evidence-table">
                      <thead>
                        <tr>
                          <th style={{ width: '85px' }}>ID</th>
                          <th style={{ width: '180px' }}>Source & Publication</th>
                          <th>Finding / Claim</th>
                          <th>Verbatim Evidence Quote</th>
                          <th style={{ width: '130px' }}>Metric</th>
                          <th style={{ width: '120px' }}>Credibility</th>
                          <th style={{ width: '120px' }}>Confidence</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredEvidence.length === 0 ? (
                          <tr>
                            <td colSpan="7" className="empty-table-cell">
                              No evidence entries match the specified filter.
                            </td>
                          </tr>
                        ) : (
                          filteredEvidence.map((item) => (
                            <tr key={item.id}>
                              <td>
                                <span className="evidence-id-pill">{item.id}</span>
                              </td>
                              <td>
                                <div className="source-meta">
                                  <strong>{item.source}</strong>
                                  <small className="source-title">{item.title}</small>
                                </div>
                              </td>
                              <td className="claim-cell">
                                <p className="claim-text">{item.claim}</p>
                              </td>
                              <td className="quote-cell">
                                <blockquote className="evidence-quote">
                                  &ldquo;{item.evidence_quote}&rdquo;
                                </blockquote>
                              </td>
                              <td>
                                {item.metric ? (
                                  <span className="metric-tag">{item.metric}</span>
                                ) : (
                                  <span className="text-muted">—</span>
                                )}
                              </td>
                              <td>
                                <span
                                  className={`credibility-badge cred-${item.credibility
                                    ?.toLowerCase()
                                    .replace(/[^a-z]/g, '')}`}
                                >
                                  {item.credibility}
                                </span>
                              </td>
                              <td>
                                <div className="confidence-wrapper">
                                  <div className="confidence-bar-bg">
                                    <div
                                      className="confidence-bar-fill"
                                      style={{
                                        width: `${Math.round(item.confidence_score * 100)}%`,
                                      }}
                                    />
                                  </div>
                                  <span className="confidence-pct">
                                    {Math.round(item.confidence_score * 100)}%
                                  </span>
                                </div>
                              </td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Tab 3: Tradeoffs & Comparisons */}
              {activeTab === 'tradeoffs' && (
                <div className="tradeoffs-tab-content panel">
                  <div className="panel-heading">
                    <div>
                      <span className="eyebrow">Architectural Decision Matrix</span>
                      <h3>Tradeoffs & Systematic Comparisons</h3>
                    </div>
                  </div>

                  <div className="table-responsive">
                    <table className="modern-table tradeoffs-table">
                      <thead>
                        <tr>
                          <th style={{ width: '220px' }}>Architecture / Approach</th>
                          <th>Advantages</th>
                          <th>Limitations & Costs</th>
                          <th>Recommended Use-Case</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(briefing.tradeoffs_and_comparisons || []).map((row, i) => (
                          <tr key={i}>
                            <td>
                              <strong className="tradeoff-option">{row.option}</strong>
                            </td>
                            <td>
                              <span className="tradeoff-pro">{row.advantages}</span>
                            </td>
                            <td>
                              <span className="tradeoff-con">{row.limitations}</span>
                            </td>
                            <td>
                              <span className="tradeoff-scenario">{row.best_used_when}</span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Column: Saved Briefings History */}
        <aside className="research-history-sidebar">
          <div className="panel history-panel">
            <div className="panel-heading">
              <div>
                <span className="eyebrow">Persistence</span>
                <h3>Saved Briefings</h3>
              </div>
              <button
                type="button"
                className="refresh-btn"
                onClick={loadSavedReports}
                title="Refresh history"
              >
                ↻
              </button>
            </div>

            {loadingHistory ? (
              <div className="history-loading">
                <span className="spinner-inline" /> Loading archive...
              </div>
            ) : savedReports.length === 0 ? (
              <div className="history-empty">
                <p>No stored research briefings yet. Run your first query above!</p>
              </div>
            ) : (
              <div className="history-list">
                {savedReports.map((rep) => {
                  const isActive = briefing?.id === rep.id;
                  const dateStr = rep.created_at
                    ? new Date(rep.created_at).toLocaleDateString()
                    : 'Recent';

                  return (
                    <div
                      key={rep.id}
                      className={`history-card ${isActive ? 'history-card-active' : ''}`}
                      onClick={() => handleLoadReport(rep.id)}
                    >
                      <div className="history-card-header">
                        <strong className="history-topic" title={rep.topic}>
                          {rep.topic}
                        </strong>
                        <button
                          type="button"
                          className="history-delete-btn"
                          title="Delete report"
                          onClick={(e) => handleDeleteReport(e, rep.id)}
                        >
                          ✕
                        </button>
                      </div>
                      <div className="history-meta">
                        <span className="history-badge">📊 {rep.evidence_count} items</span>
                        <span className="history-date">{dateStr}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </aside>
      </div>

      {/* Export Modal */}
      {exportModalOpen && (
        <div className="modal-backdrop" onClick={() => setExportModalOpen(false)}>
          <div className="modal-card export-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Export Evidence Table ({exportFormat.toUpperCase()})</h3>
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
                  <span>Formatting evidence table...</span>
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
              {exportFormat === 'csv' && (
                <button
                  type="button"
                  className="secondary-button"
                  onClick={handleDownloadCsv}
                  disabled={exportLoading}
                >
                  Download .CSV
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
