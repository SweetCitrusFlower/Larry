import React from 'react';
import { motion } from 'framer-motion';
import { Calendar, Circle } from 'lucide-react';

/**
 * Renders a Journey returned by the backend.
 *
 * Backend JourneyResponse shape:
 *   { id, user_id, journey_title, overview, target_days, original_prompt, created_at,
 *     daily_plans: [{ id, journey_id, day_number, title, concepts_to_cover, difficulty }] }
 */
const RoadmapDisplay = ({ roadmap }) => {
  if (!roadmap) return null;

  // Normalise: backend returns `daily_plans`, sorted by day_number
  const plans = [...(roadmap.daily_plans ?? [])].sort(
    (a, b) => a.day_number - b.day_number
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="border-b border-slate-800 pb-4">
        <h2 className="text-2xl font-bold text-white">{roadmap.journey_title}</h2>
        {roadmap.overview && (
          <p className="text-slate-400 mt-1">{roadmap.overview}</p>
        )}
        <p className="text-xs text-slate-600 mt-2">
          {plans.length} days · started from: &ldquo;{roadmap.original_prompt}&rdquo;
        </p>
      </div>

      {/* Daily Plans */}
      <div className="space-y-4">
        {plans.map((plan, idx) => (
          <motion.div
            key={plan.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.07 }}
            className="flex gap-4 group"
          >
            {/* Timeline dot + connector */}
            <div className="flex flex-col items-center">
              <div className="w-10 h-10 rounded-full bg-blue-600/20 border border-blue-500/50 flex items-center justify-center text-blue-400 font-bold shrink-0">
                {plan.day_number}
              </div>
              {idx !== plans.length - 1 && (
                <div className="w-px flex-1 bg-slate-800 my-1 group-hover:bg-blue-500/30 transition-colors" />
              )}
            </div>

            {/* Card */}
            <div className="glass-card p-5 flex-1 hover:border-slate-700 transition-colors mb-2">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold text-lg text-white">
                  Day {plan.day_number}: {plan.title}
                </h3>
                <div className="flex items-center gap-2">
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                    plan.difficulty === 'Beginner'
                      ? 'bg-green-500/15 text-green-400'
                      : plan.difficulty === 'Intermediate'
                      ? 'bg-yellow-500/15 text-yellow-400'
                      : 'bg-red-500/15 text-red-400'
                  }`}>
                    {plan.difficulty}
                  </span>
                  <Calendar size={16} className="text-slate-500" />
                </div>
              </div>

              {/* Concepts */}
              {plan.concepts_to_cover?.length > 0 && (
                <div className="mt-3 space-y-1">
                  <p className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
                    Concepts to Cover
                  </p>
                  {plan.concepts_to_cover.map((concept, cidx) => (
                    <div key={cidx} className="flex items-center gap-2 text-sm text-slate-300">
                      <Circle size={12} className="text-blue-500 shrink-0" />
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
