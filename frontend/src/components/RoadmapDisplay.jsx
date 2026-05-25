import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Calendar, Circle, Loader2, Play, Download, CheckCircle2, Check } from 'lucide-react';
import { dailyPlanAPI, journeyAPI } from '../services/api';
import { useParams, useNavigate } from 'react-router-dom';

const RoadmapDisplay = () => {
  const [roadmap, setRoadmap] = useState(null);
  const [plans, setPlans] = useState([]);
  const [generatingIds, setGeneratingIds] = useState(new Set());
  const [exportingPdf, setExportingPdf] = useState(false);
  const [completingIds, setCompletingIds] = useState(new Set());
  const { journeyId } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchJourney = async () => {
      try {
        const res = await journeyAPI.getJourney(journeyId);
        setRoadmap(res.data);
        
        // Fetch full daily plans because getJourney drops content_status
        const plansRes = await dailyPlanAPI.getJourneyDailyPlans(journeyId);
        if (plansRes.data) {
          setPlans([...plansRes.data].sort((a, b) => a.day_number - b.day_number));
        }
      } catch (e) {
        console.error("Failed to fetch journey", e);
      }
    };
    if (journeyId) {
      fetchJourney();
    }
  }, [journeyId]);

  const handleGenerate = async (planId) => {
    setGeneratingIds(prev => new Set(prev).add(planId));
    try {
      const response = await dailyPlanAPI.generateContent(planId);
      setPlans(prev => prev.map(p => p.id === planId ? response.data : p));
    } catch (e) {
      console.error("Failed to generate content", e);
    } finally {
      setGeneratingIds(prev => {
        const next = new Set(prev);
        next.delete(planId);
        return next;
      });
    }
  };

  const handleStartLesson = (plan) => {
    navigate(`/workspace/${plan.id}`);
  };

  const handleExportPdf = async () => {
    const hasCompletedPlans = plans.some(p => p.theoretical_topic_content && p.theoretical_topic_content.trim() !== "");
    if (!hasCompletedPlans) {
      alert("No lessons generated yet to export!");
      return;
    }

    setExportingPdf(true);
    try {
      const response = await journeyAPI.exportPdf(journeyId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Journey_${journeyId}_Export.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch (e) {
      console.error("Failed to export PDF", e);
      alert("Failed to export PDF.");
    } finally {
      setExportingPdf(false);
    }
  };

  const handleMarkCompleted = async (planId) => {
    setCompletingIds(prev => new Set(prev).add(planId));
    try {
      await dailyPlanAPI.markAsCompleted(planId);
      setPlans(prev => prev.map(p => p.id === planId ? { ...p, completion_status: true } : p));
    } catch (e) {
      console.error("Failed to mark plan as completed", e);
    } finally {
      setCompletingIds(prev => {
        const next = new Set(prev);
        next.delete(planId);
        return next;
      });
    }
  };

  if (!roadmap) {
    return (
      <div className="flex h-full items-center justify-center text-slate-500 w-full">
        <Loader2 className="animate-spin" size={32} />
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="border-b border-slate-800 pb-4 flex flex-col md:flex-row md:items-start justify-between gap-4">
        <div className="flex-1 w-full">
          <h2 className="text-2xl font-bold text-white">{roadmap.journey_title}</h2>
          {roadmap.overview && (
            <p className="text-slate-400 mt-1">{roadmap.overview}</p>
          )}
          <p className="text-xs text-slate-600 mt-2 mb-4">
            {plans.length} days · started from: &ldquo;{roadmap.original_prompt}&rdquo;
          </p>
          
          {/* Progress Bar */}
          {plans.length > 0 && (
            <div className="mt-4 max-w-md">
              <div className="flex justify-between items-end mb-1">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Journey Progress</span>
                <span className="text-xs font-bold text-blue-400">
                  {Math.round((plans.filter(p => p.completion_status).length / plans.length) * 100)}%
                </span>
              </div>
              <div className="w-full h-2.5 bg-slate-800 rounded-full overflow-hidden border border-slate-700/50">
                <motion.div 
                  className="h-full bg-gradient-to-r from-blue-600 to-cyan-400 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${(plans.filter(p => p.completion_status).length / plans.length) * 100}%` }}
                  transition={{ duration: 1, ease: "easeOut" }}
                />
              </div>
            </div>
          )}
        </div>
        
        <button 
          onClick={handleExportPdf}
          disabled={exportingPdf || !plans.some(p => p.theoretical_topic_content && p.theoretical_topic_content.trim() !== "")}
          className="bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-50 disabled:cursor-not-allowed border border-slate-700 px-4 py-2 rounded-lg text-sm font-semibold transition-colors flex items-center gap-2"
          title="Export Progress to PDF"
        >
          {exportingPdf ? <Loader2 size={16} className="animate-spin" /> : <Download size={16} />}
          Export PDF
        </button>
      </div>

      {/* Daily Plans */}
      <div className="space-y-4">
        {plans.map((plan, idx) => {
          console.log("Fetched plan data:", plan);
          return (
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
              {/* Actions */}
              <div className="mt-5 flex justify-end gap-3 border-t border-slate-800/50 pt-4">
                {(plan.content_status === 'COMPLETED' || plan.theoretical_topic_content) ? (
                  <>
                    <button 
                      onClick={() => handleStartLesson(plan)} 
                      className="bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white px-5 py-2 rounded-lg text-sm font-semibold transition-colors flex items-center gap-2"
                    >
                      <Play size={16} /> Start Lesson
                    </button>
                    {plan.completion_status ? (
                      <button 
                        disabled 
                        className="bg-green-500/20 text-green-400 border border-green-500/30 px-5 py-2 rounded-lg text-sm font-semibold flex items-center gap-2 cursor-default"
                      >
                        <CheckCircle2 size={16} /> Completed
                      </button>
                    ) : (
                      <button 
                        onClick={() => handleMarkCompleted(plan.id)}
                        disabled={completingIds.has(plan.id)}
                        className="bg-blue-600 hover:bg-blue-500 text-white px-5 py-2 rounded-lg text-sm font-semibold transition-colors flex items-center gap-2 disabled:opacity-50"
                      >
                        {completingIds.has(plan.id) ? <Loader2 size={16} className="animate-spin" /> : <Check size={16} />} 
                        Mark as Completed
                      </button>
                    )}
                  </>
                ) : (generatingIds.has(plan.id) || plan.content_status === 'GENERATING') ? (
                  <button disabled className="bg-slate-800 text-slate-400 border border-slate-700 px-5 py-2 rounded-lg text-sm font-semibold flex items-center gap-2 cursor-not-allowed">
                    <Loader2 size={16} className="animate-spin" /> Generating...
                  </button>
                ) : (
                  <button 
                    onClick={() => handleGenerate(plan.id)} 
                    className="bg-slate-800 hover:bg-slate-700 text-white border border-slate-700 px-5 py-2 rounded-lg text-sm font-semibold transition-colors"
                  >
                    Generate Lesson
                  </button>
                )}
              </div>
            </div>
          </motion.div>
        )})}
      </div>
    </motion.div>
  );
};

export default RoadmapDisplay;
