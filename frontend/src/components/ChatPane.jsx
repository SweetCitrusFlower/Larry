import React, { useState, useRef, useEffect } from 'react';
import { chatAPI, journeyAPI, knowledgeSourceAPI } from '../services/api';
import { Send, Sparkles, Loader2, User, Bot, Paperclip } from 'lucide-react';
import { motion } from 'framer-motion';
import { useNavigate, useParams } from 'react-router-dom';

const ChatPane = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [days, setDays] = useState(7);
  const [loading, setLoading] = useState(false);
  const [uploadingFile, setUploadingFile] = useState(false);
  const scrollRef = useRef(null);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();
  const { journeyId } = useParams();

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        if (journeyId) {
          const res = await journeyAPI.getJourney(journeyId);
          const j = res.data;
          setMessages([
            { role: 'assistant', content: "Hi, I'm Larry. What would you like to learn today? Tell me the topic and how many days you have." },
            { role: 'user', content: `I want to learn ${j.original_prompt} in ${j.target_days} days.` },
            { role: 'assistant', content: `Great! I've generated your ${j.journey_title} roadmap. Check it out on the right.` }
          ]);
        } else {
          setMessages([{ role: 'assistant', content: "Hi, I'm Larry. What would you like to learn today? Tell me the topic and how many days you have." }]);
        }
      } catch (err) {
        setMessages([{ role: 'assistant', content: "Hi, I'm Larry. What would you like to learn today? Tell me the topic and how many days you have." }]);
      }
    };
    fetchHistory();
  }, [journeyId]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const pushMessage = (role, content) =>
    setMessages((prev) => [...prev, { role, content }]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userContent = `I want to learn ${input} in ${days} days.`;
    pushMessage('user', userContent);
    const savedInput = input;
    const savedDays = parseInt(days, 10);
    setInput('');
    setLoading(true);

    try {
      // 1. Persist the user message to the backend
      await chatAPI.sendMessage(userContent, 'user');

      // 2. Call the journey generation endpoint
      const response = await journeyAPI.generate(savedInput, savedDays);
      const journey = response.data;

      pushMessage(
        'assistant',
        `Great! I've generated your ${journey.journey_title} roadmap. Check it out on the right.`
      );

      navigate(`/journey/${journey.id}`);
    } catch (err) {
      const detail =
        err.response?.data?.detail || 'Sorry, I encountered an error. Please try again.';
      pushMessage('assistant', detail);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    setUploadingFile(true);
    pushMessage('user', `Uploading file: ${file.name}...`);
    
    try {
      await knowledgeSourceAPI.upload(file);
      pushMessage('assistant', `File '${file.name}' has been successfully uploaded and added to my knowledge base. You can now ask me questions about it!`);
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to upload the file. Please ensure it is a supported format (PDF, TXT, MD, PY).';
      pushMessage('assistant', `Error: ${detail}`);
    } finally {
      setUploadingFile(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <div className="flex flex-col h-full glass-card overflow-hidden">
      <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/50 shrink-0">
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
        {uploadingFile && (
          <div className="flex justify-start">
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center">
                <Paperclip size={16} className="text-slate-400" />
              </div>
              <div className="bg-slate-800 p-3 rounded-2xl rounded-tl-none border border-slate-700 flex items-center gap-2">
                <Loader2 className="animate-spin text-blue-400" size={16} />
                <span className="text-sm text-slate-300">Processing file...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="p-4 border-t border-slate-800 bg-slate-900/50 shrink-0">
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
        <div className="relative flex items-center gap-2">
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileUpload} 
            className="hidden" 
            accept=".pdf,.txt,.md,.py" 
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={loading || uploadingFile}
            className="p-3 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 rounded-xl transition-colors text-slate-400 focus:outline-none border border-slate-700 shrink-0"
            title="Upload File"
          >
            <Paperclip size={18} />
          </button>
          
          <div className="relative flex-1">
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
              disabled={!input.trim() || loading || uploadingFile}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:hover:bg-blue-600 rounded-lg transition-colors text-white"
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPane;
