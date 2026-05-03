import React from 'react';
import Editor from '@monaco-editor/react';

const EditorPane = ({ language, code, setCode }) => {
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
          onChange={(value) => setCode(value)}
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
