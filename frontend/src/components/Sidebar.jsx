import React, { useEffect, useState } from 'react';
import { journeyAPI } from '../services/api';
import { Plus, MessageSquare, Map, History, Library, Terminal, Sparkles } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAutopilot } from '../context/AutopilotContext';
import { Trash2 } from 'lucide-react';

const Sidebar = () => {
  const { startVisualDemo, stopGhostMode, isGhostModeActive } = useAutopilot();
  const [journeys, setJourneys] = useState([]);
  const navigate = useNavigate();
  const location = useLocation();

  const fetchJourneys = async () => {
    try {
      const res = await journeyAPI.getJourneys();
      setJourneys(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchJourneys();
  }, [location.pathname]); // Refresh when navigation changes

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (window.confirm("Are you sure you want to delete this journey? This will remove all associated daily plans, tasks, and chat history.")) {
      try {
        await journeyAPI.delete(id);
        setJourneys(prev => prev.filter(j => j.id !== id));
        if (location.pathname.includes(`/journey/${id}`) || location.pathname.includes(`/workspace/`)) {
          navigate('/');
        }
      } catch (err) {
        console.error("Failed to delete journey", err);
        alert("Failed to delete journey");
      }
    }
  };

  return (
    <aside className="w-64 bg-slate-950 border-r border-slate-800 flex flex-col h-[calc(100vh-64px)] overflow-hidden shrink-0 tour-sidebar">
      <div className="p-4 border-b border-slate-800 space-y-2">
        <button 
          onClick={() => navigate('/')}
          className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg font-medium transition-colors"
        >
          <Plus size={18} />
          New Journey
        </button>
        <button 
          onClick={() => navigate('/submissions')}
          className={`w-full flex items-center justify-center gap-2 py-2 px-4 rounded-lg font-medium transition-colors ${
            location.pathname === '/submissions' 
            ? 'bg-slate-800 text-blue-400' 
            : 'bg-transparent text-slate-400 hover:bg-slate-900 hover:text-slate-200'
          }`}
        >
          <History size={18} />
          Submission History
        </button>
        <button 
          onClick={() => navigate('/materials')}
          className={`w-full flex items-center justify-center gap-2 py-2 px-4 rounded-lg font-medium transition-colors ${
            location.pathname === '/materials' 
            ? 'bg-slate-800 text-blue-400' 
            : 'bg-transparent text-slate-400 hover:bg-slate-900 hover:text-slate-200'
          }`}
        >
          <Library size={18} />
          Material Explorer
        </button>
        {isGhostModeActive ? (
          <button 
            onClick={stopGhostMode}
            className="w-full flex items-center justify-center gap-2 py-2 px-4 rounded-lg font-medium transition-all mt-2 border bg-red-900/50 text-red-300 border-red-500 shadow-[0_0_15px_rgba(239,68,68,0.4)] hover:bg-red-900/80"
          >
            <Sparkles size={18} />
            Stop Ghost Mode
          </button>
        ) : (
          <button 
            onClick={startVisualDemo}
            className="w-full flex items-center justify-center gap-2 py-2 px-4 rounded-lg font-medium transition-all mt-2 border bg-purple-600/10 text-purple-400 border-purple-500/30 hover:bg-purple-600/20 hover:text-purple-300 hover:shadow-[0_0_10px_rgba(168,85,247,0.2)]"
          >
            <Sparkles size={18} />
            Start Visual Demo
          </button>
        )}
      </div>
      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-2 custom-scrollbar">
        <h3 className="text-xs font-bold text-slate-500 tracking-wider mb-2 uppercase">Your Journeys</h3>
        {journeys.map(j => {
          const isActive = location.pathname.includes(`/journey/${j.id}`) || location.pathname.includes(`/workspace/`);
          return (
            <button
              key={j.id}
              onClick={() => navigate(`/journey/${j.id}`)}
              className={`flex flex-col text-left p-3 rounded-xl border transition-all ${
                isActive && location.pathname.includes(`/journey/${j.id}`) 
                  ? 'bg-slate-800 border-slate-700' 
                  : 'bg-transparent border-transparent hover:bg-slate-900'
              }`}
            >
              <div className="flex items-center justify-between w-full">
                <div className="flex items-center gap-2 text-sm font-semibold text-slate-200 truncate">
                  <Map size={16} className="text-blue-400 shrink-0" />
                  <span className="truncate">{j.journey_title || 'Untitled Journey'}</span>
                </div>
                <button
                  onClick={(e) => handleDelete(e, j.id)}
                  className="p-1.5 text-slate-500 hover:text-red-400 hover:bg-slate-800 rounded-md transition-colors"
                  title="Delete Journey"
                >
                  <Trash2 size={14} />
                </button>
              </div>
              <div className="text-xs text-slate-500 mt-1 pl-6 text-left">
                {new Date(j.created_at).toLocaleDateString()}
              </div>
            </button>
          )
        })}
        {journeys.length === 0 && (
          <div className="text-center text-slate-500 text-sm mt-4">
            No journeys yet.
          </div>
        )}
      </div>
    </aside>
  );
};

export default Sidebar;
