import { useState, useCallback, useRef, useEffect } from 'react';

const useFrustrationDetector = ({
  lineThreshold = 10,
  timeWindowMs = 60000,
  triggerCount = 3,
  cooldownMs = 60000,
  onFrustrationDetected
}) => {
  const [deletions, setDeletions] = useState([]);
  const [lastAlertTime, setLastAlertTime] = useState(0);
  const previousLineCountRef = useRef(-1);

  // Expose a change handler
  const trackChange = useCallback((value) => {
    if (value === undefined) return;
    
    const currentLineCount = value.split('\n').length;
    
    // Skip the very first assignment so it doesn't trigger a deletion if the editor initializes with less code
    if (previousLineCountRef.current >= 0) {
      const lineDifference = previousLineCountRef.current - currentLineCount;
      
      // If user deleted more than the threshold at once
      if (lineDifference > lineThreshold) {
        const now = Date.now();
        
        setDeletions((prevDeletions) => {
          // Keep only deletions within the sliding window
          const validDeletions = prevDeletions.filter(timestamp => now - timestamp <= timeWindowMs);
          const updatedDeletions = [...validDeletions, now];
          
          if (updatedDeletions.length >= triggerCount) {
            // Check if we are past the cooldown
            if (now - lastAlertTime > cooldownMs) {
              if (onFrustrationDetected) {
                onFrustrationDetected();
              }
              setLastAlertTime(now);
              return []; // Reset after alerting
            }
          }
          return updatedDeletions;
        });
      }
    }
    
    previousLineCountRef.current = currentLineCount;
  }, [lineThreshold, timeWindowMs, triggerCount, cooldownMs, lastAlertTime, onFrustrationDetected]);

  return trackChange;
};

export default useFrustrationDetector;
