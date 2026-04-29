// Initialize Lucide icons
lucide.createIcons();

// ==========================================================================
// Monaco Editor Initialization
// ==========================================================================
let editor;

require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs' }});

require(['vs/editor/editor.main'], function() {
    editor = monaco.editor.create(document.getElementById('monaco-editor-container'), {
        value: '',
        language: 'python',
        theme: 'vs-dark',
        automaticLayout: true,
        minimap: { enabled: false },
        fontSize: 14,
        fontFamily: "'Fira Code', 'Consolas', monospace",
        scrollBeyondLastLine: false,
        roundedSelection: false,
        padding: { top: 16 }
    });
});

// Run Code function
async function runCode() {
    if (!editor) return;
    const code = editor.getValue();
    const inputData = document.getElementById('console-input').value;
    
    // Switch to output tab
    switchConsoleTab('output');
    const outputEl = document.getElementById('console-output');
    outputEl.innerHTML = '<span style="color: #9cdcfe;">Se rulează codul...</span>';
    outputEl.classList.remove('error-text');
    
    try {
        const response = await fetch('http://localhost:8000/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: code, input: inputData })
        });
        
        if (!response.ok) throw new Error("Eroare server");
        
        const data = await response.json();
        
        let finalText = "";
        if (data.stdout) finalText += data.stdout;
        if (data.stderr) {
            outputEl.classList.add('error-text');
            finalText += (finalText ? "\n" : "") + data.stderr;
        }
        
        if (!finalText) {
            finalText = "(Programul nu a afișat nimic)";
        }
        
        outputEl.innerText = finalText;
        
    } catch (e) {
        outputEl.classList.add('error-text');
        outputEl.innerText = "❌ Eroare de conectare la backend (http://localhost:8000/run). Serverul Python rulează?";
    }
}


// ==========================================================================
// Resizer Logic
// ==========================================================================
const resizer = document.getElementById('dragMe');
const leftPane = document.querySelector('.editor-pane');
const rightPane = document.querySelector('.chat-pane');

let x = 0;
let leftWidth = 0;

const mouseDownHandler = function(e) {
    x = e.clientX;
    leftWidth = leftPane.getBoundingClientRect().width;
    
    document.addEventListener('mousemove', mouseMoveHandler);
    document.addEventListener('mouseup', mouseUpHandler);
    
    // Disable text selection while dragging
    document.body.style.userSelect = 'none';
};

const mouseMoveHandler = function(e) {
    const dx = e.clientX - x;
    const newLeftWidth = ((leftWidth + dx) * 100) / resizer.parentNode.getBoundingClientRect().width;
    
    // Constraints (keep between 20% and 80%)
    if (newLeftWidth > 20 && newLeftWidth < 80) {
        leftPane.style.width = `${newLeftWidth}%`;
        leftPane.style.flex = 'none'; // Overrides flex: 1
    }
};

const mouseUpHandler = function() {
    document.removeEventListener('mousemove', mouseMoveHandler);
    document.removeEventListener('mouseup', mouseUpHandler);
    document.body.style.userSelect = '';
};

resizer.addEventListener('mousedown', mouseDownHandler);

// ==========================================================================
// Console & Horizontal Resizer Logic
// ==========================================================================
const hResizer = document.getElementById('h-dragMe');
const topPane = document.getElementById('code-section');
const bottomPane = document.getElementById('console-section');

let h_y = 0;
let topHeight = 0;

const hMouseDownHandler = function(e) {
    h_y = e.clientY;
    topHeight = topPane.getBoundingClientRect().height;
    
    document.addEventListener('mousemove', hMouseMoveHandler);
    document.addEventListener('mouseup', hMouseUpHandler);
    document.body.style.userSelect = 'none';
};

const hMouseMoveHandler = function(e) {
    const dy = e.clientY - h_y;
    const parentHeight = topPane.parentNode.getBoundingClientRect().height;
    const newTopHeight = ((topHeight + dy) * 100) / parentHeight;
    
    if (newTopHeight > 20 && newTopHeight < 80) {
        topPane.style.flex = 'none';
        topPane.style.height = `${newTopHeight}%`;
        bottomPane.style.flex = '1';
    }
};

const hMouseUpHandler = function() {
    document.removeEventListener('mousemove', hMouseMoveHandler);
    document.removeEventListener('mouseup', hMouseUpHandler);
    document.body.style.userSelect = '';
    if (editor) editor.layout(); // Refresh monaco layout
};

if(hResizer) hResizer.addEventListener('mousedown', hMouseDownHandler);

