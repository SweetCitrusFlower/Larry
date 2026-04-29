from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import subprocess
import tempfile
import os
import pdfplumber
from fpdf import FPDF
import io
import re
from fastapi.responses import Response
import markdown
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

class GeneratePdfRequest(BaseModel):
    text: str

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
            
        return {"text": text[:15000], "filename": file.filename}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def strip_markdown(text: str) -> str:
    text = re.sub(r'^#+\s*(.*)', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    return text

@app.post("/generate-pdf")
async def generate_pdf(request: GeneratePdfRequest):
    pdf = FPDF()
    pdf.add_page()
    
    import urllib.request
    base_url = "https://github.com/googlefonts/roboto/raw/main/src/hinted/"
    fonts = {
        '': 'Roboto-Regular.ttf',
        'B': 'Roboto-Bold.ttf',
        'I': 'Roboto-Italic.ttf'
    }
    
    font_loaded = True
    for style, fname in fonts.items():
        if not os.path.exists(fname):
            try:
                urllib.request.urlretrieve(base_url + fname, fname)
            except:
                font_loaded = False
                break
        if font_loaded:
            pdf.add_font("Roboto", style=style, fname=fname)
            
    if font_loaded:
        pdf.set_font("Roboto", size=12)
    else:
        pdf.set_font("Helvetica", size=12)
        replacements = {'ă':'a', 'â':'a', 'î':'i', 'ș':'s', 'ț':'t', 'Ă':'A', 'Â':'A', 'Î':'I', 'Ș':'S', 'Ț':'T'}
        for k, v in replacements.items():
            request.text = request.text.replace(k, v)
            
    # Convert markdown to html
    html = markdown.markdown(request.text, extensions=['fenced_code', 'tables'])
    
    # fpdf2 write_html method natively handles standard html tags
    pdf.write_html(html)
    
    pdf_out = bytes(pdf.output())
    return Response(content=pdf_out, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=notite.pdf"})


if __name__ == "__main__":
    import uvicorn
    print("Porneste serverul Python Backend...")
    print("Poti deschide acum index.html in browser!")
    uvicorn.run(app, host="0.0.0.0", port=8000)
