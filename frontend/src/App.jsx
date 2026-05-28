import React, { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import axios from 'axios';
import FavoriteButton from './components/FavoriteButton';
import FavoritesPanel from './components/FavoritesPanel';

function App() {
  const [status, setStatus] = useState('Checking backend status...');
  const [isFavoritesOpen, setIsFavoritesOpen] = useState(false);

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
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>AI Coding Coaching Platform</h1>
        <button 
          onClick={() => setIsFavoritesOpen(true)}
          style={{ padding: '8px 16px', background: '#007bff', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
        >
          Show Favorites
        </button>
      </div>
      <p>Backend Status: <strong>{status}</strong></p>
      
      <div style={{ marginTop: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '10px' }}>
          <h3 style={{ margin: 0, marginRight: '10px' }}>main.py</h3>
          <FavoriteButton itemType="code" itemContent="# Write your python code here\nprint('Hello World')" />
        </div>
        <div style={{ border: '1px solid #ccc', height: '400px' }}>
          <Editor
            height="100%"
            defaultLanguage="python"
            defaultValue="# Write your python code here\nprint('Hello World')"
          />
        </div>
      </div>

      <FavoritesPanel 
        isOpen={isFavoritesOpen} 
        onClose={() => setIsFavoritesOpen(false)} 
      />
    </div>
  );
}

export default App;
