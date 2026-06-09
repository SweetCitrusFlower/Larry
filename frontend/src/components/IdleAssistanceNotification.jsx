import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Lightbulb, X, Loader2 } from 'lucide-react';

/**
 * IdleAssistanceNotification Component
 * 
 * Displays a non-intrusive notification with a hint when the user has been
 * inactive for 4+ minutes on a coding task.
 * 
 * Features:
 * - Smooth animation in/out
 * - Dismissible by user
 * - Shows loading state while hint is being generated
 * - Context-aware hints from backend
 * - Reusable and themeable
 */
const IdleAssistanceNotification = ({
  isVisible,
  hint,
  loading = false,
  onDismiss,
  onClose,
}) => {
  const [showNotification, setShowNotification] = useState(isVisible);

  useEffect(() => {
    setShowNotification(isVisible);
  }, [isVisible]);

  const handleClose = () => {
    setShowNotification(false);
    onDismiss?.();
    
    // Give animation time to complete before calling onClose
    setTimeout(() => {
      onClose?.();
    }, 300);
  };

  return (
    <AnimatePresence>
      {showNotification && (
        <motion.div
          initial={{ opacity: 0, x: 20, y: -20 }}
          animate={{ opacity: 1, x: 0, y: 0 }}
          exit={{ opacity: 0, x: 20, y: -20 }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          className="fixed bottom-8 right-8 z-50 max-w-md"
        >
          <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 rounded-xl shadow-2xl backdrop-blur-sm p-6 relative overflow-hidden">
            {/* Animated background gradient */}
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            
            {/* Content */}
            <div className="relative z-10">
              {/* Header */}
              <div className="flex items-start gap-4 mb-4">
                <div className="flex-shrink-0 pt-1">
                  <div className="flex items-center justify-center h-8 w-8 rounded-lg bg-blue-500/20 border border-blue-500/30">
                    <Lightbulb size={18} className="text-blue-400" />
                  </div>
                </div>
                
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-semibold text-white mb-1">
                    Looks like you're stuck!
                  </h3>
                  <p className="text-xs text-slate-400 mb-3">
                    Here's a hint to help you move forward:
                  </p>
                </div>
                
                {/* Close button */}
                <button
                  onClick={handleClose}
                  className="flex-shrink-0 p-1 -mr-1 -mt-1 text-slate-400 hover:text-slate-200 hover:bg-slate-700/50 rounded-lg transition-colors"
                  aria-label="Dismiss hint"
                >
                  <X size={18} />
                </button>
              </div>

              {/* Hint content */}
              <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700/50 min-h-[60px] flex items-center">
                {loading ? (
                  <div className="flex items-center gap-3 text-slate-400 w-full">
                    <Loader2 size={16} className="animate-spin flex-shrink-0" />
                    <span className="text-sm">Generating hint...</span>
                  </div>
                ) : hint ? (
                  <p className="text-sm leading-relaxed text-slate-300">
                    {hint}
                  </p>
                ) : (
                  <p className="text-sm text-slate-500 italic">
                    No hint available. Check the problem description and try again!
                  </p>
                )}
              </div>

              {/* Footer message */}
              <p className="text-xs text-slate-500 mt-4 text-center">
                Remember: The best learning happens when you keep trying!
              </p>
            </div>

            {/* Subtle animation border */}
            <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-blue-500/50 to-transparent opacity-50" />
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default IdleAssistanceNotification;
