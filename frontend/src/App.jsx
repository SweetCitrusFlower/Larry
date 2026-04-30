import React, { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import axios from 'axios';

function App() {
  const [status, setStatus] = useState('Checking backend status...');

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

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>AI Coding Coaching Platform</h1>
      <p>Backend Status: <strong>{status}</strong></p>
      
      <div style={{ marginTop: '20px', border: '1px solid #ccc', height: '400px' }}>
        <Editor
          height="100%"
          defaultLanguage="python"
          defaultValue="# Write your python code here"
        />
      </div>
    </div>
  );
}

export default App;
