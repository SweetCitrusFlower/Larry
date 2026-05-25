import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { History, X, CheckCircle2, XCircle, Code2, Loader2, Clock, HardDrive, Calendar } from 'lucide-react';
import { submissionAPI } from '../services/api';

const Submissions = () => {
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSubmission, setSelectedSubmission] = useState(null);

  useEffect(() => {
    const fetchSubmissions = async () => {
      try {
        const res = await submissionAPI.getMySubmissions();
        setSubmissions(res.data);
      } catch (e) {
        console.error("Failed to fetch submissions", e);
      } finally {
        setLoading(false);
      }
    };
    fetchSubmissions();
  }, []);

  const formatDate = (dateString) => {
    if (!dateString) return "N/A";
    const d = new Date(dateString);
    return d.toLocaleString([], {
      month: 'short', day: 'numeric', year: 'numeric',
      hour: '2-digit', minute: '2-digit'
    });
  };

  const getStatusBadge = (status) => {
    if (status === 'accepted') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-green-500/15 text-green-400 border border-green-500/20">
          <CheckCircle2 size={14} /> Accepted
        </span>
      );
    }
    if (status === 'pending') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-yellow-500/15 text-yellow-400 border border-yellow-500/20">
          <Loader2 size={14} className="animate-spin" /> Pending
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-500/15 text-red-400 border border-red-500/20">
        <XCircle size={14} /> {status === 'failed' ? 'Failed' : status}
      </span>
    );
  };

  return (
    <div className="flex-1 w-full flex flex-col h-full bg-slate-950 overflow-hidden relative">
      
      {/* Header */}
      <div className="px-8 py-6 border-b border-slate-800 shrink-0">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 bg-blue-600/20 border border-blue-500/30 rounded-xl flex items-center justify-center">
            <History size={20} className="text-blue-400" />
          </div>
          <h1 className="text-2xl font-bold text-white">Submission History</h1>
        </div>
        <p className="text-slate-400 text-sm ml-14">View your past code executions and evaluation results.</p>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
        {loading ? (
          <div className="flex justify-center items-center h-full">
            <Loader2 size={32} className="animate-spin text-slate-500" />
          </div>
        ) : submissions.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-slate-500 gap-4">
            <Code2 size={48} className="text-slate-700" />
            <p>You haven't submitted any code yet.</p>
          </div>
        ) : (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-950/50 border-b border-slate-800 text-slate-400 text-xs uppercase tracking-wider">
                  <th className="px-6 py-4 font-semibold">Lesson / Task</th>
                  <th className="px-6 py-4 font-semibold">Date</th>
                  <th className="px-6 py-4 font-semibold">Status</th>
                  <th className="px-6 py-4 font-semibold text-right">Metrics</th>
                  <th className="px-6 py-4 font-semibold text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {submissions.map((sub, idx) => (
                  <motion.tr 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    key={sub.id} 
                    className="hover:bg-slate-800/30 transition-colors group"
                  >
                    <td className="px-6 py-4">
                      <div className="font-semibold text-slate-200">{sub.task_title || 'Unknown Task'}</div>
                      <div className="text-xs text-slate-500 mt-1">{sub.daily_plan_title || 'Unknown Plan'}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2 text-sm text-slate-400">
                        <Calendar size={14} />
                        {formatDate(sub.created_at)}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      {getStatusBadge(sub.result_status)}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex flex-col items-end gap-1">
                        <div className="flex items-center gap-1.5 text-xs text-slate-400">
                          <Clock size={12} /> {sub.execution_time ? `${sub.execution_time}s` : '-'}
                        </div>
                        <div className="flex items-center gap-1.5 text-xs text-slate-400">
                          <HardDrive size={12} /> {sub.memory_usage ? `${sub.memory_usage} KB` : '-'}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button 
                        onClick={() => setSelectedSubmission(sub)}
                        className="text-sm font-semibold text-blue-400 hover:text-blue-300 bg-blue-500/10 hover:bg-blue-500/20 px-4 py-2 rounded-lg transition-colors opacity-0 group-hover:opacity-100 focus:opacity-100"
                      >
                        View Code
                      </button>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Code Modal */}
      <AnimatePresence>
        {selectedSubmission && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 md:p-8">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedSubmission(null)}
              className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            />
            <motion.div 
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="relative w-full max-w-4xl max-h-full bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl flex flex-col overflow-hidden"
            >
              {/* Modal Header */}
              <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/50">
                <div>
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <Code2 size={18} className="text-blue-400" />
                    Submitted Code
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">
                    {selectedSubmission.task_title} • {formatDate(selectedSubmission.created_at)}
                  </p>
                </div>
                <div className="flex items-center gap-4">
                  {getStatusBadge(selectedSubmission.result_status)}
                  <button 
                    onClick={() => setSelectedSubmission(null)}
                    className="p-2 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-white transition-colors"
                  >
                    <X size={20} />
                  </button>
                </div>
              </div>
              
              {/* Modal Body */}
              <div className="flex-1 overflow-auto p-6 bg-[#1e1e1e] custom-scrollbar">
                <pre className="font-mono text-sm text-[#d4d4d4] w-full">
                  <code>{selectedSubmission.submitted_code}</code>
                </pre>
              </div>

              {/* Output & Errors (If Any) */}
              {(selectedSubmission.stdout || selectedSubmission.stderr) && (
                <div className="border-t border-slate-800 bg-slate-950 p-6 max-h-[30%] overflow-auto custom-scrollbar shrink-0">
                  {selectedSubmission.stdout && (
                    <div className="mb-4">
                      <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Standard Output</h4>
                      <pre className="font-mono text-xs text-slate-300 bg-slate-900 p-4 rounded-lg border border-slate-800">
                        {selectedSubmission.stdout}
                      </pre>
                    </div>
                  )}
                  {selectedSubmission.stderr && (
                    <div>
                      <h4 className="text-xs font-bold text-red-500 uppercase tracking-wider mb-2">Error / Stderr</h4>
                      <pre className="font-mono text-xs text-red-400 bg-red-950/20 p-4 rounded-lg border border-red-900/30 whitespace-pre-wrap">
                        {selectedSubmission.stderr}
                      </pre>
                    </div>
                  )}
                </div>
              )}
            </motion.div>
          </div>
        )}
      </AnimatePresence>

    </div>
  );
};

export default Submissions;
