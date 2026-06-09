import React, { createContext, useContext, useState, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

// Simple Global Event Bus for Autopilot
class EventBus {
  constructor() {
    this.listeners = {};
  }
  on(event, callback) {
    if (!this.listeners[event]) this.listeners[event] = [];
    this.listeners[event].push(callback);
    return () => {
      this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    };
  }
  emit(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(cb => cb(data));
    }
  }
}

export const autopilotBus = new EventBus();

const AutopilotContext = createContext();

export const useAutopilot = () => useContext(AutopilotContext);

export const AutopilotProvider = ({ children }) => {
  const [isGhostModeActive, setIsGhostModeActive] = useState(false);
  const ghostModeActiveRef = useRef(false);
  const navigate = useNavigate();

  const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

  const GHOST_TOPICS = [
    "I want to learn Object Oriented Programming in Python.",
    "Teach me how to make Python API requests.",
    "I need to master Data Structures like Dictionaries and Sets in Python.",
    "I want to understand File handling in Python."
  ];

  // Helper function to poll the DOM until a specific element is rendered
  const waitForElement = (selector, timeout = 120000, context = document) => {
    return new Promise((resolve, reject) => {
      if (context.querySelector(selector)) {
        return resolve(context.querySelector(selector));
      }

      const observer = new MutationObserver((mutations) => {
        if (context.querySelector(selector)) {
          resolve(context.querySelector(selector));
          observer.disconnect();
        }
      });

      observer.observe(document.body, {
        childList: true,
        subtree: true
      });

      setTimeout(() => {
        observer.disconnect();
        reject(new Error(`Timeout waiting for element ${selector}`));
      }, timeout);
    });
  };

  const startVisualDemo = useCallback(async () => {
    if (ghostModeActiveRef.current) {
      // Toggle off
      ghostModeActiveRef.current = false;
      setIsGhostModeActive(false);
      return;
    }

    ghostModeActiveRef.current = true;
    setIsGhostModeActive(true);

    console.log("[Ghost Mode] Starting Visual Demo loop...");

    try {
      let topicIndex = 0;
      
      while (ghostModeActiveRef.current) {
        // Ensure we start at Dashboard
        navigate('/');
        await sleep(2000);

        if (!ghostModeActiveRef.current) break;

        // Step 1: Pick a topic
        const topic = GHOST_TOPICS[topicIndex % GHOST_TOPICS.length];
        console.log(`[Ghost Mode] Step 1: Selected topic - "${topic}"`);
        topicIndex++;

        // Step 2: Simulate typing in ChatPane
        console.log("[Ghost Mode] Step 2: Simulating chat typing");
        autopilotBus.emit('GHOST_TYPE_CHAT', topic);
        
        // Wait for typing to finish
        await sleep(topic.length * 120 + 1000);
        
        if (!ghostModeActiveRef.current) break;

        // Submit chat
        autopilotBus.emit('GHOST_SUBMIT_CHAT');
        
        // Step 3: Wait for roadmap generation and navigation
        console.log("[Ghost Mode] Step 3: Waiting for roadmap generation and navigation");
        // ChatPane automatically navigates to /journey/:id upon success
        await waitForElement('.ghost-daily-plan', 120000);
        
        // Wait a moment so the user can see the generated roadmap
        await sleep(2000);

        // Step 4: Iterate through all Daily Plans
        let hasUncompletedPlans = true;
        console.log("[Ghost Mode] Step 4: Iterating through Daily Plans");

        while (hasUncompletedPlans && ghostModeActiveRef.current) {
          // Re-fetch all daily plan DOM elements to check their current status
          const planElements = Array.from(document.querySelectorAll('.ghost-daily-plan'));
          
          let planToWorkOn = null;
          let btnToClick = null;
          let actionType = null; // 'START' or 'GENERATE'

          for (const planEl of planElements) {
             const completedBtn = planEl.querySelector('.ghost-completed-btn');
             if (completedBtn) continue; // Skip completed

             const startBtn = planEl.querySelector('.ghost-start-lesson-btn');
             if (startBtn) {
               planToWorkOn = planEl;
               btnToClick = startBtn;
               actionType = 'START';
               break;
             }

             const generateBtn = planEl.querySelector('.ghost-generate-lesson-btn');
             if (generateBtn) {
               planToWorkOn = planEl;
               btnToClick = generateBtn;
               actionType = 'GENERATE';
               break;
             }
          }

          if (!planToWorkOn) {
            console.log("[Ghost Mode] All plans completed in this journey.");
            hasUncompletedPlans = false;
            break; // Journey is complete!
          }

          console.log(`[Ghost Mode] Found plan to work on. Action: ${actionType}`);

          // We have a plan to work on
          planToWorkOn.scrollIntoView({ behavior: 'smooth', block: 'center' });
          await sleep(1500);

          if (actionType === 'GENERATE') {
             btnToClick.click();
             // Wait for it to turn into a Start Lesson button within THIS specific plan
             await waitForElement('.ghost-start-lesson-btn', 120000, planToWorkOn); // Generation can take a while
             await sleep(1000);
             // Re-query the button inside this plan
             btnToClick = planToWorkOn.querySelector('.ghost-start-lesson-btn');
          }

          if (!ghostModeActiveRef.current) break;

          // Click the button to enter the Workspace
          if (btnToClick) {
            console.log("[Ghost Mode] Clicking plan button to start lesson.");
            btnToClick.click();
          }

          // Step 5: Workspace Flow
          console.log("[Ghost Mode] Step 5: Waiting for Workspace (theory and editor) to load");
          // Wait for the Workspace to load the theory and editor
          await waitForElement('#theory-container', 10000);
          await sleep(1500); // Small pause before scrolling

          if (!ghostModeActiveRef.current) break;

          // Simulate reading (scrolling theory)
          console.log("[Ghost Mode] Simulating reading (scrolling theory)");
          autopilotBus.emit('GHOST_SCROLL_THEORY');
          await sleep(5000); // Wait for scroll animation to finish

          if (!ghostModeActiveRef.current) break;

          // Type into Editor
          await sleep(1000);
          console.log("[Ghost Mode] Emitting code typing start event");
          
          // We wrap the code typing in a promise so we can wait for it
          await new Promise((resolve) => {
            const onCodeTyped = () => {
              autopilotBus.off('GHOST_CODE_TYPING_DONE', onCodeTyped);
              resolve();
            };
            autopilotBus.on('GHOST_CODE_TYPING_DONE', onCodeTyped);
            autopilotBus.emit('GHOST_TYPE_CODE_START');
          });

          if (!ghostModeActiveRef.current) break;

          // Submit Code
          console.log("[Ghost Mode] Submitting code for execution");
          autopilotBus.emit('GHOST_SUBMIT_CODE');

          // Wait for console output to show success or error
          try {
            await waitForElement('.console-output-success', 30000);
          } catch(e) {
            console.warn("Ghost mode: execution timeout or no task available", e);
          }

          if (!ghostModeActiveRef.current) break;

          // Wait 3 seconds to let user read the output
          await sleep(3000);

          // Click the back button to return to the Journey Roadmap
          console.log("[Ghost Mode] Returning to Journey roadmap");
          autopilotBus.emit('GHOST_RETURN_TO_JOURNEY');
          
          // Wait for the roadmap to mount again before the next loop
          await waitForElement('.ghost-daily-plan', 10000);
          await sleep(2000);
        }

        // Journey completed or interrupted. If ghost mode still active, the outer while loop will start a new one.
      }
    } catch (e) {
      console.error("Autopilot sequence aborted or errored", e);
    } finally {
      setIsGhostModeActive(false);
      ghostModeActiveRef.current = false;
    }
  }, [navigate]);

  const stopGhostMode = useCallback(() => {
    console.log("[Ghost Mode] Stopping via user command.");
    ghostModeActiveRef.current = false;
    setIsGhostModeActive(false);
  }, []);

  return (
    <AutopilotContext.Provider value={{ isGhostModeActive, startVisualDemo, stopGhostMode }}>
      {/* Optional: Visual overlay when ghost mode is active */}
      {isGhostModeActive && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 pointer-events-none">
          <div className="bg-purple-600/90 text-white px-6 py-2 rounded-full shadow-2xl shadow-purple-500/50 flex items-center gap-3 backdrop-blur-md animate-pulse">
             <div className="w-2 h-2 bg-white rounded-full animate-ping"></div>
             <span className="font-bold tracking-widest text-sm uppercase">Ghost Mode Active</span>
          </div>
        </div>
      )}
      {children}
    </AutopilotContext.Provider>
  );
};
