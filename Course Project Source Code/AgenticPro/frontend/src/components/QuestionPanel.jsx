import { useState } from 'react';

export default function QuestionPanel({ question, onApplyExample }) {
  const [activeTab, setActiveTab] = useState('problem');

  if (!question) {
    return (
      <div className="panel question-panel">
        <div className="empty-state">No question selected.</div>
      </div>
    );
  }

  // Parse prompt for structured sections if present
  const promptText = question.prompt || '';

  return (
    <section className="panel question-panel" aria-labelledby="question-heading">
      <div className="question-header">
        <div className="eyebrow">Exercise</div>
        <div className="question-meta-pills">
          <span className={`pill pill-diff diff-${(question.difficulty || 'L1').toLowerCase()}`}>
            Level: {question.difficulty || 'L1'}
          </span>
          <span className="pill pill-domain">
            {question.domain || 'Algorithms'}
          </span>
          <span className="pill pill-points">{question.points ?? 10} Points</span>
          <span className="pill pill-lang">{question.language ?? 'python'}</span>
          <span className="pill pill-id">{question.id}</span>
        </div>
      </div>

      <h2 id="question-heading" className="question-title">
        {question.title ?? 'Untitled Problem'}
      </h2>

      <div className="panel-tab-bar">
        <button
          type="button"
          className={`panel-tab-btn ${activeTab === 'problem' ? 'active' : ''}`}
          onClick={() => setActiveTab('problem')}
        >
          Problem Statement
        </button>
        <button
          type="button"
          className={`panel-tab-btn ${activeTab === 'spec' ? 'active' : ''}`}
          onClick={() => setActiveTab('spec')}
        >
          Specifications & Formats
        </button>
      </div>

      <div className="question-body">
        {activeTab === 'problem' ? (
          <div className="problem-content">
            <div className="prompt-text">
              {promptText.split('\n\n').map((paragraph, index) => {
                if (paragraph.startsWith('Input format:') || paragraph.startsWith('Output format:')) {
                  return (
                    <div key={index} className="format-callout">
                      <strong>{paragraph.split('\n')[0]}</strong>
                      <p>{paragraph.split('\n').slice(1).join('\n') || paragraph}</p>
                    </div>
                  );
                }
                return <p key={index}>{paragraph}</p>;
              })}
            </div>
          </div>
        ) : (
          <div className="spec-content">
            <div className="spec-card">
              <h4>Input Format</h4>
              <p>Standard input stream (stdin). Read values separated by spaces or newlines.</p>
            </div>
            <div className="spec-card">
              <h4>Output Format</h4>
              <p>Standard output stream (stdout). Ensure no extraneous trailing prompts are printed.</p>
            </div>
            <div className="spec-card">
              <h4>Constraints</h4>
              <ul>
                <li>Execution time limit: 5.0 seconds per test case</li>
                <li>Memory limit: 256 MB</li>
                <li>Environment: Isolated sandbox runtime</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
