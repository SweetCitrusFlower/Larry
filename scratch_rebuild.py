import re

with open('frontend/src/components/ChatPane.jsx', 'r') as f:
    content = f.read()

# 1. State Variables
state_vars = """  const [uploadingFile, setUploadingFile] = useState(false);
  const [showSimilarityModal, setShowSimilarityModal] = useState(false);
  const [similarJourney, setSimilarJourney] = useState(null);
  const [pendingPrompt, setPendingPrompt] = useState('');
  const [pendingDays, setPendingDays] = useState(7);"""
content = content.replace("  const [uploadingFile, setUploadingFile] = useState(false);", state_vars)

# 2. Add handleUseExisting and handleForceGenerate
methods = """  const handleUseExisting = async () => {
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
  };

  const handleForceGenerate = async () => {
    try {
      setLoading(true);
      const response = await journeyAPI.generate(pendingPrompt, pendingDays);
      const journey = response.data;

      const assistantResponse = `Great! I've generated your ${journey.journey_title} roadmap. Check it out on the right.`;
      pushMessage('assistant', assistantResponse);
      
      await chatAPI.sendMessage(pendingPrompt, 'user', null, journey.id);
      await chatAPI.sendMessage(assistantResponse, 'assistant', null, journey.id);

      navigate(`/journey/${journey.id}`);
    } catch (err) {
      const detail = err.response?.data?.detail || 'Sorry, I encountered an error. Please try again.';
      pushMessage('assistant', detail);
    } finally {
      setLoading(false);
      setShowSimilarityModal(false);
    }
  };

  const handleFileUpload"""
content = content.replace("  const handleFileUpload", methods)

# 3. Interceptor in handleSend
old_handle_send = """      if (journeyId) {
         // Modify existing journey
         const response = await journeyAPI.modify(journeyId, savedInput);
         const journey = response.data;
         const assistantResponse = `I've updated your ${journey.journey_title} roadmap based on your feedback. Check it out on the right.`;
         pushMessage('assistant', assistantResponse);
         await chatAPI.sendMessage(assistantResponse, 'assistant', null, journey.id);
         autopilotBus.emit('JOURNEY_MODIFIED');
      } else {
         // 2. Call the journey generation endpoint
         const response = await journeyAPI.generate(savedInput, savedDays);
         const journey = response.data;

         const assistantResponse = `Great! I've generated your ${journey.journey_title} roadmap. Check it out on the right.`;
         pushMessage('assistant', assistantResponse);
         
         // Persist the initial user prompt and assistant response linked to the new journey
         await chatAPI.sendMessage(savedInput, 'user', null, journey.id);
         await chatAPI.sendMessage(assistantResponse, 'assistant', null, journey.id);

         navigate(`/journey/${journey.id}`);
      }"""

new_handle_send = """      if (journeyId) {
         // Modify existing journey
         const response = await journeyAPI.modify(journeyId, savedInput);
         const journey = response.data;
         const assistantResponse = `I've updated your ${journey.journey_title} roadmap based on your feedback. Check it out on the right.`;
         pushMessage('assistant', assistantResponse);
         await chatAPI.sendMessage(assistantResponse, 'assistant', null, journey.id);
         autopilotBus.emit('JOURNEY_MODIFIED');
      } else {
         console.log(`[Similarity Interceptor] Checking similarity for prompt: "${savedInput}", days: ${savedDays}`);
         const similarityResponse = await journeyAPI.checkSimilarity(savedInput, savedDays);

         if (similarityResponse.status === 200 && similarityResponse.data && similarityResponse.data.score >= 80) {
            console.log(`[Similarity Interceptor] MATCH FOUND! Score: ${similarityResponse.data.score}`);
            setSimilarJourney(similarityResponse.data);
            setPendingPrompt(savedInput);
            setPendingDays(savedDays);
            setShowSimilarityModal(true);
            setLoading(false);
            return;
         }

         // Call the journey generation endpoint
         const response = await journeyAPI.generate(savedInput, savedDays);
         const journey = response.data;

         const assistantResponse = `Great! I've generated your ${journey.journey_title} roadmap. Check it out on the right.`;
         pushMessage('assistant', assistantResponse);
         
         await chatAPI.sendMessage(savedInput, 'user', null, journey.id);
         await chatAPI.sendMessage(assistantResponse, 'assistant', null, journey.id);

         navigate(`/journey/${journey.id}`);
      }"""

content = content.replace(old_handle_send, new_handle_send)

# 4. Modal UI
modal_ui = """      </div>

      {showSimilarityModal && similarJourney && (
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
      )}

      <div className="p-4 border-t border-slate-800 bg-slate-900/50 shrink-0">"""

content = content.replace('      </div>\n\n      <div className="p-4 border-t border-slate-800 bg-slate-900/50 shrink-0">', modal_ui)

with open('frontend/src/components/ChatPane.jsx', 'w') as f:
    f.write(content)
