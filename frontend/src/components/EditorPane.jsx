import React, { useCallback } from 'react';
import Editor from '@monaco-editor/react';
import useFrustrationDetector from '../hooks/useFrustrationDetector';
import useEditorActivity from '../hooks/useEditorActivity';

const EditorPane = ({ language, code, setCode, onActivityDetected = null }) => {
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

  // Track editor activity for idle assistance
  const { handleEditorActivity } = useEditorActivity(
    240000, // 4 minutes
    onActivityDetected // Callback when idle threshold is reached
  );

  const handleChange = useCallback((value) => {
    setCode(value);
    trackChange(value);
    handleEditorActivity(); // Track this activity
  }, [setCode, trackChange, handleEditorActivity]);

  return (
    <div className="flex-1 flex flex-col w-full h-full min-h-0">
      <div className="flex-1 relative min-h-0 w-full">
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
            padding: { top: 16 }
          }}
        />
      </div>
    </div>
  );
};

export default EditorPane;
