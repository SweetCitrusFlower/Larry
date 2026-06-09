import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * Hook to track editor activity and detect user inactivity.
 * 
 * Features:
 * - Tracks typing, deletion, pasting, and other code modifications
 * - Maintains an inactivity timer that resets on activity
 * - Triggers callback when inactivity threshold is reached (4 minutes)
 * - Prevents duplicate notifications
 * 
 * @param {number} inactivityThreshold - Time in milliseconds before triggering callback (default: 4 minutes)
 * @param {Function} onIdleDetected - Callback function when inactivity is detected
 * @returns {Object} - { isIdle, resetTimer }
 */
export const useEditorActivity = (
  inactivityThreshold = 240000, // 4 minutes in ms
  onIdleDetected = null
) => {
  const [isIdle, setIsIdle] = useState(false);
  const timerRef = useRef(null);
  const hasTriggeredRef = useRef(false);

  /**
   * Reset the inactivity timer
   * Called whenever editor activity is detected
   */
  const resetTimer = useCallback(() => {
    // Clear existing timer
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }

    // Reset idle state if we were idle
    if (isIdle) {
      setIsIdle(false);
      hasTriggeredRef.current = false;
    }

    // Set new timer
    timerRef.current = setTimeout(() => {
      if (!hasTriggeredRef.current) {
        setIsIdle(true);
        hasTriggeredRef.current = true;
        
        // Call the provided callback
        if (onIdleDetected) {
          onIdleDetected();
        }
      }
    }, inactivityThreshold);
  }, [isIdle, inactivityThreshold, onIdleDetected]);

  /**
   * Handle any editor activity
   * Debounced to avoid resetting timer too frequently
   */
  const handleEditorActivity = useCallback(() => {
    resetTimer();
  }, [resetTimer]);

  /**
   * Allow manual reset from parent components
   * Useful after dismissing a hint
   */
  const manualReset = useCallback(() => {
    hasTriggeredRef.current = false;
    resetTimer();
  }, [resetTimer]);

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, []);

  // Initialize timer on mount
  useEffect(() => {
    resetTimer();
  }, [resetTimer]);

  return {
    isIdle,
    handleEditorActivity,
    manualReset,
  };
};

export default useEditorActivity;
