import React from 'react';
import { Sparkles, Map, ArrowRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const SimilarityModal = ({ isOpen, onClose, similarJourney, onUseExisting, onForceGenerate, loading }) => {
  if (!isOpen || !similarJourney) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm"
          onClick={onClose}
        />

        {/* Modal */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          className="relative w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden"
        >
          <div className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-purple-500/20 flex items-center justify-center border border-purple-500/30">
                <Sparkles className="w-5 h-5 text-purple-400" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-white">Similar Journey Found</h2>
                <p className="text-sm text-slate-400">We found an existing roadmap that matches your request!</p>
              </div>
            </div>

            <div className="bg-slate-950 rounded-xl p-4 border border-slate-800 mb-6">
              <div className="flex items-start gap-3">
                <Map className="w-5 h-5 text-blue-400 mt-0.5 shrink-0" />
                <div>
                  <h3 className="font-medium text-slate-200">{similarJourney.journey.journey_title}</h3>
                  <p className="text-sm text-slate-400 mt-1 line-clamp-2">
                    {similarJourney.journey.overview}
                  </p>
                  <div className="flex items-center gap-4 mt-3 text-xs text-slate-500 font-medium">
                    <span className="flex items-center gap-1.5 px-2 py-1 bg-slate-900 rounded-md border border-slate-800">
                      Duration: {similarJourney.journey.target_days} Days
                    </span>
                    <span className="flex items-center gap-1.5 px-2 py-1 bg-purple-500/10 text-purple-400 rounded-md border border-purple-500/20">
                      Match: {Math.round(similarJourney.score)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <p className="text-sm text-slate-400 mb-6 leading-relaxed">
              Using the existing roadmap gives you instant access to the curriculum without waiting for AI generation. Would you like to use this one, or force generate a brand new one?
            </p>

            <div className="flex flex-col sm:flex-row gap-3">
              <button
                onClick={onForceGenerate}
                disabled={loading}
                className="flex-1 px-4 py-2.5 rounded-lg border border-slate-700 text-slate-300 font-medium hover:bg-slate-800 transition-colors disabled:opacity-50"
              >
                Force Generate New
              </button>
              <button
                onClick={onUseExisting}
                disabled={loading}
                className="flex-1 px-4 py-2.5 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <span>Use Existing</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};

export default SimilarityModal;
