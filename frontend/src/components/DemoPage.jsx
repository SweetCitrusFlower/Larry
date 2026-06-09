import React, { useState, useEffect, useRef } from 'react';
import { Play, Square, Terminal as TerminalIcon, AlertCircle, Lightbulb, Code2, BrainCircuit } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { demoAPI } from '../services/api';

const EVENT_STYLES = {
  system: { color: 'text-slate-400', icon: <TerminalIcon size={16} /> },
  memory: { color: 'text-purple-400', icon: <BrainCircuit size={16} /> },
  coding: { color: 'text-green-400', icon: <Code2 size={16} /> },
  evaluating: { color: 'text-yellow-400', icon: <Play size={16} /> },
  tutor: { color: 'text-blue-400', icon: <Lightbulb size={16} /> },
  reflecting: { color: 'text-indigo-400', icon: <BrainCircuit size={16} /> },
  error: { color: 'text-red-400', icon: <AlertCircle size={16} /> },
  end: { color: 'text-emerald-400', icon: <Square size={16} /> },
};

export default function DemoPage() {
  const [events, setEvents] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState(null);
  const eventSourceRef = useRef(null);
  const terminalEndRef = useRef(null);

  // Auto-scroll to bottom of terminal
  useEffect(() => {
    if (terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [events]);

  // Clean up SSE on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const handleStartDemo = async () => {
    try {
      setError(null);
      setEvents([]);
      setIsRunning(true);
      
      // Close existing stream if any
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      // Start the demo via API
      await demoAPI.startDemo();

      // Connect to SSE stream
      // Nginx proxies /api/v1 to the backend
      const sse = new EventSource(`/api/v1/demo/stream`);
      
      eventSourceRef.current = sse;

      // Listen to all standard event types defined in our backend
      const handleEvent = (e) => {
        const type = e.type;
        const data = e.data.replace(/\\n/g, '\n');
        
        setEvents((prev) => [...prev, { id: Date.now() + Math.random(), type, data }]);
        
        if (type === 'end') {
          setIsRunning(false);
          sse.close();
        }
      };

      Object.keys(EVENT_STYLES).forEach(eventType => {
        sse.addEventListener(eventType, handleEvent);
      });
      
      // Standard message fallback
      sse.onmessage = handleEvent;

      sse.onerror = (e) => {
        console.error('SSE Error:', e);
        // Only show error if we were actually running and didn't get an 'end' event
        if (eventSourceRef.current?.readyState !== EventSource.CLOSED) {
            setError("Connection to demo stream lost.");
            setIsRunning(false);
            sse.close();
        }
      };

    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || err.message || "Failed to start demo");
      setIsRunning(false);
    }
  };

  const handleStopDemo = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    setIsRunning(false);
    setEvents(prev => [...prev, { id: Date.now(), type: 'system', data: 'Demo stopped by user.' }]);
  };

  return (
    <div className="flex flex-col h-full w-full max-w-6xl mx-auto space-y-6">
      
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent mb-2">
            Autonomous Student Demo
          </h1>
          <p className="text-slate-400">
            Watch an AI agent simulate a real user generating a journey, writing code, and learning from the Socratic Tutor.
          </p>
        </div>
        
        <div className="flex gap-4">
          {!isRunning ? (
            <button
              onClick={handleStartDemo}
              className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-medium transition-all shadow-[0_0_20px_rgba(37,99,235,0.3)] hover:shadow-[0_0_25px_rgba(37,99,235,0.5)]"
            >
              <Play size={18} />
              Initialize Agent
            </button>
          ) : (
            <button
              onClick={handleStopDemo}
              className="flex items-center gap-2 px-6 py-3 bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/50 rounded-xl font-medium transition-all"
            >
              <Square size={18} />
              Stop Agent
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 flex items-center gap-3">
          <AlertCircle size={20} />
          {error}
        </div>
      )}

      {/* Terminal Window */}
      <div className="flex-1 bg-[#0f111a] border border-slate-800 rounded-2xl overflow-hidden flex flex-col shadow-2xl relative">
        {/* Terminal Header */}
        <div className="h-12 bg-slate-900 border-b border-slate-800 flex items-center px-4 gap-2 shrink-0">
          <div className="flex gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
            <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
            <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
          </div>
          <div className="mx-auto flex items-center gap-2 text-slate-500 text-sm font-mono">
            <TerminalIcon size={14} />
            agent-console ~ student-demo
          </div>
        </div>

        {/* Terminal Body */}
        <div className="flex-1 p-6 overflow-y-auto font-mono text-sm space-y-4 custom-scrollbar">
          {events.length === 0 && !isRunning && (
            <div className="text-slate-500 flex flex-col items-center justify-center h-full gap-4">
              <BrainCircuit size={48} className="text-slate-700" />
              <p>Waiting for initialization...</p>
            </div>
          )}
          
          <AnimatePresence>
            {events.map((ev) => {
              const style = EVENT_STYLES[ev.type] || EVENT_STYLES.system;
              return (
                <motion.div
                  key={ev.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex gap-4"
                >
                  <div className={`mt-0.5 shrink-0 ${style.color}`}>
                    {style.icon}
                  </div>
                  <div className="flex-1">
                    <span className={`font-semibold mr-2 ${style.color}`}>
                      [{ev.type.toUpperCase()}]
                    </span>
                    <span className="text-slate-300 whitespace-pre-wrap">
                      {ev.data}
                    </span>
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>
          <div ref={terminalEndRef} />
        </div>
        
        {/* Glowing border effect when running */}
        {isRunning && (
          <div className="absolute inset-0 pointer-events-none rounded-2xl ring-1 ring-blue-500/50 shadow-[inset_0_0_30px_rgba(37,99,235,0.1)]"></div>
        )}
      </div>
    </div>
  );
}
