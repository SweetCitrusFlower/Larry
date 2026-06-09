import React, { useState, useEffect, useRef } from 'react';
import { knowledgeSourceAPI } from '../services/api';
import { useFavorites } from '../context/FavoritesContext';
import { Star, FileText, UploadCloud, Calendar } from 'lucide-react';
import { motion } from 'framer-motion';

const MaterialExplorer = () => {
  const [materials, setMaterials] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);
  const { addFavorite, removeFavorite, isFavorited, getFavorite } = useFavorites();

  useEffect(() => {
    fetchMaterials();
  }, []);

  const fetchMaterials = async () => {
    try {
      const res = await knowledgeSourceAPI.getKnowledgeSources();
      setMaterials(res.data);
    } catch (error) {
      console.error('Error fetching materials:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    try {
      await knowledgeSourceAPI.upload(file);
      await fetchMaterials();
    } catch (error) {
      console.error('Error uploading material:', error);
      alert('Failed to upload material: ' + (error.response?.data?.detail || error.message));
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleToggleFavorite = async (material) => {
    // We store the unique ID and title in the item_content as JSON to avoid extra fetching later.
    // However, the backend schemas might only accept a raw string. 
    // We'll store stringified JSON.
    const contentString = JSON.stringify({ id: material.id, title: material.title });
    
    // Check if it's already favorited
    // We define a matcher function for the context to find it.
    const matcher = (content) => {
      try {
        const parsed = JSON.parse(content);
        return parsed.id === material.id;
      } catch (e) {
        return false;
      }
    };

    const existingFav = getFavorite('knowledge_source', matcher);

    if (existingFav) {
      await removeFavorite(existingFav.id);
    } else {
      await addFavorite('knowledge_source', contentString);
    }
  };

  const isMaterialFavorited = (material) => {
    const matcher = (content) => {
      try {
        const parsed = JSON.parse(content);
        return parsed.id === material.id;
      } catch (e) {
        return false;
      }
    };
    return isFavorited('knowledge_source', matcher);
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar h-full w-full">
      <div className="max-w-6xl mx-auto py-8 px-4">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Material Explorer</h1>
            <p className="text-slate-400">Browse and favorite uploaded knowledge sources for your learning journey.</p>
          </div>
          <div>
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileUpload} 
              className="hidden" 
              accept=".pdf,.txt,.md,.py" 
            />
            <button 
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              <UploadCloud size={18} />
              <span>{uploading ? 'Uploading...' : 'Upload New'}</span>
            </button>
          </div>
        </div>

        {materials.length === 0 ? (
          <div className="text-center py-20 border-2 border-dashed border-slate-800 rounded-3xl">
            <FileText size={48} className="mx-auto text-slate-700 mb-4" />
            <h3 className="text-xl font-bold text-slate-300 mb-2">No Materials Found</h3>
            <p className="text-slate-500">Upload PDFs or text files to enrich the Socratic Tutor's knowledge base.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {materials.map((material) => {
              const favorited = isMaterialFavorited(material);
              return (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  key={material.id} 
                  className="bg-slate-900 border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-all flex flex-col group relative"
                >
                  <button 
                    onClick={() => handleToggleFavorite(material)}
                    className="absolute top-4 right-4 p-2 rounded-full bg-slate-950/50 hover:bg-slate-800 transition-colors z-10"
                    title={favorited ? "Remove from favorites" : "Add to favorites"}
                  >
                    <Star 
                      size={20} 
                      className={favorited ? "text-yellow-400 fill-yellow-400" : "text-slate-500 group-hover:text-slate-400"} 
                    />
                  </button>

                  <div className="w-12 h-12 bg-blue-900/30 rounded-xl flex items-center justify-center mb-4 text-blue-400">
                    <FileText size={24} />
                  </div>
                  
                  <h3 className="text-lg font-bold text-white mb-2 pr-8 truncate" title={material.title}>
                    {material.title}
                  </h3>
                  
                  <div className="mt-auto pt-4 flex items-center justify-between border-t border-slate-800">
                    <span className={`text-xs px-2 py-1 rounded-md font-medium ${
                      material.processing_status === 'completed' ? 'bg-emerald-500/10 text-emerald-400' :
                      material.processing_status === 'failed' ? 'bg-red-500/10 text-red-400' :
                      'bg-amber-500/10 text-amber-400'
                    }`}>
                      {material.processing_status === 'completed' ? 'Indexed' : material.processing_status}
                    </span>
                    <div className="flex items-center gap-1 text-slate-500 text-xs">
                      <Calendar size={12} />
                      <span>{new Date(material.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default MaterialExplorer;
