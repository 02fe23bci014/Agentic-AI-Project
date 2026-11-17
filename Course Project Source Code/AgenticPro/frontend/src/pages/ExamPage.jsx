import { useState, useEffect } from 'react';
import CodeEditor from '../components/CodeEditor.jsx';
import QuestionPanel from '../components/QuestionPanel.jsx';
import ResultPanel from '../components/ResultPanel.jsx';
import TestCasePanel from '../components/TestCasePanel.jsx';
import { api } from '../services/api';

const DEFAULT_PYTHON_CODE = `# Solution in Python
import sys

def main():
    lines = sys.stdin.read().split()
    if not lines:
        return
    a = int(lines[0])
    b = int(lines[1])
    print(a + b)

if __name__ == '__main__':
    main()
`;

export default function ExamPage({ exam: initialExam, onExit, currentStudentId = 'student-test-001' }) {
  const [exam, setExam] = useState(initialExam);
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [testCases, setTestCases] = useState([]);
  const [loading, setLoading] = useState(true);

  // Per-question code states
  const [codeByQuestion, setCodeByQuestion] = useState({});
  const [languageByQuestion, setLanguageByQuestion] = useState({});
  const [customInput, setCustomInput] = useState('');
  const [showCustomInput, setShowCustomInput] = useState(false);

  // Execution states
  const [evalResult, setEvalResult] = useState(null);
  const [running, setRunning] = useState(false);
  const [runType, setRunType] = useState('eval'); // 'test' | 'eval'

  // Timer state
  const durationSec = (exam?.duration_minutes ?? 60) * 60;
  const [timeLeft, setTimeLeft] = useState(durationSec);

  useEffect(() => {
    loadExamData();
  }, [initialExam]);

  // Countdown timer effect
  useEffect(() => {
    if (timeLeft <= 0) return;
    const timer = setInterval(() => {
      setTimeLeft((t) => Math.max(0, t - 1));
    }, 1000);
    return () => clearInterval(timer);
  }, [timeLeft]);

  const loadExamData = async () => {
    setLoading(true);
    try {
      let activeExam = initialExam;
      if (!activeExam) {
        const exams = await api.getExams();
        activeExam = exams[0];
      }

      if (!activeExam) {
        throw new Error('No exam found');
      }

      setExam(activeExam);

      // Fetch all question IDs for this exam
      const qIds = activeExam.question_ids || [];
      const loadedQuestions = [];

      for (const qId of qIds) {
        try {
          const q = await api.getQuestion(qId);
          loadedQuestions.push(q);
        } catch {
          // Fallback if not found
          loadedQuestions.push({
            id: qId,
            title: `Question ${qId}`,
            prompt: 'Solve the required programming exercise for this exam.',
            language: 'python',
            points: 10,
          });
        }
      }

      setQuestions(loadedQuestions);

      // Initialize code templates for each question
      const initialCode = {};
      const initialLang = {};
      loadedQuestions.forEach((q) => {
        initialCode[q.id] = DEFAULT_PYTHON_CODE;
        initialLang[q.id] = q.language || 'python';
      });
      setCodeByQuestion(initialCode);
      setLanguageByQuestion(initialLang);

      // Load test cases for the first question
      if (loadedQuestions.length > 0) {
        loadQuestionTestCases(loadedQuestions[0].id);
      }
    } catch (err) {
      console.error('Failed to load exam:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadQuestionTestCases = async (questionId) => {
    try {
      const cases = await api.getTestCases(questionId, true);
      setTestCases(cases);
      const firstPublic = cases.find((c) => !c.is_hidden);
      if (firstPublic && firstPublic.stdin) {
        setCustomInput(firstPublic.stdin);
      }
    } catch {
      setTestCases([]);
    }
  };

  const handleSelectQuestion = (index) => {
    setCurrentQuestionIndex(index);
    setEvalResult(null);
    const q = questions[index];
    if (q) {
      loadQuestionTestCases(q.id);
    }
  };

  const currentQuestion = questions[currentQuestionIndex];
  const currentCode = currentQuestion ? codeByQuestion[currentQuestion.id] || DEFAULT_PYTHON_CODE : '';
  const currentLang = currentQuestion ? languageByQuestion[currentQuestion.id] || 'python' : 'python';

  const handleCodeChange = (newCode) => {
    if (!currentQuestion) return;
    setCodeByQuestion((prev) => ({
      ...prev,
      [currentQuestion.id]: newCode,
    }));
  };

  const handleLanguageChange = (newLang) => {
    if (!currentQuestion) return;
    setLanguageByQuestion((prev) => ({
      ...prev,
      [currentQuestion.id]: newLang,
    }));
  };

  // Run code against custom stdin (Quick Test)
  const handleRunCode = async () => {
    if (!currentQuestion) return;
    setRunning(true);
    setRunType('test');
    try {
      const res = await api.runCodeDirectly({
        source_code: currentCode,
        language: currentLang,
        stdin: customInput,
      });
      setEvalResult({
        type: 'run_code',
        stdout: res.stdout,
        stderr: res.stderr,
        returncode: res.returncode,
        timed_out: res.timed_out,
      });
    } catch (err) {
      setEvalResult({
        type: 'run_code',
        stdout: '',
        stderr: err.message || 'Execution failed',
        returncode: 1,
        timed_out: false,
      });
    } finally {
      setRunning(false);
    }
  };

  // Full submission & evaluation
  const handleSubmitSolution = async () => {
    if (!currentQuestion || !exam) return;
    setRunning(true);
    setRunType('eval');
    try {
      const submissionId = `sub-${crypto.randomUUID().slice(0, 8)}`;
      // 1. Post submission
      await api.submit({
        id: submissionId,
        exam_id: exam.id,
        question_id: currentQuestion.id,
        student_id: currentStudentId,
        language: currentLang,
        source_code: currentCode,
        submitted_at: new Date().toISOString(),
      });

      // 2. Trigger automated evaluation
      const evaluation = await api.runEvaluation(submissionId);
      setEvalResult({
        type: 'eval_complete',
        ...evaluation,
      });
    } catch (err) {
      setEvalResult({
        type: 'eval_complete',
        status: 'error',
        score: 0,
        passed: 0,
        total: testCases.length,
        feedback: `Submission evaluation error: ${err.message}`,
      });
    } finally {
      setRunning(false);
    }
  };

  // Format countdown mm:ss
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="page-content exam-loading-state">
        <div className="spinner" />
        <h2>Initializing Laboratory Workspace...</h2>
      </div>
    );
  }

  return (
    <section className="page-content exam-layout">
      {/* Top Exam Navigation Bar */}
      <div className="exam-top-banner">
        <div className="exam-banner-left">
          <button type="button" className="back-link-btn" onClick={onExit}>
            ← Back to Dashboard
          </button>
          <div>
            <div className="eyebrow">{exam?.id}</div>
            <h1 className="exam-heading-title">{exam?.title || 'Programming Lab Assessment'}</h1>
          </div>
        </div>

        <div className="exam-banner-right">
          <div className={`exam-timer-pill ${timeLeft < 300 ? 'timer-critical' : ''}`}>
            <span className="timer-icon" aria-hidden="true">⏱</span>
            <span className="timer-digits">{formatTime(timeLeft)}</span>
            <small className="timer-sub">REMAINING</small>
          </div>
        </div>
      </div>

      {/* Question Selector Tabs */}
      <div className="exam-question-nav">
        <div className="nav-tabs-list">
          {questions.map((q, idx) => (
            <button
              key={q.id || idx}
              type="button"
              className={`question-nav-tab ${currentQuestionIndex === idx ? 'active' : ''}`}
              onClick={() => handleSelectQuestion(idx)}
            >
              <span className="q-nav-num">Ex {idx + 1}</span>
              <span className="q-nav-title">{q.title || `Problem ${idx + 1}`}</span>
              <span className="q-nav-pts">{q.points ?? 10}p</span>
            </button>
          ))}
        </div>
      </div>

      {/* Main 2-Column Split Workspace */}
      <div className="exam-grid">
        {/* Left Column: Problem description & Test Cases */}
        <div className="exam-sidebar">
          <QuestionPanel
            question={currentQuestion}
            onApplyExample={(input) => {
              setCustomInput(input);
              setShowCustomInput(true);
            }}
          />

          <TestCasePanel
            cases={testCases}
            onSelectCase={(input) => {
              setCustomInput(input);
              setShowCustomInput(true);
            }}
          />
        </div>

        {/* Right Column: Code Editor & Execution Results */}
        <div className="editor-column">
          <CodeEditor
            value={currentCode}
            onChange={handleCodeChange}
            language={currentLang}
            onLanguageChange={handleLanguageChange}
          />

          {/* Custom Input Accordion */}
          <div className="custom-input-section">
            <button
              type="button"
              className="toggle-custom-input-btn"
              onClick={() => setShowCustomInput(!showCustomInput)}
            >
              <span>{showCustomInput ? '▼ Hide Custom Test Input' : '▶ Test with Custom Input (stdin)'}</span>
              <span className="toggle-hint">Useful for debugging edge cases</span>
            </button>

            {showCustomInput && (
              <div className="custom-input-box">
                <textarea
                  className="custom-stdin-textarea"
                  placeholder="Enter inputs here as they will be supplied to stdin..."
                  value={customInput}
                  onChange={(e) => setCustomInput(e.target.value)}
                  rows={3}
                />
              </div>
            )}
          </div>

          {/* Action Bar */}
          <div className="editor-actions-bar">
            <div className="editor-env-info">
              <span className="env-dot" />
              <span>Isolated Sandbox Runtime: {currentLang.toUpperCase()}</span>
            </div>

            <div className="editor-btn-group">
              <button
                type="button"
                className="secondary-button"
                onClick={handleRunCode}
                disabled={running}
                title="Execute code directly against custom stdin"
              >
                {running && runType === 'test' ? 'Testing…' : '▶ Run Code'}
              </button>

              <button
                type="button"
                className="primary-button"
                onClick={handleSubmitSolution}
                disabled={running}
                title="Submit solution to evaluate against all test cases"
              >
                {running && runType === 'eval' ? 'Grading…' : '✓ Submit Solution'}
              </button>
            </div>
          </div>

          {/* Evaluation & Result Output Panel */}
          <ResultPanel
            result={evalResult}
            running={running}
            runType={runType}
            questionPoints={currentQuestion?.points ?? 10}
          />
        </div>
      </div>
    </section>
  );
}
