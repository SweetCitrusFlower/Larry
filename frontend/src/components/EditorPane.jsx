import React from 'react';
import Editor from '@monaco-editor/react';

const EditorPane = ({ language, code, setCode }) => {
  return (
    <div className="flex-1 flex flex-col w-full h-full min-h-0">
      <div className="flex-1 relative min-h-0 w-full">
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
            padding: { top: 16 }
          }}
        />
      </div>
    </div>
  );
};

export default EditorPane;
