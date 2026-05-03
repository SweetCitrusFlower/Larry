import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import EditorPane from './components/EditorPane';
import ConsolePane from './components/ConsolePane';
import ChatPane from './components/ChatPane';
import AuthModal from './components/AuthModal';

function App() {
  const [language, setLanguage] = useState('python');
  const [code, setCode] = useState('# Write your code here\nprint("Hello Larry!")');
  const [output, setOutput] = useState('');
  const [input, setInput] = useState('');
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

  return (
    <div className="app-container">
      <Navbar 
        language={language} 
        setLanguage={setLanguage} 
        onLoginClick={() => setIsAuthModalOpen(true)}
      />
      
      <main className="main-layout">
        <Sidebar />
        
        <div className="center-pane">
          <EditorPane 
            language={language} 
            code={code} 
            setCode={setCode} 
          />
          <ConsolePane 
            output={output} 
            input={input} 
            setInput={setInput} 
          />
        </div>
        
        <ChatPane />
      </main>

      <AuthModal 
        isOpen={isAuthModalOpen} 
        onClose={() => setIsAuthModalOpen(false)} 
      />

    </div>
  );
}

export default App;
