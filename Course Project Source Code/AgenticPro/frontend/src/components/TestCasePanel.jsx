export default function TestCasePanel({ cases = [], onSelectCase }) {
  const displayCases = cases.length > 0 ? cases : [
    { id: 'sample-1', stdin: '2\n3', expected_stdout: '5', points: 5, is_hidden: false },
    { id: 'sample-2', stdin: '-4\n9', expected_stdout: '5', points: 5, is_hidden: false },
  ];

  const publicCases = displayCases.filter((c) => !c.is_hidden);
  const hiddenCount = displayCases.filter((c) => c.is_hidden).length;

  return (
    <section className="panel testcase-panel" aria-labelledby="tests-heading">
      <div className="panel-heading">
        <div>
          <div className="eyebrow">Verification</div>
          <h3 id="tests-heading">Test Cases</h3>
        </div>
        <div className="test-meta-badge">
          <span>{publicCases.length} Visible</span>
          {hiddenCount > 0 && <span className="hidden-pill">+{hiddenCount} Hidden</span>}
        </div>
      </div>

      <div className="test-case-list">
        {publicCases.map((testCase, index) => (
          <div className="test-case-card" key={testCase.id || index}>
            <div className="test-case-header">
              <span className="case-badge">Case {index + 1}</span>
              <span className="case-points">{testCase.points ?? 1} pt</span>
              {onSelectCase && (
                <button
                  type="button"
                  className="case-action-btn"
                  onClick={() => onSelectCase(testCase.stdin)}
                  title="Load input into custom tester"
                >
                  Use as Input
                </button>
              )}
            </div>

            <div className="test-case-io-grid">
              <div className="io-block">
                <span className="io-label">Input</span>
                <pre className="io-box">{testCase.stdin || '(empty)'}</pre>
              </div>
              <div className="io-block">
                <span className="io-label">Expected Output</span>
                <pre className="io-box">{testCase.expected_stdout || '(empty)'}</pre>
              </div>
            </div>
          </div>
        ))}

        {hiddenCount > 0 && (
          <div className="hidden-cases-note">
            <span className="lock-icon" aria-hidden="true">🔒</span>
            <div>
              <strong>{hiddenCount} Hidden Test Cases</strong>
              <small>Evaluated automatically when you submit for grading.</small>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
