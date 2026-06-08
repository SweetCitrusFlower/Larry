import React from 'react';
import { useFavorites } from '../context/FavoritesContext';
import { X, Trash2, FileText, Code } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const FavoritesPanel = ({ isOpen, onClose }) => {
  const { favorites, loading, removeFavorite } = useFavorites();

  const parseContent = (fav) => {
    if (fav.item_type === 'knowledge_source') {
      try {
        const parsed = JSON.parse(fav.item_content);
        return {
          title: parsed.title || 'Untitled Material',
          description: `Material ID: ${parsed.id}`,
          icon: <FileText size={16} className="text-blue-400" />
        };
      } catch (e) {
        return { title: 'Unknown Material', description: fav.item_content, icon: <FileText size={16} /> };
      }
    }
    // Fallback for code or other types
    return {
      title: fav.item_type.toUpperCase(),
      description: fav.item_content,
      icon: <Code size={16} className="text-emerald-400" />
    };
  };

  return (
    <>
      {/* Backdrop overlay for closing */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/20 backdrop-blur-sm transition-opacity"
          onClick={onClose}
        ></div>
      )}

      {/* Side Panel */}
      <div 
        className={`fixed top-0 right-0 h-full w-full sm:w-[400px] bg-slate-950 border-l border-slate-800 shadow-2xl z-50 transform transition-transform duration-300 ease-in-out flex flex-col ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        <div className="flex items-center justify-between p-6 border-b border-slate-800 bg-slate-900/50">
          <h2 className="text-xl font-bold text-white">My Favorites</h2>
          <button 
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 custom-scrollbar">
          {loading && favorites.length === 0 ? (
            <div className="flex justify-center items-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
          ) : favorites.length === 0 ? (
            <div className="text-center py-12">
              <StarIcon size={48} className="mx-auto text-slate-800 mb-4" />
              <p className="text-slate-500">No favorites saved yet.</p>
            </div>
          ) : (
            <div className="space-y-4">
              <AnimatePresence>
                {favorites.map((fav) => {
                  const { title, description, icon } = parseContent(fav);
                  return (
                    <motion.div 
                      layout
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -20, scale: 0.95 }}
                      key={fav.id} 
                      className="bg-slate-900 border border-slate-800 rounded-xl p-4 group hover:border-slate-700 transition-colors"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          {icon}
                          <span className="text-sm font-semibold text-slate-200 line-clamp-1" title={title}>
                            {title}
                          </span>
                        </div>
                        <button 
                          onClick={() => removeFavorite(fav.id)}
                          className="text-slate-500 hover:text-red-400 p-1 rounded-md opacity-0 group-hover:opacity-100 transition-all"
                          title="Remove favorite"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                      
                      <div className="bg-slate-950 rounded-lg p-3 text-sm text-slate-400 mb-3 line-clamp-3 break-words">
                        {description}
                      </div>

                      <div className="text-xs text-slate-600 flex justify-between items-center">
                        <span>Saved</span>
                        <span>{new Date(fav.created_at).toLocaleDateString()}</span>
                      </div>
                    </motion.div>
                  );
                })}
              </AnimatePresence>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

// Helper since Star wasn't imported
const StarIcon = ({ size, className }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
  </svg>
);

export default FavoritesPanel;
