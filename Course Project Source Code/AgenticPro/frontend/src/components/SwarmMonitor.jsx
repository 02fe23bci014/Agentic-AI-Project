import { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function SwarmMonitor() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeAgent, setActiveAgent] = useState('Scoring Swarm Agent');

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getStats();
      setStats(data);
    } catch (err) {
      setError(err.message || 'Could not load swarm statistics');
    } finally {
      setLoading(false);
    }
  };

  const agentDetails = {
    'Sandbox Runner Agent': {
      role: 'Secure code execution isolation',
      description: 'Executes submitted student code in restricted environments. Enforces memory caps (256MB), CPU quotas (1.0 core), dropped capabilities, and fallback execution.',
      inputs: ['source_code', 'language', 'stdin'],
      outputs: ['stdout', 'stderr', 'returncode', 'timed_out'],
      icon: '🛡️',
    },
    'Question Generation Agent': {
      role: 'Automated problem & constraint generation',
      description: 'Creates rigorous algorithmic problems given topics, difficulty levels, and target languages with comprehensive prompt templates.',
      inputs: ['topic', 'difficulty', 'language', 'marks'],
      outputs: ['title', 'description', 'input_format', 'output_format', 'constraints', 'examples'],
      icon: '🧠',
    },
    'Test Case Agent': {
      role: 'Comprehensive test generation',
      description: 'Generates diverse test cases including public examples, hidden verification tests, edge cases (zero, negative, max limits), and boundary conditions.',
      inputs: ['question_spec', 'test_type', 'case_count'],
      outputs: ['stdin', 'expected_stdout', 'points', 'is_hidden'],
      icon: '🧪',
    },
    'Scoring Swarm Agent': {
      role: 'Multi-criteria evaluation & points calculation',
      description: 'Executes within parallel Swarm threads. Calculates earned marks scaled to total question points, weighting test cases by difficulty.',
      inputs: ['test_case_results', 'max_score'],
      outputs: ['score', 'earned_percentage', 'status'],
      icon: '🎯',
    },
    'Feedback Swarm Agent': {
      role: 'Code critique & algorithmic advice',
      description: 'Analyzes submission execution logs, exceptions, and mismatches. Synthesizes constructive guidance for students on fixing bugs.',
      inputs: ['stderr_logs', 'failed_cases', 'source_code'],
      outputs: ['feedback_summary', 'suggestions', 'critique'],
      icon: '💬',
    },
    'Similarity Agent': {
      role: 'Plagiarism & code similarity detection',
      description: 'Compares student submissions against peer code and known solutions using token-level matching to ensure academic integrity.',
      inputs: ['source_code', 'peer_submissions'],
      outputs: ['similarity_score', 'flagged_clusters'],
      icon: '🔍',
    },
  };

  return (
    <section className="page-content swarm-monitor-page">
      <div className="page-heading">
        <div>
          <div className="eyebrow">Multi-Agent Architecture</div>
          <h1>Agentic Swarm Monitor</h1>
        </div>
        <button
          type="button"
          className="refresh-btn"
          onClick={loadStats}
          disabled={loading}
        >
          {loading ? 'Refreshing…' : '↻ Refresh System'}
        </button>
      </div>

      {/* Overview Stat Badges */}
      <div className="stats-grid swarm-stats-grid">
        <div className="stat-block">
          <span>Active Agents</span>
          <strong>6 Registered</strong>
        </div>
        <div className="stat-block">
          <span>Stored Exams</span>
          <strong>{stats?.counts?.exams ?? '—'}</strong>
        </div>
        <div className="stat-block">
          <span>Question Bank</span>
          <strong>{stats?.counts?.questions ?? '—'}</strong>
        </div>
        <div className="stat-block">
          <span>Total Submissions</span>
          <strong>{stats?.counts?.submissions ?? '—'}</strong>
        </div>
      </div>

      {/* Architecture Flowchart */}
      <div className="panel architecture-panel">
        <div className="panel-heading">
          <div>
            <div className="eyebrow">Execution Pipeline</div>
            <h2>Autonomous Swarm Workflow</h2>
          </div>
          <span className="live-pill">● Parallel Orchestration</span>
        </div>

        <div className="pipeline-flow">
          <div className="pipeline-node node-input">
            <span className="node-icon">💻</span>
            <strong>Student Code</strong>
            <small>Python / C++ / Java</small>
          </div>

          <div className="pipeline-arrow">➔</div>

          <div className="pipeline-node node-sandbox">
            <span className="node-icon">🛡️</span>
            <strong>Sandbox Runner</strong>
            <small>Resource Isolation</small>
          </div>

          <div className="pipeline-arrow">➔</div>

          <div className="pipeline-node node-coordinator">
            <span className="node-icon">⚡</span>
            <strong>Swarm Coordinator</strong>
            <small>Worker Threadpool</small>
          </div>

          <div className="pipeline-arrow">➔</div>

          <div className="pipeline-swarm-parallel">
            <div className="parallel-node">
              <span className="mini-icon">🎯</span>
              <span>Scoring Agent</span>
            </div>
            <div className="parallel-node">
              <span className="mini-icon">💬</span>
              <span>Feedback Agent</span>
            </div>
            <div className="parallel-node">
              <span className="mini-icon">🔍</span>
              <span>Similarity Agent</span>
            </div>
          </div>

          <div className="pipeline-arrow">➔</div>

          <div className="pipeline-node node-output">
            <span className="node-icon">📊</span>
            <strong>Persisted Grade</strong>
            <small>SQLite & Results</small>
          </div>
        </div>
      </div>

      {/* Interactive Agent Inspector */}
      <div className="agent-inspector-layout">
        <div className="agent-list-column">
          <h3>Registered Swarm Agents</h3>
          <div className="agent-card-list">
            {Object.entries(agentDetails).map(([name, info]) => (
              <div
                key={name}
                className={`agent-card ${activeAgent === name ? 'selected' : ''}`}
                onClick={() => setActiveAgent(name)}
              >
                <span className="agent-card-icon">{info.icon}</span>
                <div className="agent-card-meta">
                  <strong>{name}</strong>
                  <small>{info.role}</small>
                </div>
                <span className="agent-status-dot" title="Agent online" />
              </div>
            ))}
          </div>
        </div>

        <div className="agent-detail-column">
          {activeAgent && agentDetails[activeAgent] && (
            <div className="panel agent-detail-panel">
              <div className="detail-header">
                <span className="detail-icon">{agentDetails[activeAgent].icon}</span>
                <div>
                  <h2>{activeAgent}</h2>
                  <span className="role-tag">{agentDetails[activeAgent].role}</span>
                </div>
              </div>

              <p className="detail-description">{agentDetails[activeAgent].description}</p>

              <div className="io-spec-grid">
                <div className="io-spec-block">
                  <h4>Context & Inputs</h4>
                  <ul>
                    {agentDetails[activeAgent].inputs.map((inp) => (
                      <li key={inp}>
                        <code>{inp}</code>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="io-spec-block">
                  <h4>Outputs & Findings</h4>
                  <ul>
                    {agentDetails[activeAgent].outputs.map((out) => (
                      <li key={out}>
                        <code>{out}</code>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="swarm-protocol-box">
                <h4>Swarm Protocol Guarantees</h4>
                <div className="guarantees-grid">
                  <div className="guarantee-item">
                    <strong>Conflict Detection:</strong> Merges findings and flags divergent evaluations.
                  </div>
                  <div className="guarantee-item">
                    <strong>Fault Tolerance:</strong> Saves evaluation state even if a single agent encounters a timeout.
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
