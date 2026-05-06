import React from 'react';
import { motion } from 'framer-motion';
import { Calendar, CheckCircle2, Circle } from 'lucide-react';

const RoadmapDisplay = ({ roadmap }) => {
  if (!roadmap) return null;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="border-b border-slate-800 pb-4">
        <h2 className="text-2xl font-bold text-white">{roadmap.journey_title}</h2>
        <p className="text-slate-400 mt-1">{roadmap.overview}</p>
      </div>

      <div className="space-y-4">
        {roadmap.daily_plans?.map((day, idx) => (
          <motion.div 
            key={idx}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="flex gap-4 group"
          >
            <div className="flex flex-col items-center">
              <div className="w-10 h-10 rounded-full bg-blue-600/20 border border-blue-500/50 flex items-center justify-center text-blue-400 font-bold shrink-0">
                {day.day_number}
              </div>
              {idx !== roadmap.daily_plans.length - 1 && (
                <div className="w-px h-full bg-slate-800 my-1 group-hover:bg-blue-500/30 transition-colors" />
              )}
            </div>
            
            <div className="glass-card p-5 flex-1 hover:border-slate-700 transition-colors">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold text-lg text-white">Day {day.day_number}: {day.title}</h3>
                <div className="flex items-center gap-2">
                  <span className="text-xs px-2 py-1 rounded bg-slate-800 text-slate-300">
                    {day.difficulty}
                  </span>
                  <Calendar size={16} className="text-slate-500" />
                </div>
              </div>
              
              {day.concepts_to_cover && (
                <div className="mt-4 space-y-2">
                  <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Concepts to Cover</p>
                  {day.concepts_to_cover.map((concept, tidx) => (
                    <div key={tidx} className="flex items-center gap-2 text-sm text-slate-300">
                      <Circle size={12} className="text-blue-500" />
                      {concept}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
};

export default RoadmapDisplay;
