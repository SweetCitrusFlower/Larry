import React, { useState, useEffect } from 'react';
import { Target, CheckCircle, XCircle, Activity } from 'lucide-react';
import api from '../services/api';
import { motion } from 'framer-motion';

const StatisticsDashboard = () => {
  const [stats, setStats] = useState({
    total_submissions: 0,
    successful_submissions: 0,
    failed_submissions: 0,
    success_rate: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.get('/submissions/user/statistics');
        setStats(response.data);
      } catch (err) {
        console.error("Failed to load statistics", err);
        setError("Failed to load statistics. Please try again later.");
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="flex flex-col items-center gap-4 text-slate-400">
          <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <p>Loading your statistics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-6 rounded-2xl max-w-md text-center">
          <XCircle className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>{error}</p>
        </div>
      </div>
    );
  }

  const StatCard = ({ title, value, icon: Icon, color, delay }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className="glass-card p-6 flex items-start gap-4 hover:border-slate-700 transition-colors"
      style={{ background: 'rgba(15, 23, 42, 0.5)', border: '1px solid rgba(51, 65, 85, 0.5)', borderRadius: '1rem' }}
    >
      <div className={`p-3 rounded-xl ${color} bg-opacity-20 flex items-center justify-center`}>
        <Icon size={24} className={color.replace('bg-', 'text-')} />
      </div>
      <div>
        <h3 className="text-sm font-medium text-slate-400 mb-1">{title}</h3>
        <p className="text-3xl font-bold text-white">{value}</p>
      </div>
    </motion.div>
  );

  return (
    <div className="p-8 max-w-6xl mx-auto h-full overflow-y-auto custom-scrollbar w-full">
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-3xl font-bold text-white mb-2">My Statistics</h1>
        <p className="text-slate-400">Track your progress and coding success rate.</p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        <StatCard 
          title="Total Submissions" 
          value={stats.total_submissions} 
          icon={Activity} 
          color="bg-blue-500" 
          delay={0.1}
        />
        <StatCard 
          title="Successful" 
          value={stats.successful_submissions} 
          icon={CheckCircle} 
          color="bg-green-500" 
          delay={0.2}
        />
        <StatCard 
          title="Failed" 
          value={stats.failed_submissions} 
          icon={XCircle} 
          color="bg-red-500" 
          delay={0.3}
        />
        <StatCard 
          title="Success Rate" 
          value={`${stats.success_rate}%`} 
          icon={Target} 
          color="bg-yellow-500" 
          delay={0.4}
        />
      </div>

      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.5 }}
        className="glass-card p-8"
        style={{ background: 'rgba(15, 23, 42, 0.5)', border: '1px solid rgba(51, 65, 85, 0.5)', borderRadius: '1.5rem' }}
      >
        <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
          <Target size={20} className="text-blue-400" />
          Overall Performance
        </h2>
        
        <div className="space-y-4">
          <div className="flex justify-between text-sm">
            <span className="text-slate-400 font-medium">Success Rate</span>
            <span className="text-white font-bold">{stats.success_rate}%</span>
          </div>
          
          <div className="h-6 w-full bg-slate-800 rounded-full overflow-hidden flex relative">
            {stats.total_submissions > 0 ? (
              <>
                <motion.div 
                  initial={{ width: 0 }}
                  animate={{ width: `${stats.success_rate}%` }}
                  transition={{ duration: 1, ease: "easeOut" }}
                  className="h-full bg-gradient-to-r from-green-500 to-green-400"
                  title="Successful"
                />
                <motion.div 
                  initial={{ width: 0 }}
                  animate={{ width: `${100 - stats.success_rate}%` }}
                  transition={{ duration: 1, ease: "easeOut" }}
                  className="h-full bg-gradient-to-r from-red-500 to-red-400"
                  title="Failed"
                />
              </>
            ) : (
              <div className="h-full w-full bg-slate-700/50 flex items-center justify-center">
                <span className="text-xs text-slate-500 font-medium">No Data</span>
              </div>
            )}
          </div>
          
          <div className="flex justify-between text-xs text-slate-500 pt-2">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span>Accepted ({stats.successful_submissions})</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <span>Failed ({stats.failed_submissions})</span>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default StatisticsDashboard;
