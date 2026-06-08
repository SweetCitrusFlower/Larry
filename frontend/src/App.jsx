import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import ChatPane from './components/ChatPane';
import RoadmapDisplay from './components/RoadmapDisplay';
import AuthModal from './components/AuthModal';
import Workspace from './components/Workspace';
import Submissions from './components/Submissions';
import { LogOut, Layout, BookOpen, Star } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

import Editor from '@monaco-editor/react';
import axios from 'axios';
import FavoriteButton from './components/FavoriteButton';
import FavoritesPanel from './components/FavoritesPanel';

// A wrapper for the Dashboard (New Journey view)
const Dashboard = () => {
  return (
    <>
      {/* Left Side - Chat Assistant */}
      <div className="w-full md:w-[400px] lg:w-[450px] shrink-0 h-full">
        <ChatPane />
      </div>

      {/* Right Side - Content Area */}
      <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar h-full">
        <div className="h-full flex flex-col items-center justify-center text-center p-12 border-2 border-dashed border-slate-800 rounded-3xl">
          <div className="w-16 h-16 bg-slate-900 rounded-2xl flex items-center justify-center mb-6 border border-slate-800">
            <BookOpen size={32} className="text-slate-600" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">Ready to Start?</h2>
          <p className="text-slate-500 max-w-sm">
            Ask Larry to generate a roadmap for any skill you want to master. 
            Your personalized path to success starts here.
          </p>
        </div>
      </div>
    </>
  );
};

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('token'));
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(!isAuthenticated);
  const [isFavoritesOpen, setIsFavoritesOpen] = useState(false);

  // Sync modal state if auth state changes
  useEffect(() => {
    if (!isAuthenticated) {
      setIsAuthModalOpen(true);
    }
  }, [isAuthenticated]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 flex flex-col font-sans h-screen overflow-hidden">
      {/* Header */}
      <header className="h-16 border-b border-slate-800 bg-slate-950/50 backdrop-blur-md flex items-center justify-between px-8 shrink-0 z-40">
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
              <button 
                onClick={() => setIsFavoritesOpen(true)}
                className="flex items-center gap-2 text-sm text-yellow-400 hover:text-yellow-300 transition-colors"
              >
                <Star size={16} />
                <span>Favorites</span>
              </button>
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

      <div className="flex flex-1 overflow-hidden">
        {isAuthenticated && <Sidebar />}
        <main className="flex-1 flex gap-6 p-6 overflow-hidden max-w-full">
           <Routes>
              {/* Only render actual content if authenticated to prevent 401 loops */}
              {isAuthenticated ? (
                <>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/journey/:journeyId" element={
                    <>
                      <div className="w-full md:w-[400px] lg:w-[450px] shrink-0 h-full">
                        <ChatPane />
                      </div>
                      <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar h-full">
                        <RoadmapDisplay />
                      </div>
                    </>
                  } />
                  <Route path="/workspace/:dailyPlanId" element={<Workspace />} />
                  <Route path="/submissions" element={<Submissions />} />
                </>
              ) : (
                <Route path="/login" element={
                  <div className="flex-1 flex flex-col items-center justify-center text-slate-500">
                     <p>Please log in to continue.</p>
                  </div>
                } />
              )}
              
              {/* Fallback route */}
              <Route path="*" element={<Navigate to={isAuthenticated ? "/" : "/login"} replace />} />
           </Routes>
        </main>
      </div>

      <AuthModal 
        isOpen={isAuthModalOpen} 
        onClose={() => {
          // If they close the modal but aren't authenticated, re-open it or let them stay on the blank login screen
          if (!isAuthenticated) setIsAuthModalOpen(true);
          else setIsAuthModalOpen(false);
        }}
        onAuthSuccess={() => {
          setIsAuthenticated(true);
          setIsAuthModalOpen(false);
        }}
      />
      
      <FavoritesPanel 
        isOpen={isFavoritesOpen} 
        onClose={() => setIsFavoritesOpen(false)} 
      />
    </div>
  );
}
