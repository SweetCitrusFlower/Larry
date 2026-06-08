import React from 'react';
import Editor from '@monaco-editor/react';
import useFrustrationDetector from '../hooks/useFrustrationDetector';

const EditorPane = ({ language, code, setCode }) => {
  const trackChange = useFrustrationDetector({
    lineThreshold: 10,
    timeWindowMs: 60000,
    triggerCount: 3,
    cooldownMs: 60000,
    onFrustrationDetected: () => {
      console.log("Utility Agent Alert: Massive code deletions detected.");
      alert("Utility Agent: I noticed you're deleting a lot of code. Are you having difficulties? Let me know if I can help!");
    }
  });

  const handleChange = (value) => {
    setCode(value);
    trackChange(value);
  };

  return (
    <div className="editor-pane">
      <div className="pane-header">
        <span className="file-tab active">
          main.py
        </span>
      </div>
      <div className="editor-container">
        <Editor
          height="100%"
          language={language}
          value={code}
          theme="vs-dark"
          onChange={handleChange}
          options={{
            fontSize: 14,
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            automaticLayout: true,
            padding: { top: 16 },
            backgroundColor: '#0f172a'
          }}
        />
      </div>

    </div>
  );
};

export default EditorPane;
