import React, { useState, useEffect, useRef } from 'react';
import Editor from '@monaco-editor/react';
import axios from 'axios';
import TourGuide from './components/TourGuide';

function App() {
  const [status, setStatus] = useState('Checking backend status...');
  const tourRef = useRef();

  useEffect(() => {
    axios.get('http://127.0.0.1:8000')
      .then(response => {
        setStatus(response.data.status);
      })
      .catch(error => {
        setStatus('Backend is not reachable');
        console.error(error);
      });
  }, []);

  const handleReplayTour = () => {
    if (tourRef.current) {
      tourRef.current.startTour();
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif', height: '100vh', display: 'flex', flexDirection: 'column', boxSizing: 'border-box' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>AI Coding Coaching Platform</h1>
          <p>Backend Status: <strong>{status}</strong></p>
        </div>
        <button 
          onClick={handleReplayTour} 
          style={{ padding: '10px 15px', backgroundColor: '#007ACC', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
        >
          Help / Replay Tour
        </button>
      </div>
      
      <TourGuide ref={tourRef} />

      <div style={{ display: 'flex', flex: 1, marginTop: '20px', gap: '20px' }}>
        {/* Editor Pane */}
        <div className="tour-editor" style={{ flex: 2, border: '1px solid #ccc', display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ margin: 0, padding: '10px', backgroundColor: '#f5f5f5', borderBottom: '1px solid #ccc' }}>Code Editor</h3>
          <div style={{ flex: 1 }}>
            <Editor
              height="100%"
              defaultLanguage="python"
              defaultValue="# Write your python code here"
            />
          </div>
        </div>

        {/* Side Pane for Chat and Console */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* Chat Pane */}
          <div className="tour-chat" style={{ flex: 1, border: '1px solid #ccc', display: 'flex', flexDirection: 'column' }}>
            <h3 style={{ margin: 0, padding: '10px', backgroundColor: '#f5f5f5', borderBottom: '1px solid #ccc' }}>AI Tutor Chat</h3>
            <div style={{ flex: 1, padding: '10px', backgroundColor: '#2d2d2d', color: '#fff', overflowY: 'auto' }}>
              <p>Welcome! How can I help you today?</p>
              {/* Chat messages would go here */}
            </div>
          </div>
          
          {/* Console Pane */}
          <div className="tour-console" style={{ height: '300px', border: '1px solid #ccc', display: 'flex', flexDirection: 'column' }}>
            <h3 style={{ margin: 0, padding: '10px', backgroundColor: '#f5f5f5', borderBottom: '1px solid #ccc' }}>Execution Console</h3>
            <div style={{ flex: 1, padding: '10px', backgroundColor: '#000', color: '#00FF00', fontFamily: 'monospace' }}>
              $ Console output will appear here...
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}

export default App;
