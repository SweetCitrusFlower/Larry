import React, { useState, useEffect, forwardRef, useImperativeHandle } from 'react';
import Joyride, { STATUS } from 'react-joyride';

const TourGuide = forwardRef((props, ref) => {
  const [run, setRun] = useState(false);

  // Auto-start logic removed so that App.jsx cleanly triggers it when ready
  // Expose a method to manually restart the tour from the parent component
  useImperativeHandle(ref, () => ({
    startTour: () => {
      setRun(true);
    }
  }));

  const steps = [
    {
      target: 'body', // Centers the first welcome message
      content: 'Welcome to Larry! Let us give you a quick tour of your new AI-powered IDE.',
      placement: 'center',
      disableBeacon: true, // Don't show a pulsing beacon for the first step
    },
    {
      target: '.tour-chat',
      content: 'This is your AI Tutor. Tell Larry what you want to learn, and he will generate a complete learning journey for you!',
      placement: 'right', // Adjust based on your layout
    },
    {
      target: '.tour-sidebar',
      content: 'Here you will find your active journeys, daily plans, and previous coding submissions.',
      placement: 'right',
    },
    {
      target: '.tour-favorites',
      content: 'Save your favorite materials here for quick access later.',
      placement: 'bottom',
    }
  ];

  const handleJoyrideCallback = (data) => {
    const { status } = data;
    const finishedStatuses = [STATUS.FINISHED, STATUS.SKIPPED];
    
    // When the user finishes or skips the tour, save it in local storage
    if (finishedStatuses.includes(status)) {
      setRun(false);
      localStorage.setItem('hasSeenTour', 'true');
    }
  };

  return (
    <Joyride
      callback={handleJoyrideCallback}
      continuous={true} // Show next/back buttons
      hideCloseButton={false}
      run={run}
      scrollToFirstStep={true}
      showProgress={true} // Displays "1 of 4"
      showSkipButton={true} // Allows power users to skip
      steps={steps}
      styles={{
        options: {
          zIndex: 10000,
          primaryColor: '#007ACC', // VS Code Blue for primary actions
          backgroundColor: '#1E1E1E', // Dark editor background
          textColor: '#D4D4D4', // Light text
          arrowColor: '#1E1E1E', 
          overlayColor: 'rgba(0, 0, 0, 0.7)', // Dim the background
        },
        tooltip: {
          borderRadius: '8px',
          boxShadow: '0 4px 15px rgba(0,0,0,0.5)',
        },
        buttonNext: {
          backgroundColor: '#007ACC',
          borderRadius: '4px',
          fontWeight: 600,
        },
        buttonBack: {
          color: '#D4D4D4',
        },
        buttonSkip: {
          color: '#9CDCFE',
        }
      }}
    />
  );
});

export default TourGuide;
