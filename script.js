// Initialize Lucide icons
lucide.createIcons();

// ==========================================================================
// Monaco Editor Initialization
// ==========================================================================
let editor;

require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs' }});

require(['vs/editor/editor.main'], function() {
    editor = monaco.editor.create(document.getElementById('monaco-editor-container'), {
        value: [
            'def calculate_fibonacci(n):',
            '    """Calculate the nth Fibonacci number."""',
            '    if n <= 0:',
            '        return 0',
            '    elif n == 1:',
            '        return 1',
            '    ',
            '    a, b = 0, 1',
            '    for _ in range(2, n + 1):',
            '        a, b = b, a + b',
            '    return b',
            '',
            '# Test the function',
            'print(f"Fibonacci of 10 is: {calculate_fibonacci(10)}")'
        ].join('\n'),
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

// Run Code function (mock)
function runCode() {
    if (!editor) return;
    const code = editor.getValue();
    
    // Simulate running code and getting output in chat
    addAiMessage(`Se rulează \`main.py\`...\n\n\`\`\`\nOutput:\nFibonacci of 10 is: 55\n\`\`\``);
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
// Chat & Ollama Logic
// ==========================================================================
let OLLAMA_MODEL = 'qwen2.5-coder:3b'; // Schimbă această variabilă cu modelul dorit
const OLLAMA_URL = 'http://localhost:11434/api/chat';

let conversationHistory = [
    { role: "system", content: "Ești un asistent de programare (AI Coach). Răspunzi concis și la obiect. Când ești întrebat de cod, te uiți pe contextul furnizat." }
];

const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const messagesContainer = document.getElementById('messages');
const chatContainer = document.getElementById('chat-container');

// Auto-resize textarea
userInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight < 150 ? this.scrollHeight : 150) + 'px';
    
    if (this.value.trim() === '') {
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

function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    addUserMessage(text);

    userInput.value = '';
    userInput.style.height = 'auto';
    sendBtn.setAttribute('disabled', 'true');

    showTypingIndicator();

    let editorCode = editor ? editor.getValue() : "";
    fetchOllamaResponse(text, editorCode);
}

async function fetchOllamaResponse(userMessage, currentCode) {
    // Adaugă contextul de cod la mesaj (invizibil pentru istoric dacă preferi, dar aici îl adăugăm la mesaj)
    let promptMessage = userMessage;
    if (currentCode.trim().length > 0) {
        promptMessage = `[Codul curent din editor este:\n${currentCode}]\n\n${userMessage}`;
    }

    conversationHistory.push({ role: "user", content: promptMessage });

    try {
        const response = await fetch(OLLAMA_URL, {
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
        addAiMessage(aiReply);
        
    } catch (error) {
        console.error("Ollama Error:", error);
        removeTypingIndicator();
        addAiMessage(`❌ Eroare la conectarea cu Ollama. Asigură-te că rulează local (\`ollama serve\`) și că modelul \`${OLLAMA_MODEL}\` este instalat. Mesaj tehnic: ${error.message}`);
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

    const msgHTML = `
        <div class="message ai-message">
            <div class="avatar ai-avatar">
                <i data-lucide="bot"></i>
            </div>
            <div class="message-content">
                <p>${formattedText}</p>
                <span class="timestamp">${time}</span>
            </div>
        </div>
    `;
    messagesContainer.insertAdjacentHTML('beforeend', msgHTML);
    lucide.createIcons();
    scrollToBottom();
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
        { role: "system", content: "Ești un asistent de programare (AI Coach). Răspunzi concis și la obiect. Când ești întrebat de cod, te uiți pe contextul furnizat." }
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
