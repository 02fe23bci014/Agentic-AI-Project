import { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function StudentDashboard({ onStart, currentStudentId = 'student-test-001' }) {
  const [exams, setExams] = useState([]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadDashboardData();
  }, [currentStudentId]);

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [examsData, resultsData] = await Promise.all([
        api.getExams().catch(() => []),
        api.getResults({ student_id: currentStudentId }).catch(() => []),
      ]);
      setExams(examsData);
      setResults(resultsData);
    } catch (err) {
      setError(err.message || 'Error loading dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const filteredExams = exams.filter((exam) =>
    (exam.title || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (exam.id || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Map results by exam ID
  const resultsByExam = {};
  results.forEach((r) => {
    resultsByExam[r.exam_id] = r;
  });

  return (
    <section className="page-content student-dashboard">
      {/* Student Welcome Banner */}
      <div className="welcome-banner">
        <div className="welcome-text">
          <div className="eyebrow">Academic Session 2026-2027</div>
          <h1>Student Assessment Hub</h1>
          <p>
            Welcome, <strong>{currentStudentId}</strong>. Access your scheduled programming laboratory assessments,
            test code in isolated sandboxes, and inspect AI-driven evaluation reports.
          </p>
        </div>
        <div className="welcome-stats">
          <div className="welcome-stat-pill">
            <span className="pill-num">{exams.length}</span>
            <span className="pill-label">Total Labs</span>
          </div>
          <div className="welcome-stat-pill">
            <span className="pill-num">{results.length}</span>
            <span className="pill-label">Graded</span>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="dashboard-section-header">
        <div>
          <h2>Available Laboratory Exams</h2>
          <span className="muted">Select an assessment to launch the code arena</span>
        </div>

        <div className="search-filter-box">
          <input
            type="text"
            className="search-input"
            placeholder="Search exams by title or ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {loading ? (
        <div className="loading-state">
          <div className="spinner" />
          <span>Loading programming labs...</span>
        </div>
      ) : error ? (
        <div className="panel error-panel">
          <p>{error}</p>
          <button type="button" className="secondary-button" onClick={loadDashboardData}>
            Try Again
          </button>
        </div>
      ) : filteredExams.length === 0 ? (
        <div className="panel empty-panel">
          <div className="empty-icon" aria-hidden="true">📋</div>
          <h3>No Laboratory Exams Found</h3>
          <p>There are no active exams matching your query at this time.</p>
        </div>
      ) : (
        <div className="exam-cards-grid">
          {filteredExams.map((exam, index) => {
            const hasResult = resultsByExam[exam.id];
            const qCount = (exam.question_ids || []).length;

            return (
              <div className="exam-card" key={exam.id}>
                <div className="exam-card-header">
                  <span className="exam-index">LAB #{String(index + 1).padStart(2, '0')}</span>
                  <span className={`exam-status-badge ${hasResult ? 'badge-completed' : 'badge-available'}`}>
                    {hasResult ? 'Graded' : 'Ready'}
                  </span>
                </div>

                <h3 className="exam-card-title">{exam.title}</h3>
                <span className="exam-card-id">{exam.id}</span>

                <div className="exam-card-meta">
                  <div className="meta-item">
                    <span className="meta-label">Duration</span>
                    <strong className="meta-value">{exam.duration_minutes} Mins</strong>
                  </div>
                  <div className="meta-item">
                    <span className="meta-label">Questions</span>
                    <strong className="meta-value">{qCount} Problems</strong>
                  </div>
                  {hasResult && (
                    <div className="meta-item">
                      <span className="meta-label">Your Score</span>
                      <strong className="meta-value score-highlight">
                        {hasResult.score} / {hasResult.max_score}
                      </strong>
                    </div>
                  )}
                </div>

                <div className="exam-card-actions">
                  <button
                    type="button"
                    className="primary-button full-width"
                    onClick={() => onStart(exam)}
                  >
                    {hasResult ? 'Review & Practice Again' : 'Enter Coding Arena →'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Recent Activity / Performance History */}
      {results.length > 0 && (
        <div className="panel recent-results-panel">
          <div className="panel-heading">
            <div>
              <div className="eyebrow">Academic Records</div>
              <h3>Your Recent Evaluation Scores</h3>
            </div>
          </div>

          <div className="table-responsive">
            <table className="modern-table">
              <thead>
                <tr>
                  <th>Exam ID</th>
                  <th>Score</th>
                  <th>Max Score</th>
                  <th>Percentage</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {results.map((res) => {
                  const pct = res.max_score > 0 ? Math.round((res.score / res.max_score) * 100) : 0;
                  return (
                    <tr key={res.exam_id}>
                      <td>
                        <strong>{res.exam_id}</strong>
                      </td>
                      <td>{res.score}</td>
                      <td>{res.max_score}</td>
                      <td>
                        <span className={`pct-pill ${pct >= 70 ? 'pct-high' : pct >= 40 ? 'pct-med' : 'pct-low'}`}>
                          {pct}%
                        </span>
                      </td>
                      <td>
                        <span className="status-tag published">Published</span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </section>
  );
}
