import { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function FacultyDashboard() {
  const [activeTab, setActiveTab] = useState('exams'); // 'exams' | 'questions' | 'testcases' | 'submissions'
  const [stats, setStats] = useState(null);
  const [exams, setExams] = useState([]);
  const [questions, setQuestions] = useState([]);
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [notification, setNotification] = useState(null);

  // Exam Creator Modal
  const [showExamModal, setShowExamModal] = useState(false);
  const [newExamId, setNewExamId] = useState('');
  const [newExamTitle, setNewExamTitle] = useState('');
  const [newExamDuration, setNewExamDuration] = useState(60);
  const [selectedQuestionsForExam, setSelectedQuestionsForExam] = useState([]);

  // Question Creator Modal
  const [showQuestionModal, setShowQuestionModal] = useState(false);
  const [newQId, setNewQId] = useState('');
  const [newQTitle, setNewQTitle] = useState('');
  const [newQPrompt, setNewQPrompt] = useState('');
  const [newQLang, setNewQLang] = useState('python');
  const [newQPoints, setNewQPoints] = useState(10);
  const [newQDiff, setNewQDiff] = useState('L1');
  const [newQDomain, setNewQDomain] = useState('Algorithms');

  // Filter States
  const [modalDomainFilter, setModalDomainFilter] = useState('ALL');
  const [modalDiffFilter, setModalDiffFilter] = useState('ALL');
  const [qBankDomainFilter, setQBankDomainFilter] = useState('ALL');
  const [qBankDiffFilter, setQBankDiffFilter] = useState('ALL');

  // AI Question Generator Studio
  const [aiTopic, setAiTopic] = useState('Arrays');
  const [aiDifficulty, setAiDifficulty] = useState('Easy');
  const [aiLanguage, setAiLanguage] = useState('python');
  const [aiMarks, setAiMarks] = useState(10);
  const [generatingAi, setGeneratingAi] = useState(false);
  const [generatedResult, setGeneratedResult] = useState(null);

  // Test Case Studio
  const [selectedQuestionForTest, setSelectedQuestionForTest] = useState('');
  const [questionTestCases, setQuestionTestCases] = useState([]);
  const [newTestStdin, setNewTestStdin] = useState('');
  const [newTestExpected, setNewTestExpected] = useState('');
  const [newTestPoints, setNewTestPoints] = useState(5);
  const [newTestHidden, setNewTestHidden] = useState(false);

  // Submission Inspector Modal
  const [inspectedSub, setInspectedSub] = useState(null);
  const [inspectedEval, setInspectedEval] = useState(null);
  const [evaluatingSub, setEvaluatingSub] = useState(false);

  useEffect(() => {
    loadAllData();
  }, []);

  const showToast = (msg, isError = false) => {
    setNotification({ msg, isError });
    setTimeout(() => setNotification(null), 4000);
  };

  const loadAllData = async () => {
    setLoading(true);
    try {
      const [statsData, examsData, questionsData, subsData] = await Promise.all([
        api.getStats().catch(() => null),
        api.getExams().catch(() => []),
        api.getQuestions().catch(() => []),
        api.getSubmissions().catch(() => []),
      ]);
      setStats(statsData);
      setExams(examsData);
      setQuestions(questionsData);
      setSubmissions(subsData);

      if (questionsData.length > 0 && !selectedQuestionForTest) {
        setSelectedQuestionForTest(questionsData[0].id);
        loadTestCases(questionsData[0].id);
      }
    } catch (err) {
      showToast(err.message, true);
    } finally {
      setLoading(false);
    }
  };

  const loadTestCases = async (questionId) => {
    if (!questionId) return;
    try {
      const cases = await api.getTestCases(questionId, true);
      setQuestionTestCases(cases);
    } catch {
      setQuestionTestCases([]);
    }
  };

  // Create Exam
  const handleCreateExam = async (e) => {
    e.preventDefault();
    if (!newExamId || !newExamTitle) {
      showToast('Please provide an exam ID and title', true);
      return;
    }
    try {
      await api.createExam({
        id: newExamId.trim(),
        title: newExamTitle.trim(),
        duration_minutes: Number(newExamDuration),
        question_ids: selectedQuestionsForExam,
      });
      showToast(`Exam "${newExamTitle}" created successfully!`);
      setShowExamModal(false);
      setNewExamId('');
      setNewExamTitle('');
      setSelectedQuestionsForExam([]);
      loadAllData();
    } catch (err) {
      showToast(err.message, true);
    }
  };

  // Delete Exam
  const handleDeleteExam = async (id) => {
    if (!window.confirm(`Delete exam "${id}"?`)) return;
    try {
      await api.deleteExam(id);
      showToast('Exam deleted successfully');
      loadAllData();
    } catch (err) {
      showToast(err.message, true);
    }
  };

  // Create Question Manually
  const handleCreateQuestion = async (e) => {
    e.preventDefault();
    if (!newQId || !newQTitle || !newQPrompt) {
      showToast('Please fill all question fields', true);
      return;
    }
    try {
      await api.createQuestion({
        id: newQId.trim(),
        title: newQTitle.trim(),
        prompt: newQPrompt.trim(),
        language: newQLang,
        points: Number(newQPoints),
        difficulty: newQDiff,
        domain: newQDomain,
      });
      showToast(`Question "${newQTitle}" saved to Question Bank!`);
      setShowQuestionModal(false);
      setNewQId('');
      setNewQTitle('');
      setNewQPrompt('');
      setNewQDiff('L1');
      setNewQDomain('Algorithms');
      loadAllData();
    } catch (err) {
      showToast(err.message, true);
    }
  };

  // Generate Question with AI Agent
  const handleGenerateAiQuestion = async () => {
    setGeneratingAi(true);
    setGeneratedResult(null);
    try {
      const res = await api.generateQuestion({
        topic: aiTopic,
        difficulty: aiDifficulty,
        language: aiLanguage,
        marks: Number(aiMarks),
      });
      setGeneratedResult(res);
      showToast('Question generated by AI Agent!');
    } catch (err) {
      showToast(err.message, true);
    } finally {
      setGeneratingAi(false);
    }
  };

  // Save AI Generated Question to DB
  const handleSaveAiQuestion = async () => {
    if (!generatedResult) return;
    try {
      await api.createQuestion({
        id: generatedResult.id,
        title: generatedResult.title,
        prompt: generatedResult.prompt,
        language: generatedResult.language,
        points: generatedResult.points,
      });

      // If sample input/output is present, also save a sample test case!
      if (generatedResult.sample_input && generatedResult.sample_output) {
        try {
          await api.createTestCase({
            id: `tc-${generatedResult.id}-01`,
            question_id: generatedResult.id,
            stdin: generatedResult.sample_input,
            expected_stdout: generatedResult.sample_output,
            points: generatedResult.points,
            is_hidden: false,
          });
        } catch {
          // ignore test case error
        }
      }

      showToast(`AI Question "${generatedResult.title}" saved to Question Bank!`);
      setGeneratedResult(null);
      loadAllData();
    } catch (err) {
      showToast(err.message, true);
    }
  };

  // Delete Question
  const handleDeleteQuestion = async (id) => {
    if (!window.confirm(`Delete question "${id}"? This also removes test cases.`)) return;
    try {
      await api.deleteQuestion(id);
      showToast('Question removed from bank');
      loadAllData();
    } catch (err) {
      showToast(err.message, true);
    }
  };

  // Add Test Case
  const handleAddTestCase = async (e) => {
    e.preventDefault();
    if (!selectedQuestionForTest || !newTestExpected) {
      showToast('Expected output is required', true);
      return;
    }
    try {
      const tcId = `tc-${selectedQuestionForTest}-${Date.now().toString().slice(-4)}`;
      await api.createTestCase({
        id: tcId,
        question_id: selectedQuestionForTest,
        stdin: newTestStdin,
        expected_stdout: newTestExpected,
        points: Number(newTestPoints),
        is_hidden: newTestHidden,
      });
      showToast('Test case saved successfully!');
      setNewTestStdin('');
      setNewTestExpected('');
      loadTestCases(selectedQuestionForTest);
    } catch (err) {
      showToast(err.message, true);
    }
  };

  // Inspect & Grade Submission
  const handleInspectSubmission = async (sub) => {
    setInspectedSub(sub);
    setInspectedEval(null);
    try {
      const ev = await api.getEvaluation(sub.id);
      setInspectedEval(ev);
    } catch {
      setInspectedEval(null);
    }
  };

  const handleReEvaluateSubmission = async (subId) => {
    setEvaluatingSub(true);
    try {
      const res = await api.runEvaluation(subId);
      setInspectedEval(res);
      showToast('Evaluation executed successfully!');
    } catch (err) {
      showToast(err.message, true);
    } finally {
      setEvaluatingSub(false);
    }
  };

  return (
    <section className="page-content faculty-dashboard">
      {notification && (
        <div className={`toast-notification ${notification.isError ? 'toast-error' : 'toast-success'}`}>
          {notification.msg}
        </div>
      )}

      {/* Heading */}
      <div className="page-heading">
        <div>
          <div className="eyebrow">Faculty Administration</div>
          <h1>Programming Lab Instructor Dashboard</h1>
        </div>
        <div className="header-actions">
          <button type="button" className="refresh-btn" onClick={loadAllData} disabled={loading}>
            {loading ? 'Refreshing…' : '↻ Refresh'}
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-block">
          <span>Active Labs / Exams</span>
          <strong>{exams.length}</strong>
        </div>
        <div className="stat-block">
          <span>Total Questions in Bank</span>
          <strong>{questions.length}</strong>
        </div>
        <div className="stat-block">
          <span>Submissions Received</span>
          <strong>{submissions.length}</strong>
        </div>
        <div className="stat-block">
          <span>Average Score</span>
          <strong>{stats?.averages?.score ? `${stats.averages.score} pts` : '—'}</strong>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="panel-tab-bar faculty-tabs">
        <button
          type="button"
          className={`panel-tab-btn ${activeTab === 'exams' ? 'active' : ''}`}
          onClick={() => setActiveTab('exams')}
        >
          Exams Management ({exams.length})
        </button>
        <button
          type="button"
          className={`panel-tab-btn ${activeTab === 'questions' ? 'active' : ''}`}
          onClick={() => setActiveTab('questions')}
        >
          Question Bank & AI Generator ({questions.length})
        </button>
        <button
          type="button"
          className={`panel-tab-btn ${activeTab === 'testcases' ? 'active' : ''}`}
          onClick={() => setActiveTab('testcases')}
        >
          Test Case Studio
        </button>
        <button
          type="button"
          className={`panel-tab-btn ${activeTab === 'submissions' ? 'active' : ''}`}
          onClick={() => setActiveTab('submissions')}
        >
          Student Submissions ({submissions.length})
        </button>
      </div>

      {/* Tab 1: Exams */}
      {activeTab === 'exams' && (
        <div className="faculty-tab-content">
          <div className="sub-header-bar">
            <div>
              <h3>Configured Lab Assessments</h3>
              <span className="muted">Create and organize laboratory sessions</span>
            </div>
            <button
              type="button"
              className="primary-button"
              onClick={() => setShowExamModal(true)}
            >
              + Create New Lab Exam
            </button>
          </div>

          <div className="table-responsive panel">
            <table className="modern-table">
              <thead>
                <tr>
                  <th>Exam ID</th>
                  <th>Title</th>
                  <th>Duration</th>
                  <th>Questions</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {exams.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="empty-td">No exams configured yet.</td>
                  </tr>
                ) : (
                  exams.map((ex) => (
                    <tr key={ex.id}>
                      <td><code>{ex.id}</code></td>
                      <td><strong>{ex.title}</strong></td>
                      <td>{ex.duration_minutes} minutes</td>
                      <td>
                        <span className="count-pill">
                          {(ex.question_ids || []).length} Problems
                        </span>
                      </td>
                      <td>
                        <button
                          type="button"
                          className="action-link-danger"
                          onClick={() => handleDeleteExam(ex.id)}
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 2: Questions & AI Generator */}
      {activeTab === 'questions' && (
        <div className="faculty-tab-content">
          <div className="questions-studio-grid">
            {/* Left: AI Question Generation Studio */}
            <div className="panel ai-generator-panel">
              <div className="panel-heading">
                <div>
                  <div className="eyebrow">Agentic AI Tool</div>
                  <h3>Question Generation Agent</h3>
                </div>
                <span className="ai-pill">✨ Powered by Ollama / Swarm</span>
              </div>

              <div className="form-group-grid">
                <label className="form-label">
                  <span>Topic</span>
                  <select
                    className="form-input"
                    value={aiTopic}
                    onChange={(e) => setAiTopic(e.target.value)}
                  >
                    <option value="Arrays">Arrays & Pointers</option>
                    <option value="Strings">Strings & Parsing</option>
                    <option value="Math">Number Theory & Math</option>
                    <option value="Recursion">Recursion & Backtracking</option>
                    <option value="Sorting">Sorting & Searching</option>
                    <option value="Dynamic Programming">Dynamic Programming</option>
                  </select>
                </label>

                <label className="form-label">
                  <span>Difficulty</span>
                  <select
                    className="form-input"
                    value={aiDifficulty}
                    onChange={(e) => setAiDifficulty(e.target.value)}
                  >
                    <option value="Easy">Easy</option>
                    <option value="Medium">Medium</option>
                    <option value="Hard">Hard</option>
                  </select>
                </label>

                <label className="form-label">
                  <span>Target Language</span>
                  <select
                    className="form-input"
                    value={aiLanguage}
                    onChange={(e) => setAiLanguage(e.target.value)}
                  >
                    <option value="python">Python</option>
                    <option value="cpp">C++</option>
                    <option value="java">Java</option>
                  </select>
                </label>

                <label className="form-label">
                  <span>Points</span>
                  <input
                    type="number"
                    className="form-input"
                    value={aiMarks}
                    min={1}
                    max={100}
                    onChange={(e) => setAiMarks(e.target.value)}
                  />
                </label>
              </div>

              <button
                type="button"
                className="primary-button full-width"
                onClick={handleGenerateAiQuestion}
                disabled={generatingAi}
              >
                {generatingAi ? 'Autonomous Agent Synthesizing Question…' : '⚡ Generate Question with Agent'}
              </button>

              {generatedResult && (
                <div className="generated-preview-card">
                  <div className="preview-header">
                    <h4>{generatedResult.title}</h4>
                    <span className="pill pill-points">{generatedResult.points} pts</span>
                  </div>
                  <pre className="preview-prompt">{generatedResult.prompt}</pre>
                  {generatedResult.sample_input && (
                    <div className="preview-sample">
                      <small>Sample Input: <code>{generatedResult.sample_input}</code></small>
                      <small>Expected Output: <code>{generatedResult.sample_output}</code></small>
                    </div>
                  )}
                  <button
                    type="button"
                    className="save-agent-btn"
                    onClick={handleSaveAiQuestion}
                  >
                    + Save into Question Bank
                  </button>
                </div>
              )}
            </div>

            {/* Right: Existing Question Bank */}
            <div className="panel question-bank-panel">
              <div className="panel-heading">
                <div>
                  <div className="eyebrow">Curriculum Bank</div>
                  <h3>Existing Questions ({questions.length})</h3>
                </div>
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => setShowQuestionModal(true)}
                >
                  + Add Manually
                </button>
              </div>

              <div className="qbank-filters-row">
                <select
                  className="form-input-sm"
                  value={qBankDomainFilter}
                  onChange={(e) => setQBankDomainFilter(e.target.value)}
                >
                  <option value="ALL">All DSA Domains ({questions.length})</option>
                  <option value="Arrays">Arrays</option>
                  <option value="Strings">Strings</option>
                  <option value="Stacks">Stacks</option>
                  <option value="Queues">Queues</option>
                  <option value="Linked Lists">Linked Lists</option>
                  <option value="Trees">Trees</option>
                  <option value="Graphs">Graphs</option>
                  <option value="Dynamic Programming">Dynamic Programming</option>
                </select>

                <select
                  className="form-input-sm"
                  value={qBankDiffFilter}
                  onChange={(e) => setQBankDiffFilter(e.target.value)}
                >
                  <option value="ALL">All Difficulty Levels</option>
                  <option value="L1">Level 1 (L1 - Foundational)</option>
                  <option value="L2">Level 2 (L2 - Intermediate)</option>
                  <option value="L3">Level 3 (L3 - Advanced)</option>
                </select>
              </div>

              <div className="question-bank-scroll">
                {questions
                  .filter((q) => {
                    const matchDomain = qBankDomainFilter === 'ALL' || (q.domain || 'Algorithms') === qBankDomainFilter;
                    const matchDiff = qBankDiffFilter === 'ALL' || (q.difficulty || 'L1') === qBankDiffFilter;
                    return matchDomain && matchDiff;
                  })
                  .map((q) => (
                  <div className="qbank-card" key={q.id}>
                    <div className="qbank-card-header">
                      <div>
                        <div className="qbank-meta-tags">
                          <span className={`diff-badge diff-${(q.difficulty || 'L1').toLowerCase()}`}>
                            {q.difficulty || 'L1'}
                          </span>
                          <span className="domain-pill-sm">{q.domain || 'Algorithms'}</span>
                        </div>
                        <strong>{q.title}</strong>
                        <span className="qbank-id">{q.id}</span>
                      </div>
                      <div className="qbank-pills">
                        <span className="pill pill-lang">{q.language}</span>
                        <span className="pill pill-points">{q.points}p</span>
                      </div>
                    </div>
                    <p className="qbank-prompt-preview">{q.prompt}</p>
                    <div className="qbank-actions">
                      <button
                        type="button"
                        className="action-btn-small"
                        onClick={() => {
                          setSelectedQuestionForTest(q.id);
                          setActiveTab('testcases');
                          loadTestCases(q.id);
                        }}
                      >
                        Manage Test Cases
                      </button>
                      <button
                        type="button"
                        className="action-link-danger"
                        onClick={() => handleDeleteQuestion(q.id)}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Test Case Studio */}
      {activeTab === 'testcases' && (
        <div className="faculty-tab-content">
          <div className="testcase-studio-grid">
            {/* Left: Test Cases List for Selected Question */}
            <div className="panel testcase-list-panel">
              <div className="panel-heading">
                <div>
                  <div className="eyebrow">Verification Suite</div>
                  <h3>Test Cases for Selected Question</h3>
                </div>
                <select
                  className="form-input"
                  style={{ maxWidth: '240px' }}
                  value={selectedQuestionForTest}
                  onChange={(e) => {
                    setSelectedQuestionForTest(e.target.value);
                    loadTestCases(e.target.value);
                  }}
                >
                  {questions.map((q) => (
                    <option key={q.id} value={q.id}>
                      {q.title} ({q.id})
                    </option>
                  ))}
                </select>
              </div>

              <div className="test-cases-table-wrap">
                {questionTestCases.length === 0 ? (
                  <div className="empty-panel">
                    <p>No test cases registered for this question yet. Add one on the right.</p>
                  </div>
                ) : (
                  <div className="test-cases-cards">
                    {questionTestCases.map((tc, idx) => (
                      <div className="tc-admin-card" key={tc.id || idx}>
                        <div className="tc-admin-header">
                          <span className="tc-admin-badge">Case #{idx + 1} ({tc.id})</span>
                          <div className="tc-admin-meta">
                            <span className={`pill ${tc.is_hidden ? 'pill-fail' : 'pill-success'}`}>
                              {tc.is_hidden ? 'Hidden Test' : 'Public Sample'}
                            </span>
                            <span className="pill pill-points">{tc.points} pts</span>
                          </div>
                        </div>
                        <div className="test-case-io-grid">
                          <div className="io-block">
                            <span className="io-label">stdin</span>
                            <pre className="io-box">{tc.stdin || '(empty)'}</pre>
                          </div>
                          <div className="io-block">
                            <span className="io-label">expected stdout</span>
                            <pre className="io-box">{tc.expected_stdout || '(empty)'}</pre>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Right: Add Test Case Form */}
            <div className="panel add-testcase-panel">
              <div className="panel-heading">
                <div>
                  <div className="eyebrow">Studio</div>
                  <h3>Add Test Case</h3>
                </div>
              </div>

              <form onSubmit={handleAddTestCase} className="admin-form">
                <label className="form-label">
                  <span>Standard Input (stdin)</span>
                  <textarea
                    className="form-input code-font"
                    rows={4}
                    placeholder="Input fed to program's standard input..."
                    value={newTestStdin}
                    onChange={(e) => setNewTestStdin(e.target.value)}
                  />
                </label>

                <label className="form-label">
                  <span>Expected Output (expected_stdout) *</span>
                  <textarea
                    className="form-input code-font"
                    rows={4}
                    placeholder="Exact expected standard output..."
                    value={newTestExpected}
                    onChange={(e) => setNewTestExpected(e.target.value)}
                    required
                  />
                </label>

                <div className="form-group-grid">
                  <label className="form-label">
                    <span>Points</span>
                    <input
                      type="number"
                      step="0.5"
                      className="form-input"
                      value={newTestPoints}
                      onChange={(e) => setNewTestPoints(e.target.value)}
                      required
                    />
                  </label>

                  <label className="checkbox-label" style={{ marginTop: '28px' }}>
                    <input
                      type="checkbox"
                      checked={newTestHidden}
                      onChange={(e) => setNewTestHidden(e.target.checked)}
                    />
                    <span>Hidden test case (private to evaluation)</span>
                  </label>
                </div>

                <button type="submit" className="primary-button full-width">
                  + Add Test Case
                </button>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Tab 4: Submissions */}
      {activeTab === 'submissions' && (
        <div className="faculty-tab-content">
          <div className="sub-header-bar">
            <div>
              <h3>Student Submissions Log</h3>
              <span className="muted">Inspect submitted code and trigger evaluations</span>
            </div>
          </div>

          <div className="table-responsive panel">
            <table className="modern-table">
              <thead>
                <tr>
                  <th>Submission ID</th>
                  <th>Student ID</th>
                  <th>Exam</th>
                  <th>Question</th>
                  <th>Language</th>
                  <th>Submitted At</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {submissions.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="empty-td">No submissions recorded yet.</td>
                  </tr>
                ) : (
                  submissions.map((sub) => (
                    <tr key={sub.id}>
                      <td><code>{sub.id}</code></td>
                      <td><strong>{sub.student_id}</strong></td>
                      <td>{sub.exam_id}</td>
                      <td>{sub.question_id}</td>
                      <td><span className="pill pill-lang">{sub.language}</span></td>
                      <td><small>{new Date(sub.submitted_at).toLocaleString()}</small></td>
                      <td>
                        <button
                          type="button"
                          className="action-btn-small"
                          onClick={() => handleInspectSubmission(sub)}
                        >
                          Inspect & Grade
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Exam Creator Modal */}
      {showExamModal && (
        <div className="modal-overlay" onClick={() => setShowExamModal(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Create New Laboratory Exam</h3>
              <button
                type="button"
                className="modal-close-btn"
                onClick={() => setShowExamModal(false)}
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateExam} className="admin-form">
              <label className="form-label">
                <span>Exam ID *</span>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g., exam-midterm-01"
                  value={newExamId}
                  onChange={(e) => setNewExamId(e.target.value)}
                  required
                />
              </label>

              <label className="form-label">
                <span>Exam Title *</span>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g., Algorithms Midterm Lab Assessment"
                  value={newExamTitle}
                  onChange={(e) => setNewExamTitle(e.target.value)}
                  required
                />
              </label>

              <label className="form-label">
                <span>Duration (minutes) *</span>
                <input
                  type="number"
                  className="form-input"
                  value={newExamDuration}
                  min={10}
                  max={300}
                  onChange={(e) => setNewExamDuration(e.target.value)}
                  required
                />
              </label>

              <div className="form-label">
                <div className="picker-header-row">
                  <span>Associate Questions from Bank</span>
                  <span className="selected-count-badge">
                    {selectedQuestionsForExam.length} of {questions.length} Selected
                  </span>
                </div>

                <div className="modal-picker-filters">
                  <select
                    className="form-input-sm"
                    value={modalDomainFilter}
                    onChange={(e) => setModalDomainFilter(e.target.value)}
                  >
                    <option value="ALL">All DSA Domains ({questions.length})</option>
                    <option value="Arrays">Arrays</option>
                    <option value="Strings">Strings</option>
                    <option value="Stacks">Stacks</option>
                    <option value="Queues">Queues</option>
                    <option value="Linked Lists">Linked Lists</option>
                    <option value="Trees">Trees</option>
                    <option value="Graphs">Graphs</option>
                    <option value="Dynamic Programming">Dynamic Programming</option>
                  </select>

                  <select
                    className="form-input-sm"
                    value={modalDiffFilter}
                    onChange={(e) => setModalDiffFilter(e.target.value)}
                  >
                    <option value="ALL">All Levels</option>
                    <option value="L1">Level 1 (L1 - Foundational)</option>
                    <option value="L2">Level 2 (L2 - Intermediate)</option>
                    <option value="L3">Level 3 (L3 - Advanced)</option>
                  </select>
                </div>

                <div className="questions-picker-list">
                  {questions
                    .filter((q) => {
                      const matchDomain = modalDomainFilter === 'ALL' || (q.domain || 'Algorithms') === modalDomainFilter;
                      const matchDiff = modalDiffFilter === 'ALL' || (q.difficulty || 'L1') === modalDiffFilter;
                      return matchDomain && matchDiff;
                    })
                    .map((q) => {
                      const isSelected = selectedQuestionsForExam.includes(q.id);
                      const diffLevel = q.difficulty || 'L1';
                      return (
                        <label key={q.id} className={`checkbox-item question-picker-item ${isSelected ? 'is-selected' : ''}`}>
                          <input
                            type="checkbox"
                            checked={isSelected}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedQuestionsForExam((prev) => [...prev, q.id]);
                              } else {
                                setSelectedQuestionsForExam((prev) => prev.filter((id) => id !== q.id));
                              }
                            }}
                          />
                          <div className="q-picker-row">
                            <span className={`diff-badge diff-${diffLevel.toLowerCase()}`}>
                              {diffLevel}
                            </span>
                            <span className="domain-pill-sm">
                              {q.domain || 'Algorithms'}
                            </span>
                            <span className="q-title-bold">{q.title}</span>
                            <span className="q-points-sm">({q.points ?? 10} pts)</span>
                            <code className="q-id-code">({q.id})</code>
                          </div>
                        </label>
                      );
                    })}
                </div>
              </div>

              <div className="modal-actions">
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => setShowExamModal(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="primary-button">
                  Create Exam
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Manual Question Creator Modal */}
      {showQuestionModal && (
        <div className="modal-overlay" onClick={() => setShowQuestionModal(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Create Question Manually</h3>
              <button
                type="button"
                className="modal-close-btn"
                onClick={() => setShowQuestionModal(false)}
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateQuestion} className="admin-form">
              <div className="form-group-grid">
                <label className="form-label">
                  <span>Question ID *</span>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g., q-arrays-001"
                    value={newQId}
                    onChange={(e) => setNewQId(e.target.value)}
                    required
                  />
                </label>

                <label className="form-label">
                  <span>Title *</span>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g., Reverse an Array"
                    value={newQTitle}
                    onChange={(e) => setNewQTitle(e.target.value)}
                    required
                  />
                </label>
              </div>

              <label className="form-label">
                <span>Problem Prompt & Instructions *</span>
                <textarea
                  className="form-input"
                  rows={5}
                  placeholder="Describe the problem, input/output formats, and constraints..."
                  value={newQPrompt}
                  onChange={(e) => setNewQPrompt(e.target.value)}
                  required
                />
              </label>

              <div className="form-group-grid">
                <label className="form-label">
                  <span>Domain</span>
                  <select
                    className="form-input"
                    value={newQDomain}
                    onChange={(e) => setNewQDomain(e.target.value)}
                  >
                    <option value="Arrays">Arrays</option>
                    <option value="Strings">Strings</option>
                    <option value="Stacks">Stacks</option>
                    <option value="Queues">Queues</option>
                    <option value="Linked Lists">Linked Lists</option>
                    <option value="Trees">Trees</option>
                    <option value="Graphs">Graphs</option>
                    <option value="Dynamic Programming">Dynamic Programming</option>
                  </select>
                </label>

                <label className="form-label">
                  <span>Difficulty Level</span>
                  <select
                    className="form-input"
                    value={newQDiff}
                    onChange={(e) => setNewQDiff(e.target.value)}
                  >
                    <option value="L1">L1 (Foundational / Easy)</option>
                    <option value="L2">L2 (Intermediate / Medium)</option>
                    <option value="L3">L3 (Advanced / Hard)</option>
                  </select>
                </label>
              </div>

              <div className="form-group-grid">
                <label className="form-label">
                  <span>Language</span>
                  <select
                    className="form-input"
                    value={newQLang}
                    onChange={(e) => setNewQLang(e.target.value)}
                  >
                    <option value="python">Python</option>
                    <option value="cpp">C++</option>
                    <option value="java">Java</option>
                  </select>
                </label>

                <label className="form-label">
                  <span>Points</span>
                  <input
                    type="number"
                    className="form-input"
                    value={newQPoints}
                    min={1}
                    max={100}
                    onChange={(e) => setNewQPoints(e.target.value)}
                  />
                </label>
              </div>

              <div className="modal-actions">
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => setShowQuestionModal(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="primary-button">
                  Save Question
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Submission Inspector Modal */}
      {inspectedSub && (
        <div className="modal-overlay" onClick={() => setInspectedSub(null)}>
          <div className="modal-card wide-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <div className="eyebrow">Submission Inspector</div>
                <h3>{inspectedSub.id} by {inspectedSub.student_id}</h3>
              </div>
              <button
                type="button"
                className="modal-close-btn"
                onClick={() => setInspectedSub(null)}
              >
                ✕
              </button>
            </div>

            <div className="sub-inspect-grid">
              <div className="sub-code-block">
                <div className="code-header">
                  <span>Submitted Source Code ({inspectedSub.language})</span>
                </div>
                <pre className="code-display">{inspectedSub.source_code}</pre>
              </div>

              <div className="sub-eval-block">
                <div className="eval-status-box">
                  <h4>Evaluation Report</h4>
                  {inspectedEval ? (
                    <div className="eval-details">
                      <div className="eval-score-pill">
                        Score: <strong>{inspectedEval.score} pts</strong> ({inspectedEval.passed}/{inspectedEval.total} Passed)
                      </div>
                      <pre className="eval-feedback-log">{inspectedEval.feedback}</pre>
                    </div>
                  ) : (
                    <p className="muted">No evaluation record found for this submission.</p>
                  )}

                  <button
                    type="button"
                    className="primary-button full-width"
                    onClick={() => handleReEvaluateSubmission(inspectedSub.id)}
                    disabled={evaluatingSub}
                  >
                    {evaluatingSub ? 'Evaluating Code in Sandbox…' : '⚡ Run Evaluation Now'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
