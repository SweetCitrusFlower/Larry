from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

# Permitem cereri de la orice origine (frontend-ul nostru local)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    model: str
    messages: list
    stream: bool = False

OLLAMA_URL = "http://localhost:11434/api/chat"

@app.post("/chat")
async def chat_with_ollama(request: ChatRequest):
    try:
        payload = {
            "model": request.model,
            "messages": request.messages,
            "stream": request.stream
        }
        
        # Facem request către Ollama local
        response = requests.post(OLLAMA_URL, json=payload)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Ollama a răspuns cu eroare: {response.text}")
            
        return response.json()
        
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503, 
            detail="Nu mă pot conecta la Ollama. Asigură-te că aplicația Ollama rulează (ollama serve) pe acest calculator."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Rulăm serverul pe portul 8000
    print("Porneste serverul Python Backend...")
    print("Poti deschide acum index.html in browser!")
    uvicorn.run(app, host="0.0.0.0", port=8000)
