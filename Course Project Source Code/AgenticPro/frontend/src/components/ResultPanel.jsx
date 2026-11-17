import { useState } from 'react';

export default function ResultPanel({ result, running, runType = 'eval', questionPoints = 10 }) {
  const [activeTab, setActiveTab] = useState('tests');

  if (running) {
    return (
      <div className="result-panel-loading" role="status">
        <div className="spinner" />
        <div className="loading-text">
          <strong>
            {runType === 'test'
              ? 'Running code in sandbox...'
              : 'Executing tests & Agentic Swarm evaluation...'}
          </strong>
          <small>Checking syntax, constraints, and sandbox output</small>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="result-empty" role="status">
        <div className="result-empty-icon" aria-hidden="true">⚡</div>
        <div>
          <strong>Ready for Execution</strong>
          <p>Click "Run Code" to test against custom input, or "Submit Solution" for full grading.</p>
        </div>
      </div>
    );
  }

  // If this is a direct "Run Code" (test) result
  if (result.type === 'run_code') {
    const isSuccess = result.returncode === 0 && !result.timed_out;
    return (
      <section className="result-panel-run" aria-live="polite">
        <div className="run-header">
          <div className="run-status">
            <span
              className={`status-indicator ${
                result.timed_out
                  ? 'status-timeout'
                  : isSuccess
                  ? 'status-success'
                  : 'status-error'
              }`}
            >
              {result.timed_out
                ? 'TIMED OUT'
                : isSuccess
                ? 'EXECUTION SUCCESS (0)'
                : `EXIT CODE ${result.returncode}`}
            </span>
          </div>
          <span className="muted">Direct Sandbox Runner</span>
        </div>

        <div className="run-io-preview">
          <div className="console-pane">
            <div className="console-header">Standard Output (stdout)</div>
            <pre className="console-body">
              {result.stdout || <span className="muted-text">(no output written to stdout)</span>}
            </pre>
          </div>

          {result.stderr && (
            <div className="console-pane error-pane">
              <div className="console-header error-header">Standard Error (stderr)</div>
              <pre className="console-body error-body">{result.stderr}</pre>
            </div>
          )}
        </div>
      </section>
    );
  }

  // Full evaluation result
  const passed = result.passed ?? 0;
  const total = result.total ?? 0;
  const score = result.score ?? 0;
  const isComplete = result.status === 'completed';
  const allPassed = isComplete && total > 0 && passed === total;
  const feedback = result.feedback || '';
  const insights = result.agent_insights || null;

  // Parse feedback lines for test case breakdown
  const feedbackLines = feedback.split('\n').filter(Boolean);

  return (
    <section className="result-panel full-eval" aria-live="polite">
      <div className="eval-summary-card">
        <div className="summary-left">
          <div className="eyebrow">Evaluation Result</div>
          <div className="summary-score-row">
            <span className="summary-score">{score.toFixed(1)}</span>
            <span className="summary-max">/ {questionPoints} pts</span>
            <span
              className={`eval-status-pill ${
                allPassed ? 'pill-success' : passed > 0 ? 'pill-partial' : 'pill-fail'
              }`}
            >
              {allPassed
                ? 'ALL TESTS PASSED'
                : passed > 0
                ? 'PARTIALLY PASSED'
                : result.status === 'error'
                ? 'RUNTIME ERROR'
                : 'FAILED'}
            </span>
          </div>
          <div className="pass-rate-text">
            {passed} of {total} test cases passed ({total > 0 ? Math.round((passed / total) * 100) : 0}%)
          </div>
        </div>

        <div className="summary-right">
          <div className="pass-rate-visual">
            <div
              className="pass-rate-bar"
              style={{
                width: `${total > 0 ? Math.round((passed / total) * 100) : 0}%`,
              }}
            />
          </div>
        </div>
      </div>

      {/* Integrated Multi-Agent Quick Badges (Labs 9 - 14) */}
      {insights && (
        <div className="agent-quick-badges-bar">
          <span className={`badge-pill ${insights.safety_audit?.risk_tier === 'LOW' ? 'badge-safe' : 'badge-warn'}`}>
            🛡️ Safety: {insights.safety_audit?.risk_tier} Risk
          </span>
          <span className={`badge-pill ${insights.diagnostics?.status === 'HEALTHY' ? 'badge-safe' : 'badge-alert'}`}>
            🩺 Ops: {insights.diagnostics?.status === 'HEALTHY' ? 'Optimal' : insights.diagnostics?.category}
          </span>
          <span className="badge-pill badge-neutral">
            🏗️ SDLC: Grade {insights.sdlc_metrics?.clean_code_grade} (Complexity: {insights.sdlc_metrics?.cyclomatic_complexity})
          </span>
          <span className="badge-pill badge-safe">
            🔬 Grounding: {insights.research_check?.grounding_status === 'GROUNDED_STD_LIB' ? 'Verified' : 'External'}
          </span>
          <span className="badge-pill badge-neutral">
            🤝 Swarm: {insights.swarm_consensus?.composite_evaluation_score}/100
          </span>
        </div>
      )}

      <div className="panel-tab-bar eval-tabs">
        <button
          type="button"
          className={`panel-tab-btn ${activeTab === 'tests' ? 'active' : ''}`}
          onClick={() => setActiveTab('tests')}
        >
          Test Breakdown ({passed}/{total})
        </button>
        <button
          type="button"
          className={`panel-tab-btn ${activeTab === 'agentic' ? 'active' : ''}`}
          onClick={() => setActiveTab('agentic')}
        >
          🤖 Multi-Agent Assessment (Labs 9–14)
        </button>
        <button
          type="button"
          className={`panel-tab-btn ${activeTab === 'critique' ? 'active' : ''}`}
          onClick={() => setActiveTab('critique')}
        >
          Execution Notes
        </button>
      </div>

      <div className="eval-tab-body">
        {activeTab === 'tests' ? (
          <div className="test-results-list">
            {feedbackLines.map((line, idx) => {
              const isPass = line.toLowerCase().includes('passed');
              const isError = line.toLowerCase().includes('error') || line.toLowerCase().includes('timed out');
              return (
                <div
                  key={idx}
                  className={`test-result-row ${
                    isPass ? 'row-pass' : isError ? 'row-error' : 'row-fail'
                  }`}
                >
                  <span className="result-icon">{isPass ? '✓' : isError ? '⚠' : '✕'}</span>
                  <span className="result-text">{line}</span>
                  <span className="result-tag">{isPass ? 'Passed' : isError ? 'Error' : 'Failed'}</span>
                </div>
              );
            })}
          </div>
        ) : activeTab === 'agentic' ? (
          <div className="agentic-insights-container">
            {insights ? (
              <div className="insights-cards-grid">
                {/* Lab 12: Safety & Governance Gate */}
                <div className="insight-card">
                  <div className="insight-card-header">
                    <strong>🛡️ Lab 12: Safety & Governance Gate</strong>
                    <span className={`status-badge-sm ${insights.safety_audit?.risk_tier === 'LOW' ? 'badge-safe' : 'badge-danger'}`}>
                      {insights.safety_audit?.risk_tier} RISK ({insights.safety_audit?.risk_score}/100)
                    </span>
                  </div>
                  <p className="insight-desc">{insights.safety_audit?.details}</p>
                  <div className="insight-submeta">
                    <span>Policy Verdict: <strong>{insights.safety_audit?.policy_verdict}</strong></span>
                    <span>Blast Radius: <strong>Contained within Sandbox</strong></span>
                  </div>
                </div>

                {/* Lab 10: Cloud Operations & Runtime Diagnostics */}
                <div className={`insight-card ${insights.diagnostics?.status !== 'HEALTHY' ? 'card-alert' : ''}`}>
                  <div className="insight-card-header">
                    <strong>🩺 Lab 10: Runtime Diagnostics & Triage</strong>
                    <span className={`status-badge-sm ${insights.diagnostics?.status === 'HEALTHY' ? 'badge-safe' : 'badge-warn'}`}>
                      {insights.diagnostics?.status}
                    </span>
                  </div>
                  <p className="insight-desc">
                    <strong>Root Cause:</strong> {insights.diagnostics?.root_cause}
                  </p>
                  <div className="remediation-box">
                    <strong>Suggested Remediation:</strong>
                    <span>{insights.diagnostics?.remediation}</span>
                  </div>
                </div>

                {/* Lab 11: SDLC Factory & Code Metrics */}
                <div className="insight-card">
                  <div className="insight-card-header">
                    <strong>🏗️ Lab 11: SDLC Modularity & Metrics</strong>
                    <span className="status-badge-sm badge-info">
                      GRADE {insights.sdlc_metrics?.clean_code_grade}
                    </span>
                  </div>
                  <div className="metrics-row">
                    <div className="m-block">
                      <small>Cyclomatic Complexity</small>
                      <strong>{insights.sdlc_metrics?.cyclomatic_complexity}</strong>
                    </div>
                    <div className="m-block">
                      <small>Function Modularity</small>
                      <strong>{insights.sdlc_metrics?.function_count} fn ({insights.sdlc_metrics?.modularity})</strong>
                    </div>
                    <div className="m-block">
                      <small>Lines of Code</small>
                      <strong>{insights.sdlc_metrics?.loc} LOC</strong>
                    </div>
                  </div>
                </div>

                {/* Lab 9: Deep Research & Grounding */}
                <div className="insight-card">
                  <div className="insight-card-header">
                    <strong>🔬 Lab 9: API Research Grounding</strong>
                    <span className="status-badge-sm badge-safe">
                      {insights.research_check?.grounding_status}
                    </span>
                  </div>
                  <p className="insight-desc">
                    {insights.research_check?.documentation_fidelity}
                  </p>
                  <div className="insight-submeta">
                    <span>Verified Imports: <code>{insights.research_check?.verified_standard_libraries?.join(', ') || 'None (Built-ins)'}</code></span>
                  </div>
                </div>

                {/* Lab 14: Capstone Multi-Agent Swarm Consensus */}
                <div className="insight-card full-width-card">
                  <div className="insight-card-header">
                    <strong>🤝 Lab 14: Capstone Multi-Agent Swarm Evaluation</strong>
                    <span className="status-badge-sm badge-success">
                      {insights.swarm_consensus?.committee_decision}
                    </span>
                  </div>
                  <div className="swarm-breakdown-row">
                    <div className="swarm-agent-col">
                      <small>Lead Architect</small>
                      <strong>{insights.swarm_consensus?.lead_architect_score}%</strong>
                    </div>
                    <div className="swarm-agent-col">
                      <small>QA Lead</small>
                      <strong>{insights.swarm_consensus?.qa_lead_score}%</strong>
                    </div>
                    <div className="swarm-agent-col">
                      <small>Governance Officer</small>
                      <strong>{insights.swarm_consensus?.governance_officer_score}%</strong>
                    </div>
                    <div className="swarm-agent-col composite-col">
                      <small>Composite Score</small>
                      <strong className="comp-score">{insights.swarm_consensus?.composite_evaluation_score} / 100</strong>
                    </div>
                  </div>
                  <div className="roster-pills">
                    <small>Committee Signoff:</small>
                    {insights.swarm_consensus?.active_roster?.map((role, rIdx) => (
                      <span key={rIdx} className="roster-pill-sm">{role}</span>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="empty-panel">
                <p>Run full submission to view multi-agent evaluation insights.</p>
              </div>
            )}
          </div>
        ) : (
          <div className="critique-content">
            <div className="agent-badge-box">
              <span className="agent-avatar">🤖</span>
              <div>
                <strong>Swarm Feedback Agent</strong>
                <p>Automated code critique and optimization analysis</p>
              </div>
            </div>
            <div className="critique-box">
              <pre className="critique-text">{feedback || 'No additional critique notes available.'}</pre>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
