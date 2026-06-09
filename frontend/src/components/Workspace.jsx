import React, { useState, useEffect, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import EditorPane from './EditorPane';
import ConsolePane from './ConsolePane';
import { taskAPI, submissionAPI, dailyPlanAPI, chatAPI, hintsAPI } from '../services/api';
import { ArrowLeft, Loader2, Send, Lightbulb } from 'lucide-react';
import IdleAssistanceNotification from './IdleAssistanceNotification';
import { useParams, useNavigate } from 'react-router-dom';
import { autopilotBus } from '../context/AutopilotContext';
import { demoAPI } from '../services/api';

const Workspace = () => {
  const { dailyPlanId } = useParams();
  const navigate = useNavigate();
  const [dailyPlan, setDailyPlan] = useState(null);
  const [task, setTask] = useState(null);
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [hintLoading, setHintLoading] = useState(false);
  const [output, setOutput] = useState('');
  const [input, setInput] = useState('');

  // Idle assistance state
  const [idleNotificationVisible, setIdleNotificationVisible] = useState(false);
  const [hintText, setHintText] = useState('');
  const [currentHintId, setCurrentHintId] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const dpRes = await dailyPlanAPI.getDailyPlan(dailyPlanId);
        setDailyPlan(dpRes.data);

        const taskRes = await taskAPI.getDailyPlanTasks(dailyPlanId);
        if (taskRes.data && taskRes.data.length > 0) {
          const fetchedTask = taskRes.data[0];
          setTask(fetchedTask);
          setCode(fetchedTask.starter_code || '');
        }
      } catch (e) {
        console.error("Failed to fetch task:", e);
      } finally {
        setLoading(false);
      }
    };
    if (dailyPlanId) {
        fetchData();
    }
  }, [dailyPlanId]);

  // Autopilot Ghost Mode listeners
  useEffect(() => {
    let typeInterval;
    const handleScroll = () => {
      const container = document.getElementById('theory-container');
      if (!container) return;
      let start = container.scrollTop;
      let end = container.scrollHeight - container.clientHeight;
      if (end <= 0) return;
      
      const duration = 5000;
      const startTime = performance.now();
      
      const animateScroll = (currentTime) => {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        container.scrollTop = start + (end - start) * progress;
        if (progress < 1) {
          requestAnimationFrame(animateScroll);
        }
      };
      requestAnimationFrame(animateScroll);
    };

    const handleTypeCode = async () => {
      if (!task) {
        autopilotBus.emit('GHOST_CODE_TYPING_DONE');
        return;
      }
      try {
        // Fetch the generated code, providing the starter code as context
        const res = await demoAPI.solveTask(task.description, task.starter_code);
        const generatedCode = res.data.code;
        
        // Clear the editor so we can type the full code from scratch
        setCode('');
        
        let i = 0;
        typeInterval = setInterval(() => {
          setCode(prev => prev + generatedCode.charAt(i));
          i++;
          if (i >= generatedCode.length) {
            clearInterval(typeInterval);
            // Tell Orchestrator we are done typing
            autopilotBus.emit('GHOST_CODE_TYPING_DONE');
          }
        }, 50); // fast typing

      } catch (err) {
        console.error("Ghost failed to solve task:", err);
        // Ensure we don't hang the orchestrator if it fails
        autopilotBus.emit('GHOST_CODE_TYPING_DONE');
      }
    };

    const handleGhostSubmit = () => {
      document.getElementById('workspace-submit-btn')?.click();
    };

    const handleGhostReturn = () => {
      handleBack();
    };

    const unsubScroll = autopilotBus.on('GHOST_SCROLL_THEORY', handleScroll);
    const unsubType = autopilotBus.on('GHOST_TYPE_CODE_START', handleTypeCode);
    const unsubSubmit = autopilotBus.on('GHOST_SUBMIT_CODE', handleGhostSubmit);
    const unsubReturn = autopilotBus.on('GHOST_RETURN_TO_JOURNEY', handleGhostReturn);

    return () => {
      clearInterval(typeInterval);
      unsubScroll();
      unsubType();
      unsubSubmit();
      unsubReturn();
    };
  }, [task]);

  const handleSubmit = async () => {
    if (!task) return;
    setSubmitting(true);
    setOutput('Executing code against hidden test cases on Judge0...\n');
    try {
      const response = await submissionAPI.submitCode(task.id, code);
      const sub = response.data;
      
      let out = `Status: ${sub.result_status.toUpperCase()}\n`;
      if (sub.execution_time) out += `Time: ${sub.execution_time}s\n`;
      if (sub.memory_usage) out += `Memory: ${sub.memory_usage}KB\n`;
      if (sub.stdout) out += `\nOutput:\n${sub.stdout}\n`;
      if (sub.stderr) out += `\nErrors/Failures:\n${sub.stderr}\n`;
      
      setOutput(out);
      
      // Inject a hidden div so the orchestrator knows it succeeded/finished
      setTimeout(() => {
         const marker = document.createElement('div');
         marker.className = 'console-output-success hidden';
         document.body.appendChild(marker);
         // Cleanup marker after a bit
         setTimeout(() => marker.remove(), 10000);
      }, 500);

    } catch (e) {
      setOutput(`Error connecting to server:\n${e.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  const handleHint = async () => {
    if (!task) return;
    const userQuery = window.prompt("What part are you stuck on?");
    if (!userQuery) return;
    
    setHintLoading(true);
    setOutput((prev) => prev + `\nAsking Larry for a hint...\n`);
    try {
      const response = await chatAPI.requestHint(dailyPlanId, userQuery);
      const hintMsg = response.data.content;
      setOutput((prev) => prev + `\n💡 LARRY TUTOR:\n${hintMsg}\n\n`);
    } catch (e) {
      setOutput((prev) => prev + `\nError getting hint:\n${e.message}\n\n`);
    } finally {
      setHintLoading(false);
    }
  }
  /**
   * Called when user has been idle for 4 minutes
   * Fetches a context-aware hint from the backend
   */
  const handleIdleDetected = useCallback(async () => {
    if (!task) return;
    
    setIdleNotificationVisible(true);
    setHintLoading(true);
    setHintText('');
    
    try {
      const response = await hintsAPI.generateHint({
        task_id: task.id,
        user_id: localStorage.getItem('userId'), // Assume userId is stored
        current_code: code
      });
      
      setHintText(response.data.hint_text);
      setCurrentHintId(response.data.id);
    } catch (e) {
      console.error("Failed to fetch hint:", e);
      setHintText("I wasn't able to generate a hint right now. Try reviewing the concepts or the problem description!");
    } finally {
      setHintLoading(false);
    }
  }, [task, code]);

  const handleDismissHint = async () => {
    if (currentHintId) {
      try {
        await hintsAPI.dismissHint(currentHintId);
      } catch (e) {
        console.error("Failed to dismiss hint:", e);
      }
    }
  };

  const handleCloseNotification = () => {
    setIdleNotificationVisible(false);
  };

  if (loading || !dailyPlan) {
    return (
      <div className="flex h-full items-center justify-center text-slate-500 w-full">
        <Loader2 className="animate-spin" size={32} />
      </div>
    );
  }

  const handleBack = () => {
    if (dailyPlan.journey_id) {
      navigate(`/journey/${dailyPlan.journey_id}`);
    } else {
      navigate('/');
    }
  };

  return (
    <div className="flex w-full h-full gap-6 animate-in fade-in duration-300">
      
      {/* LEFT PANE: Theory and Instructions */}
      <div className="w-1/2 bg-slate-900 border border-slate-800 rounded-2xl flex flex-col overflow-hidden shadow-2xl">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center bg-slate-950/50 backdrop-blur shrink-0">
           <button 
             onClick={handleBack} 
             className="p-2 -ml-2 mr-3 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-white transition-colors"
           >
              <ArrowLeft size={18} />
           </button>
           <h2 className="text-lg font-bold text-white tracking-tight">Day {dailyPlan.day_number}: {dailyPlan.title}</h2>
        </div>
        
        <div id="theory-container" className="flex-1 overflow-y-auto p-8 custom-scrollbar">
           {/* Rendering Markdown with Tailwind Typography prose */}
           <div className="prose prose-invert prose-slate max-w-none prose-headings:text-slate-100 prose-a:text-blue-400 prose-code:text-blue-300">
             <ReactMarkdown>{dailyPlan.theoretical_topic_content || '*No content generated.*'}</ReactMarkdown>
           </div>
           
           {task && (
             <div className="mt-12 pt-8 border-t border-slate-800">
                <h3 className="text-xl font-bold text-white mb-4">Coding Challenge: {task.title}</h3>
                <div className="prose prose-invert prose-slate max-w-none bg-slate-950 p-6 rounded-xl border border-slate-800">
                  <ReactMarkdown>{task.description}</ReactMarkdown>
                </div>
             </div>
           )}
        </div>
      </div>
      
      {/* RIGHT PANE: Code Editor & Console */}
      <div className="w-1/2 flex flex-col gap-6">
         
         {/* Editor */}
         <div className="flex-1 bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden flex flex-col shadow-2xl">
            <div className="px-4 py-3 border-b border-slate-800 flex justify-between items-center bg-slate-950/50 backdrop-blur shrink-0">
               <span className="text-sm font-semibold text-slate-400 tracking-wide">workspace.py</span>
               <div className="flex items-center gap-3">
                  <button 
                    onClick={handleHint} 
                    disabled={hintLoading || submitting || !task}
                    className="bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:text-slate-500 text-white px-4 py-1.5 rounded-lg text-sm font-semibold transition-all shadow-lg flex items-center gap-2"
                  >
                    {hintLoading ? <Loader2 size={16} className="animate-spin" /> : <Lightbulb size={16} />}
                    Ask Larry
                  </button>
                  <button 
                    onClick={handleSubmit} 
                    disabled={submitting || hintLoading || !task}
                    className="bg-green-600 hover:bg-green-500 disabled:bg-slate-700 disabled:text-slate-500 text-white px-5 py-1.5 rounded-lg text-sm font-semibold transition-all shadow-lg flex items-center gap-2"
                  >
                    {submitting ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
                    Run & Submit
                  </button>
               </div>
            </div>
            <div className="flex-1 min-h-0">
               <EditorPane 
                 language="python" 
                 code={code} 
                 setCode={setCode}
                 onActivityDetected={handleIdleDetected}
               />
            </div>
         </div>
         
         {/* Console */}
         <div className="h-[30%] min-h-[240px] bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden flex flex-col shadow-2xl">
            <ConsolePane output={output} input={input} setInput={setInput} />
         </div>
         
      </div>

      {/* Idle Assistance Notification */}
      <IdleAssistanceNotification
        isVisible={idleNotificationVisible}
        hint={hintText}
        loading={hintLoading}
        onDismiss={handleDismissHint}
        onClose={handleCloseNotification}
      />
    </div>
  );
};

export default Workspace;
