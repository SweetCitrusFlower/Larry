import React from 'react';

const ConsolePane = ({ output, input, setInput }) => {
  return (
    <div className="console-pane">
      <div className="pane-header">
        <div className="tabs">
          <span className="tab active">Output</span>
          <span className="tab">Terminal</span>
        </div>
        <button className="clear-btn">Clear</button>
      </div>
      <div className="console-content">
        <pre className="output-text">
          {output || '> Waiting for execution...'}
        </pre>
      </div>
      <div className="console-input">
        <span className="prompt">$</span>
        <input 
          type="text" 
          value={input} 
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a command..."
        />
      </div>

    </div>
  );
};

export default ConsolePane;