// Tabs Logic
function switchConsoleTab(tabId) {
    document.getElementById('tab-output').classList.remove('active');
    document.getElementById('tab-input').classList.remove('active');
    document.getElementById('btn-tab-output').classList.remove('active');
    document.getElementById('btn-tab-input').classList.remove('active');
    
    document.getElementById('tab-' + tabId).classList.add('active');
    document.getElementById('btn-tab-' + tabId).classList.add('active');
}


// ==========================================================================
// Chat & Ollama Logic
// ==========================================================================
let OLLAMA_MODEL = 'qwen2.5-coder:3b'; // Schimbă această variabilă cu modelul dorit
const BACKEND_URL = 'http://localhost:8000/chat'; // URL-ul serverului nostru Python

let conversationHistory = [
    { role: "system", content: "Ești un asistent de programare și expert în analizarea documentelor (AI Coach). Răspunzi concis și la obiect. Când ești întrebat de cod, te uiți pe contextul furnizat. Trebuie să folosești mereu o gramatică impecabilă în limba română, incluzând diacritice (ă, â, î, ș, ț) și o exprimare naturală, profesională." }
];

const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const messagesContainer = document.getElementById('messages');
const chatContainer = document.getElementById('chat-container');

let currentPdfFile = null;

// Auto-resize textarea
userInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight < 150 ? this.scrollHeight : 150) + 'px';
    
    if (this.value.trim() === '' && !currentPdfFile) {
        sendBtn.setAttribute('disabled', 'true');
    } else {
        sendBtn.removeAttribute('disabled');
    }
});

// Handle Enter key (Shift+Enter for new line)
userInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text && !currentPdfFile) return;

    let displayMsg = text;
    if (currentPdfFile) {
        displayMsg = `📎 **${currentPdfFile.name}**\n${text}`;
    }
    addUserMessage(displayMsg);

    userInput.value = '';
    userInput.style.height = 'auto';
    sendBtn.setAttribute('disabled', 'true');

    showTypingIndicator();

    if (currentPdfFile) {
        const formData = new FormData();
        formData.append('file', currentPdfFile);
        const fileName = currentPdfFile.name;
        
        removeAttachment();
        
        try {
            const response = await fetch('http://localhost:8000/upload-pdf', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Eroare la procesarea PDF-ului.");
            }
            
            const data = await response.json();
            const contextMsg = `[Sistem: Utilizatorul a atașat documentul ${data.filename}. Conținutul extras este:\n\n${data.text}]\n\nInstrucțiunea utilizatorului: ${text || "Citește documentul și întreabă cu ce poți ajuta."}`;
            conversationHistory.push({ role: "system", content: contextMsg });
            
            let editorCode = editor ? editor.getValue() : "";
            // We pass the user instruction or a default text to the actual chat request
            fetchOllamaResponse(text || "Am atașat documentul. Răspunde conform instrucțiunilor sistemului.", editorCode);
            
        } catch (error) {
            console.error("PDF Upload Error:", error);
            removeTypingIndicator();
            addAiMessage(`❌ Eroare la procesarea PDF-ului: ${error.message}`);
        }
    } else {
        let editorCode = editor ? editor.getValue() : "";
        fetchOllamaResponse(text, editorCode);
    }
}

async function fetchOllamaResponse(userMessage, currentCode) {
    // Adaugă contextul de cod la mesaj (invizibil pentru istoric dacă preferi, dar aici îl adăugăm la mesaj)
    let promptMessage = userMessage;
    if (currentCode.trim().length > 0) {
        promptMessage = `[Codul curent din editor este:\n${currentCode}]\n\n${userMessage}`;
    }

    conversationHistory.push({ role: "user", content: promptMessage });

    try {
        const response = await fetch(BACKEND_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model: OLLAMA_MODEL,
                messages: conversationHistory,
                stream: false
            })
        });

        if (!response.ok) {
            throw new Error(`Eroare HTTP: ${response.status}`);
        }

        const data = await response.json();
        const aiReply = data.message.content;
        
        conversationHistory.push({ role: "assistant", content: aiReply });
        
        removeTypingIndicator();
        
        // Extragem codul pentru a-l pune in editor
        const codeBlockRegex = /```[\w]*\n([\s\S]*?)```/g;
        let match;
        let lastCode = null;
        let cleanText = aiReply;
        
        while ((match = codeBlockRegex.exec(aiReply)) !== null) {
            lastCode = match[1];
        }
        
        if (lastCode) {
            // Actualizăm editorul cu ultimul bloc de cod generat
            if (editor) {
                editor.setValue(lastCode.trim());
            }
            // Înlocuim blocurile de cod din textul de chat cu un mesaj informativ
            cleanText = cleanText.replace(/```[\w]*\n([\s\S]*?)```/g, '\n<br><i style="color: #4CAF50;">(Codul a fost inserat automat în editorul din stânga)</i><br>\n');
        }

        addAiMessage(cleanText);
        
    } catch (error) {
        console.error("Ollama Error:", error);
        removeTypingIndicator();
        addAiMessage(`❌ Eroare la conectarea cu Ollama. Asigură-te că rulează local (\`ollama serve\`) și că modelul \`${OLLAMA_MODEL}\` este instalat. Mesaj tehnic: ${error.message}`);
    }
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
        addAiMessage("❌ Te rog să încarci doar fișiere PDF.");
        return;
    }
    
    currentPdfFile = file;
    document.getElementById('attachment-filename').textContent = file.name;
    document.getElementById('attachment-preview').style.display = 'flex';
    lucide.createIcons();
    
    sendBtn.removeAttribute('disabled');
}

