import React, { useState, useRef, useEffect } from 'react';
import { chatAPI, journeysAPI } from '../services/api';
import { Send, Sparkles, Loader2, User, Bot } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const ChatPane = ({ onRoadmapGenerated }) => {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: "Hi, I'm Larry. What would you like to learn today? Tell me the topic and how many days you have." }
  ]);
  const [input, setInput] = useState('');
  const [days, setDays] = useState(7);
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = { 
      role: 'user', 
      content: `I want to learn ${input} in ${days} days.` 
    };
    
    setMessages(prev => [...prev, userMessage]);
    const currentInput = input;
    setInput('');
    setLoading(true);

    try {
      // Use the dedicated journeys generation endpoint
      const response = await journeysAPI.generateJourney({
        prompt: currentInput,
        target_days: parseInt(days, 10)
      });

      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: "I've generated your roadmap! Check it out below." 
      }]);

      if (response.data) {
        onRoadmapGenerated(response.data);
      }
    } catch (err) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: "Sorry, I encountered an error. Please try again later." 
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full glass-card overflow-hidden">
      <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/50">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <h3 className="font-bold text-sm tracking-widest text-slate-400">LARRY AI</h3>
        </div>
        <Sparkles size={18} className="text-blue-400" />
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-hide">
        {messages.map((msg, idx) => (
          <motion.div 
            key={idx}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`max-w-[85%] flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${msg.role === 'user' ? 'bg-blue-600' : 'bg-slate-800'}`}>
                {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
              </div>
              <div className={`p-3 rounded-2xl text-sm leading-relaxed ${
                msg.role === 'user' 
                ? 'bg-blue-600 text-white rounded-tr-none' 
                : 'bg-slate-800 text-slate-200 rounded-tl-none border border-slate-700'
              }`}>
                {msg.content}
              </div>
            </div>
          </motion.div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center">
                <Bot size={16} />
              </div>
              <div className="bg-slate-800 p-3 rounded-2xl rounded-tl-none border border-slate-700">
                <Loader2 className="animate-spin text-blue-400" size={18} />
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="p-4 border-t border-slate-800 bg-slate-900/50">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-xs text-slate-500 font-medium">Duration:</span>
          <input 
            type="number" 
            min="1" 
            max="30"
            className="w-16 bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs text-blue-400 focus:outline-none"
            value={days}
            onChange={(e) => setDays(e.target.value)}
          />
          <span className="text-xs text-slate-500">days</span>
        </div>
        <div className="relative">
          <textarea 
            rows="1"
            placeholder="I want to learn Python..."
            className="w-full bg-slate-800 border border-slate-700 rounded-xl pl-4 pr-12 py-3 text-sm focus:ring-2 focus:ring-blue-500 outline-none transition-all resize-none"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSend())}
          />
          <button 
            onClick={handleSend}
            disabled={!input.trim() || loading}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:hover:bg-blue-600 rounded-lg transition-colors text-white"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatPane;
