import React, { useState, useEffect } from 'react';
import ChatPane from './components/ChatPane';
import RoadmapDisplay from './components/RoadmapDisplay';
import AuthModal from './components/AuthModal';
import { LogOut, Layout, BookOpen, User as UserIcon } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

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
