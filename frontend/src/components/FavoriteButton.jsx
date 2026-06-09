import React, { useState } from 'react';
import axios from 'axios';

const FavoriteButton = ({ itemType, itemContent }) => {
  const [isSaved, setIsSaved] = useState(false);
  const [loading, setLoading] = useState(false);

  const toggleFavorite = async () => {
    if (isSaved) return; // For MVP, we only support saving from this button. Deletion happens in the Panel.
    
    setLoading(true);
    try {
      await axios.post('http://127.0.0.1:8000/api/v1/favorites/', {
        item_type: itemType,
        item_content: itemContent
      });
      setIsSaved(true);
    } catch (error) {
      console.error('Error saving favorite:', error);
      alert('Failed to save to favorites.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <button 
      onClick={toggleFavorite} 
      disabled={loading || isSaved}
      style={{
        background: 'none',
        border: 'none',
        cursor: (loading || isSaved) ? 'default' : 'pointer',
        padding: '8px',
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
      title="Save to Favorites"
    >
      <svg 
        width="24" 
        height="24" 
        viewBox="0 0 24 24" 
        fill={isSaved ? "red" : "none"} 
        stroke={isSaved ? "red" : "currentColor"} 
        strokeWidth="2" 
        strokeLinecap="round" 
        strokeLinejoin="round"
      >
        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
      </svg>
    </button>
  );
};

export default FavoriteButton;
