import React, { useState } from 'react';

const ChatPane = () => {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I am Larry, your AI coding assistant. How can I help you today?' }
  ]);
  const [input, setInput] = useState('');

  const sendMessage = () => {
    if (!input.trim()) return;
    const newMessages = [...messages, { role: 'user', content: input }];
    setMessages(newMessages);
    setInput('');
    
    // Mock response
    setTimeout(() => {
      setMessages([...newMessages, { role: 'assistant', content: "I'm processing your request. I can help with code analysis, bug fixing, or writing new functions." }]);
    }, 1000);
  };

  return (
    <aside className="chat-pane">
      <div className="chat-header">
        <div className="status-dot"></div>
        <h3>AI ASSISTANT</h3>
      </div>
      <div className="messages-list">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            <div className="msg-avatar">
              {msg.role === 'assistant' ? 'AI' : 'U'}
            </div>
            <div className="msg-bubble">
              {msg.content}
            </div>
          </div>
        ))}
      </div>
      <div className="chat-footer">
        <div className="quick-actions">
          <button>Explain</button>
          <button>Fix Bugs</button>
          <button>Optimize</button>
        </div>
        <div className="chat-input-wrapper">
          <textarea 
            placeholder="Ask Larry something..." 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), sendMessage())}
          />
          <button className="send-btn" onClick={sendMessage}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
          </button>
        </div>
      </div>

    </aside>
  );
};

export default ChatPane;
