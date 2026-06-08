import React, { createContext, useState, useEffect, useContext } from 'react';
import { favoritesAPI } from '../services/api';

const FavoritesContext = createContext();

export const useFavorites = () => {
  return useContext(FavoritesContext);
};

export const FavoritesProvider = ({ children, isAuthenticated }) => {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchFavorites = async () => {
    if (!isAuthenticated) return;
    setLoading(true);
    try {
      const res = await favoritesAPI.getFavorites();
      setFavorites(res.data);
    } catch (error) {
      console.error('Error fetching favorites:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFavorites();
  }, [isAuthenticated]);

  const addFavorite = async (itemType, itemContent) => {
    try {
      const res = await favoritesAPI.addFavorite({
        item_type: itemType,
        item_content: itemContent
      });
      // Prepend the new favorite so it shows up at the top
      setFavorites(prev => [res.data, ...prev]);
      return res.data;
    } catch (error) {
      console.error('Error adding favorite:', error);
      throw error;
    }
  };

  const removeFavorite = async (id) => {
    try {
      await favoritesAPI.removeFavorite(id);
      setFavorites(prev => prev.filter(fav => fav.id !== id));
    } catch (error) {
      console.error('Error deleting favorite:', error);
      throw error;
    }
  };

  const isFavorited = (itemType, contentMatcher) => {
    return favorites.some(fav => fav.item_type === itemType && contentMatcher(fav.item_content));
  };

  const getFavorite = (itemType, contentMatcher) => {
    return favorites.find(fav => fav.item_type === itemType && contentMatcher(fav.item_content));
  };

  return (
    <FavoritesContext.Provider value={{
      favorites,
      loading,
      fetchFavorites,
      addFavorite,
      removeFavorite,
      isFavorited,
      getFavorite
    }}>
      {children}
    </FavoritesContext.Provider>
  );
};
