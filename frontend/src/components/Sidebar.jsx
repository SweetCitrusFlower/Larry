import React, { useEffect, useState } from 'react';
import { journeyAPI } from '../services/api';
import { Plus, MessageSquare, Map } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';

const Sidebar = () => {
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

  return (
    <aside className="w-64 bg-slate-950 border-r border-slate-800 flex flex-col h-[calc(100vh-64px)] overflow-hidden shrink-0">
      <div className="p-4 border-b border-slate-800">
        <button 
          onClick={() => navigate('/')}
          className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg font-medium transition-colors"
        >
          <Plus size={18} />
          New Journey
        </button>
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
              <div className="flex items-center gap-2 text-sm font-semibold text-slate-200">
                <Map size={16} className="text-blue-400 shrink-0" />
                <span className="truncate">{j.journey_title || 'Untitled Journey'}</span>
              </div>
              <div className="text-xs text-slate-500 mt-1 pl-6">
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
