import re

with open('frontend/src/components/ChatPane.jsx', 'r') as f:
    content = f.read()

# 1. Add SimilarityModal import
if 'import SimilarityModal' not in content:
    content = content.replace("import { autopilotBus } from '../context/AutopilotContext';", "import { autopilotBus } from '../context/AutopilotContext';\nimport SimilarityModal from './SimilarityModal';")

# 2. Add back sendMessage to handleUseExisting
old_handle_use_existing = """  const handleUseExisting = async () => {
    try {
      setLoading(true);
      const response = await journeyAPI.clone(similarJourney.journey.id, pendingPrompt);
      const journey = response.data;

      // We do NOT send any messages, because we want the chat to be clean.
      // The frontend will automatically inject the initial prompt and assistant greeting
      // because we passed `pendingPrompt` as the new original_prompt.
      navigate(`/journey/${journey.id}`);
    } catch (err) {
      const detail = err.response?.data?.detail || 'Sorry, failed to clone the journey.';
      pushMessage('assistant', detail);
    } finally {
      setLoading(false);
      setShowSimilarityModal(false);
    }
  };"""

new_handle_use_existing = """  const handleUseExisting = async () => {
    try {
      setLoading(true);
      const response = await journeyAPI.clone(similarJourney.journey.id, pendingPrompt);
      const journey = response.data;

      const assistantResponse = `I've instantly prepared the ${journey.journey_title} roadmap for you based on an existing template! Check it out on the right.`;
      pushMessage('assistant', assistantResponse);
      
      await chatAPI.sendMessage(pendingPrompt, 'user', null, journey.id);
      await chatAPI.sendMessage(assistantResponse, 'assistant', null, journey.id);

      navigate(`/journey/${journey.id}`);
    } catch (err) {
      const detail = err.response?.data?.detail || 'Sorry, failed to clone the journey.';
      pushMessage('assistant', detail);
    } finally {
      setLoading(false);
      setShowSimilarityModal(false);
    }
  };"""

content = content.replace(old_handle_use_existing, new_handle_use_existing)

# 3. Replace inline modal with SimilarityModal component
old_modal_ui = """      {showSimilarityModal && similarJourney && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 max-w-md w-full shadow-2xl">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <Sparkles className="text-blue-400" size={24} />
                Similar Journey Found
              </h2>
            </div>
            
            <p className="text-slate-300 mb-6 leading-relaxed">
              We found a highly similar existing journey: <span className="text-white font-semibold">{similarJourney.journey.journey_title}</span> ({Math.round(similarJourney.score)}% match).
            </p>
            <p className="text-slate-400 text-sm mb-8">
              You can instantly clone this journey to save generation time, or force the creation of a brand new one.
            </p>

            <div className="flex gap-4">
              <button
                onClick={() => setShowSimilarityModal(false)}
                className="flex-1 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-xl transition-colors font-medium border border-slate-700"
              >
                Cancel
              </button>
              <button
                onClick={handleForceGenerate}
                className="flex-1 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-blue-400 rounded-xl transition-colors font-medium border border-slate-700"
              >
                Force New
              </button>
              <button
                onClick={handleUseExisting}
                className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition-colors font-medium shadow-[0_0_15px_rgba(37,99,235,0.4)]"
              >
                Use Existing
              </button>
            </div>
          </div>
        </div>
      )}"""

new_modal_ui = """      <SimilarityModal 
        isOpen={showSimilarityModal}
        onClose={() => {
            setShowSimilarityModal(false);
            setLoading(false);
        }}
        similarJourney={similarJourney}
        onUseExisting={handleUseExisting}
        onForceGenerate={handleForceGenerate}
        loading={loading}
      />"""

content = content.replace(old_modal_ui, new_modal_ui)

with open('frontend/src/components/ChatPane.jsx', 'w') as f:
    f.write(content)
