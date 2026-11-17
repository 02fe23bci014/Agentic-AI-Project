import { useState, useRef, useEffect } from 'react';

const STARTER_TEMPLATES = {
  python: `# Python 3.10+ Solution
import sys

def solve():
    # Read input from stdin
    input_data = sys.stdin.read().split()
    if not input_data:
        return
    
    # Process inputs and output result
    a = int(input_data[0])
    b = int(input_data[1])
    print(a + b)

if __name__ == '__main__':
    solve()
`,
  cpp: `// C++ 17 Solution
#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int a, b;
    if (cin >> a >> b) {
        cout << (a + b) << "\\n";
    }
    return 0;
}
`,
  java: `// Java Solution
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextInt()) {
            int a = sc.nextInt();
            int b = sc.nextInt();
            System.out.println(a + b);
        }
    }
}
`,
};

export default function CodeEditor({
  value,
  onChange,
  language = 'python',
  onLanguageChange,
  readOnly = false,
}) {
  const [fontSize, setFontSize] = useState(13);
  const textareaRef = useRef(null);

  // Calculate lines for gutter
  const lineCount = (value || '').split('\n').length;
  const lineNumbers = Array.from({ length: Math.max(lineCount, 12) }, (_, i) => i + 1);

  // Handle Tab key indentation inside textarea
  const handleKeyDown = (e) => {
    if (readOnly) return;
    if (e.key === 'Tab') {
      e.preventDefault();
      const textarea = textareaRef.current;
      if (!textarea) return;

      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;

      // Insert 4 spaces
      const updatedValue = value.substring(0, start) + '    ' + value.substring(end);
      onChange(updatedValue);

      // Move cursor
      setTimeout(() => {
        textarea.selectionStart = textarea.selectionEnd = start + 4;
      }, 0);
    }
  };

  const resetToTemplate = () => {
    const template = STARTER_TEMPLATES[language] || STARTER_TEMPLATES.python;
    onChange(template);
  };

  const copyCode = async () => {
    try {
      await navigator.clipboard.writeText(value);
      alert('Code copied to clipboard!');
    } catch {
      // Fallback
      textareaRef.current?.select();
      document.execCommand('copy');
      alert('Code copied to clipboard!');
    }
  };

  return (
    <div className="code-editor-wrapper">
      <div className="editor-toolbar">
        <div className="editor-toolbar-left">
          <label className="toolbar-label">
            <span>Language</span>
            <select
              className="toolbar-select"
              value={language}
              onChange={(e) => onLanguageChange && onLanguageChange(e.target.value)}
              disabled={readOnly}
            >
              <option value="python">Python 3.10</option>
              <option value="cpp">C++ 17</option>
              <option value="java">Java 21</option>
            </select>
          </label>
          <span className="editor-badge">{language.toUpperCase()}</span>
        </div>

        <div className="editor-toolbar-right">
          <div className="font-size-controls">
            <button
              type="button"
              className="icon-button"
              title="Decrease font size"
              onClick={() => setFontSize((s) => Math.max(11, s - 1))}
            >
              A-
            </button>
            <span className="font-size-indicator">{fontSize}px</span>
            <button
              type="button"
              className="icon-button"
              title="Increase font size"
              onClick={() => setFontSize((s) => Math.min(18, s + 1))}
            >
              A+
            </button>
          </div>

          {!readOnly && (
            <button
              type="button"
              className="toolbar-button"
              onClick={resetToTemplate}
              title="Reset code to starter boilerplate"
            >
              Reset Template
            </button>
          )}

          <button
            type="button"
            className="toolbar-button"
            onClick={copyCode}
            title="Copy code"
          >
            Copy
          </button>
        </div>
      </div>

      <div className="editor-container" style={{ fontSize: `${fontSize}px` }}>
        <div className="editor-gutter" aria-hidden="true">
          {lineNumbers.map((num) => (
            <div key={num} className="gutter-line-number">
              {num}
            </div>
          ))}
        </div>

        <textarea
          ref={textareaRef}
          className="code-textarea"
          spellCheck="false"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          readOnly={readOnly}
          aria-label="Code editor"
        />
      </div>

      <div className="editor-statusbar">
        <span>Lines: {lineCount}</span>
        <span>Characters: {(value || '').length}</span>
        <span>Encoding: UTF-8</span>
      </div>
    </div>
  );
}
