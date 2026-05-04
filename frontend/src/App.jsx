import React, { useState, useEffect } from 'react';
import ChatPane from './components/ChatPane';
import RoadmapDisplay from './components/RoadmapDisplay';
import AuthModal from './components/AuthModal';
import { LogOut, Layout, BookOpen, User as UserIcon } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('token'));
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(!isAuthenticated);
  const [currentRoadmap, setCurrentRoadmap] = useState(null);

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    setIsAuthModalOpen(true);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 flex flex-col font-sans">
      {/* Header */}
      <header className="h-16 border-b border-slate-800 bg-slate-950/50 backdrop-blur-md flex items-center justify-between px-8 sticky top-0 z-40">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <Layout size={18} className="text-white" />
          </div>
          <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
            LARRY
          </h1>
        </div>

        <div className="flex items-center gap-6">
          {isAuthenticated && (
            <>
              <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-slate-400">
                <a href="#" className="hover:text-white transition-colors">Dashboard</a>
                <a href="#" className="text-blue-400">My Roadmaps</a>
                <a href="#" className="hover:text-white transition-colors">Resources</a>
              </nav>
              <div className="h-4 w-px bg-slate-800 hidden md:block" />
              <button 
                onClick={handleLogout}
                className="flex items-center gap-2 text-sm text-slate-400 hover:text-red-400 transition-colors"
              >
                <LogOut size={16} />
                <span>Sign Out</span>
              </button>
            </>
          )}
        </div>
      </header>

      <main className="flex-1 flex flex-col md:flex-row gap-6 p-6 max-w-[1600px] mx-auto w-full overflow-hidden">
        {/* Left Side - Chat Assistant */}
        <div className="w-full md:w-[400px] lg:w-[450px] shrink-0 h-[calc(100vh-120px)]">
          <ChatPane onRoadmapGenerated={setCurrentRoadmap} />
        </div>

        {/* Right Side - Content Area */}
        <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar h-[calc(100vh-120px)]">
          <AnimatePresence mode="wait">
            {currentRoadmap ? (
              <RoadmapDisplay key="roadmap" roadmap={currentRoadmap} />
            ) : (
              <motion.div 
                key="placeholder"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="h-full flex flex-col items-center justify-center text-center p-12 border-2 border-dashed border-slate-800 rounded-3xl"
              >
                <div className="w-16 h-16 bg-slate-900 rounded-2xl flex items-center justify-center mb-6 border border-slate-800">
                  <BookOpen size={32} className="text-slate-600" />
                </div>
                <h2 className="text-2xl font-bold text-white mb-2">Ready to Start?</h2>
                <p className="text-slate-500 max-w-sm">
                  Ask Larry to generate a roadmap for any skill you want to master. 
                  Your personalized path to success starts here.
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>

      <AuthModal 
        isOpen={isAuthModalOpen} 
        onClose={() => setIsAuthModalOpen(false)}
        onAuthSuccess={() => setIsAuthenticated(true)}
      />
    </div>
  );
}

// ════════════════════════════════════════════════════════════════════════════
// MAIN APP
// ════════════════════════════════════════════════════════════════════════════
export default function App() {
  const [authed, setAuthed] = useState(!!localStorage.getItem('larry_token'));
  const [journeys, setJourneys] = useState([]);
  const [loadingJourneys, setLoadingJourneys] = useState(false);
  const [showGenerate, setShowGenerate] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [error, setError] = useState('');

  const fetchJourneys = async () => {
    setLoadingJourneys(true);
    try {
      const res = await api.get('/journeys/');
      setJourneys(res.data);
    } catch (err) {
      if (err.response?.status === 401) { localStorage.removeItem('larry_token'); setAuthed(false); }
      else setError('Nu s-au putut încărca roadmaps-urile.');
    } finally { setLoadingJourneys(false); }
  };

  useEffect(() => { if (authed) fetchJourneys(); }, [authed]);

  const logout = () => { localStorage.removeItem('larry_token'); setAuthed(false); setJourneys([]); };

  if (!authed) return <AuthPage onLogin={() => setAuthed(true)} />;

  return (
    <div className="app">
      {/* NAV */}
      <nav className="navbar">
        <div className="nav-brand">⚡ Larry</div>
        <div className="nav-actions">
          <button className="btn-primary" id="btn-new-roadmap" onClick={() => setShowGenerate(true)}>+ Roadmap Nou</button>
          <button className="btn-ghost" onClick={logout}>Ieșire</button>
        </div>
      </nav>

      {/* HERO */}
      <div className="hero">
        <h1>📚 Roadmaps-urile Mele</h1>
        <p>Planurile tale de învățare generate de AI</p>
      </div>

      {/* CONTENT */}
      <main className="main-content">
        {error && <div className="alert-err">{error}</div>}

        {loadingJourneys ? (
          <div className="loading-state">
            <div className="big-spin" />
            <p>Se încarcă roadmaps-urile...</p>
          </div>
        ) : journeys.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🗺️</div>
            <h2>Niciun roadmap încă</h2>
            <p>Generează primul tău plan de învățare personalizat cu AI!</p>
            <button className="btn-primary" onClick={() => setShowGenerate(true)}>✨ Generează primul roadmap</button>
          </div>
        ) : (
          <div className="roadmaps-grid">
            {journeys.map(j => <RoadmapCard key={j.id} journey={j} />)}
          </div>
        )}
      </main>

      {/* MODALS */}
      {showGenerate && (
        <GenerateModal
          onClose={() => setShowGenerate(false)}
          onGenerated={newJ => setJourneys(prev => [newJ, ...prev])}
        />
      )}

      {/* CHAT BUTTON + PANEL */}
      {showChat ? (
        <ChatPanel onClose={() => setShowChat(false)} />
      ) : (
        <button id="btn-open-chat" className="chat-fab" onClick={() => setShowChat(true)} title="Deschide chat AI">
          💬
        </button>
      )}
    </div>
  );
}
