from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import subprocess
import tempfile
import os
import pdfplumber

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

class RunRequest(BaseModel):
    code: str
    input: str = ""

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

@app.post("/run")
async def run_code(request: RunRequest):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(request.code)
        temp_path = f.name
        
    try:
        process = subprocess.Popen(
            ["python", temp_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8"
        )
        
        try:
            stdout, stderr = process.communicate(input=request.input, timeout=5)
            return {
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": process.returncode
            }
        except subprocess.TimeoutExpired:
            process.kill()
            return {
                "stdout": "",
                "stderr": "Error: Timeout (Codul a durat mai mult de 5 secunde. Posibilă buclă infinită).",
                "exit_code": -1
            }
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Te rog încarcă un fișier PDF.")
    
    try:
        content = await file.read()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(content)
            tmp_path = tmp.name
            
        text = ""
        try:
            with pdfplumber.open(tmp_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except:
                    pass
                
        if not text.strip():
            raise HTTPException(status_code=400, detail="Nu s-a putut extrage text din PDF (posibil să conțină doar imagini scanate).")
            
        # Cerem rezumat la Ollama
        prompt = f"Mai jos este textul pe care l-am extras deja dintr-un fișier PDF. Te rog citește-l și fă un rezumat concis, clar și bine structurat în limba română. Evidențiază ideile principale.\n\nTEXT EXTRAS DIN PDF:\n\"\"\"\n{text[:12000]}\n\"\"\"\n\nScrie direct rezumatul, fără să spui că nu poți citi fișiere PDF (pentru că textul ți-a fost deja dat)."
        
        payload = {
            "model": "qwen2.5-coder:3b",
            "messages": [
                {"role": "system", "content": "Ești un expert în analizarea documentelor. Sarcina ta este să rezumi textele care îți sunt date."},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
        
        response = requests.post(OLLAMA_URL, json=payload)
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Eroare la conectarea cu Ollama pentru generarea rezumatului.")
            
        return {"summary": response.json()["message"]["content"], "filename": file.filename}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("Porneste serverul Python Backend...")
    print("Poti deschide acum index.html in browser!")
    uvicorn.run(app, host="0.0.0.0", port=8000)
