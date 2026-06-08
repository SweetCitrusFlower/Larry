import React, { useState, useEffect } from 'react';
import axios from 'axios';

const FavoritesPanel = ({ isOpen, onClose }) => {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchFavorites();
    }
  }, [isOpen]);

  const fetchFavorites = async () => {
    setLoading(true);
    try {
      const res = await axios.get('http://127.0.0.1:8000/api/v1/favorites/');
      setFavorites(res.data);
    } catch (error) {
      console.error('Error fetching favorites:', error);
    } finally {
      setLoading(false);
    }
  };

  const removeFavorite = async (id) => {
    try {
      await axios.delete(`http://127.0.0.1:8000/api/v1/favorites/${id}`);
      setFavorites(favorites.filter(fav => fav.id !== id));
    } catch (error) {
      console.error('Error deleting favorite:', error);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      right: isOpen ? 0 : '-400px',
      width: '400px',
      height: '100vh',
      backgroundColor: '#f9f9f9',
      boxShadow: '-2px 0 5px rgba(0,0,0,0.1)',
      transition: 'right 0.3s ease',
      zIndex: 1000,
      display: 'flex',
      flexDirection: 'column'
    }}>
      <div style={{ padding: '20px', borderBottom: '1px solid #ddd', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ margin: 0 }}>My Favorites</h2>
        <button onClick={onClose} style={{ cursor: 'pointer', background: 'none', border: 'none', fontSize: '18px' }}>✕</button>
      </div>
      
      <div style={{ flex: 1, overflowY: 'auto', padding: '20px' }}>
        {loading ? (
          <p>Loading...</p>
        ) : favorites.length === 0 ? (
          <p>No favorites saved yet.</p>
        ) : (
          favorites.map(fav => (
            <div key={fav.id} style={{ background: '#fff', padding: '15px', borderRadius: '8px', marginBottom: '15px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontSize: '12px', fontWeight: 'bold', color: '#666', textTransform: 'uppercase' }}>
                  {fav.item_type}
                </span>
                <button 
                  onClick={() => removeFavorite(fav.id)}
                  style={{ color: 'red', background: 'none', border: 'none', cursor: 'pointer', fontSize: '12px' }}
                >
                  Remove
                </button>
              </div>
              <p style={{ margin: 0, whiteSpace: 'pre-wrap', fontSize: '14px', color: '#333' }}>
                {fav.item_content}
              </p>
              <small style={{ color: '#999', display: 'block', marginTop: '10px' }}>
                Saved on: {new Date(fav.created_at).toLocaleString()}
              </small>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default FavoritesPanel;