function removeAttachment() {
    currentPdfFile = null;
    document.getElementById('pdf-upload').value = '';
    document.getElementById('attachment-preview').style.display = 'none';
    if (userInput.value.trim() === '') {
        sendBtn.setAttribute('disabled', 'true');
    }
}

function addUserMessage(text) {
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const msgHTML = `
        <div class="message user-message">
            <div class="avatar user-avatar">
                <img src="https://ui-avatars.com/api/?name=User&background=005a9e&color=fff" alt="User">
            </div>
            <div class="message-content">
                <p>${escapeHTML(text)}</p>
                <span class="timestamp">${time}</span>
            </div>
        </div>
    `;
    messagesContainer.insertAdjacentHTML('beforeend', msgHTML);
    scrollToBottom();
}

function addAiMessage(text) {
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    // Basic Markdown to HTML conversion for the mock response
    let formattedText = text
        .replace(/```([\s\S]*?)```/g, '<pre style="background: #1e1e1e; padding: 10px; border-radius: 4px; overflow-x: auto; font-family: monospace; font-size: 0.85rem; margin-top: 8px;"><code>$1</code></pre>')
        .replace(/`(.*?)`/g, '<code style="background: rgba(255,255,255,0.1); padding: 2px 4px; border-radius: 3px; font-family: monospace;">$1</code>')
        .replace(/\n/g, '<br>');

    const msgId = 'msg-' + Date.now() + Math.floor(Math.random() * 1000);

    const msgHTML = `
        <div class="message ai-message">
            <div class="avatar ai-avatar">
                <i data-lucide="bot"></i>
            </div>
            <div class="message-content">
                <p id="${msgId}">${formattedText}</p>
                <button class="pdf-btn" onclick="downloadPdf('${msgId}')" style="margin-top: 8px; font-size: 0.8rem; background: #005a9e; border: none; border-radius: 4px; color: white; padding: 4px 8px; cursor: pointer; display: inline-flex; align-items: center; gap: 4px;"><i data-lucide="download" style="width: 14px; height: 14px;"></i> Descarcă ca PDF</button>
                <span class="timestamp">${time}</span>
            </div>
        </div>
    `;
    messagesContainer.insertAdjacentHTML('beforeend', msgHTML);
    lucide.createIcons();
    scrollToBottom();
    
    // Store original text
    window[msgId + '_raw'] = text;
}

window.downloadPdf = async function(msgId) {
    const rawText = window[msgId + '_raw'];
    if (!rawText) return;
    
    try {
        const response = await fetch('http://localhost:8000/generate-pdf', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: rawText })
        });
        
        if (!response.ok) throw new Error("Eroare la generarea PDF-ului.");
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = "Notite_AI.pdf";
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
    } catch (e) {
        alert("Eroare la descărcarea PDF-ului.");
        console.error(e);
    }
}

function showTypingIndicator() {
    const typingHTML = `
        <div class="message ai-message" id="typing-indicator">
            <div class="avatar ai-avatar">
                <i data-lucide="bot"></i>
            </div>
            <div class="message-content">
                <p class="typing-indicator" style="padding: 10px 14px;">
                    <span></span><span></span><span></span>
                </p>
            </div>
        </div>
    `;
    messagesContainer.insertAdjacentHTML('beforeend', typingHTML);
    lucide.createIcons();
    scrollToBottom();
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) indicator.remove();
}

function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function clearChat() {
    // Keep only the first welcome message
    const welcomeMessage = messagesContainer.firstElementChild;
    messagesContainer.innerHTML = '';
    messagesContainer.appendChild(welcomeMessage);
    
    // Reset history
    conversationHistory = [
        { role: "system", content: "Ești un asistent de programare și expert în analizarea documentelor (AI Coach). Răspunzi concis și la obiect. Când ești întrebat de cod, te uiți pe contextul furnizat. Trebuie să folosești mereu o gramatică impecabilă în limba română, incluzând diacritice (ă, â, î, ș, ț) și o exprimare naturală, profesională." }
    ];
}

function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
        tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag])
    );
}
