import { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function ResultsPage({ isFaculty = false, currentStudentId = 'student-test-001' }) {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [notification, setNotification] = useState(null);

  useEffect(() => {
    loadResults();
  }, []);

  const showToast = (msg) => {
    setNotification(msg);
    setTimeout(() => setNotification(null), 3500);
  };

  const loadResults = async () => {
    setLoading(true);
    try {
      const data = await api.getResults();
      setResults(data);
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleTogglePublish = async (examId, studentId, currentStatus) => {
    try {
      await api.publishResult(examId, studentId, !currentStatus);
      showToast(`Result ${!currentStatus ? 'published' : 'unpublished'}!`);
      loadResults();
    } catch (err) {
      showToast(`Error: ${err.message}`);
    }
  };

  const filteredResults = results.filter((r) =>
    (r.student_id || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (r.exam_id || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Stats calculation
  const totalResults = results.length;
  const avgScore = totalResults > 0
    ? (results.reduce((acc, r) => acc + (r.score || 0), 0) / totalResults).toFixed(1)
    : 0;
  const highestScore = totalResults > 0
    ? Math.max(...results.map((r) => r.score || 0))
    : 0;
  const passCount = results.filter((r) => r.max_score > 0 && (r.score / r.max_score) >= 0.5).length;
  const passRate = totalResults > 0 ? Math.round((passCount / totalResults) * 100) : 0;

  return (
    <section className="page-content results-page">
      {notification && (
        <div className="toast-notification toast-success">{notification}</div>
      )}

      <div className="page-heading">
        <div>
          <div className="eyebrow">Academic Records</div>
          <h1>Lab Assessment Results & Gradebook</h1>
        </div>
        <button type="button" className="refresh-btn" onClick={loadResults} disabled={loading}>
          {loading ? 'Refreshing…' : '↻ Refresh'}
        </button>
      </div>

      {/* Aggregate Stats */}
      <div className="stats-grid">
        <div className="stat-block">
          <span>Total Records</span>
          <strong>{totalResults}</strong>
        </div>
        <div className="stat-block">
          <span>Class Average</span>
          <strong>{avgScore} pts</strong>
        </div>
        <div className="stat-block">
          <span>Highest Score</span>
          <strong>{highestScore} pts</strong>
        </div>
        <div className="stat-block">
          <span>Pass Rate (≥50%)</span>
          <strong>{passRate}%</strong>
        </div>
      </div>

      {/* Gradebook Panel */}
      <div className="panel results-table-panel">
        <div className="panel-heading">
          <div>
            <div className="eyebrow">Records Registry</div>
            <h3>Official Graded Assessments</h3>
          </div>

          <div className="search-filter-box">
            <input
              type="text"
              className="search-input"
              placeholder="Filter by student or exam ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        {loading ? (
          <div className="loading-state">
            <div className="spinner" />
            <span>Retrieving published results...</span>
          </div>
        ) : filteredResults.length === 0 ? (
          <div className="empty-panel">
            <div className="empty-icon" aria-hidden="true">📊</div>
            <p>No results found matching your criteria.</p>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="modern-table">
              <thead>
                <tr>
                  <th>Student ID</th>
                  <th>Exam ID</th>
                  <th>Score Earned</th>
                  <th>Max Points</th>
                  <th>Percentage</th>
                  <th>Academic Standing</th>
                  <th>Publication</th>
                  {isFaculty && <th>Faculty Action</th>}
                </tr>
              </thead>
              <tbody>
                {filteredResults.map((r, idx) => {
                  const pct = r.max_score > 0 ? Math.round((r.score / r.max_score) * 100) : 0;
                  const isPass = pct >= 50;
                  return (
                    <tr key={`${r.exam_id}-${r.student_id}-${idx}`}>
                      <td>
                        <strong>{r.student_id}</strong>
                        {r.student_id === currentStudentId && (
                          <span className="you-pill">You</span>
                        )}
                      </td>
                      <td><code>{r.exam_id}</code></td>
                      <td>
                        <strong className="score-text">{r.score}</strong>
                      </td>
                      <td>{r.max_score}</td>
                      <td>
                        <div className="pct-cell">
                          <span className={`pct-pill ${pct >= 75 ? 'pct-high' : pct >= 50 ? 'pct-med' : 'pct-low'}`}>
                            {pct}%
                          </span>
                        </div>
                      </td>
                      <td>
                        <span className={`standing-badge ${isPass ? 'standing-pass' : 'standing-fail'}`}>
                          {pct >= 85 ? 'Distinction' : pct >= 50 ? 'Satisfactory' : 'Needs Review'}
                        </span>
                      </td>
                      <td>
                        <span className={`status-tag ${r.published ? 'published' : 'draft'}`}>
                          {r.published ? 'Published' : 'Instructor Draft'}
                        </span>
                      </td>
                      {isFaculty && (
                        <td>
                          <button
                            type="button"
                            className="toggle-publish-btn"
                            onClick={() => handleTogglePublish(r.exam_id, r.student_id, r.published)}
                          >
                            {r.published ? 'Unpublish' : 'Publish'}
                          </button>
                        </td>
                      )}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}
