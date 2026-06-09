# Larry: AI Coding Coaching Platform

**Version:** 1.2.0

Larry is a next-generation, web-based AI Coding Coaching platform. Designed from scratch using a Multi-Agent System (MAS) and Retrieval-Augmented Generation (RAG), Larry provides users with personalized learning journeys, dynamic curriculum generation, an isolated, real-time code execution environment, and a fully context-aware Socratic Tutor.

This document serves as the official project architecture and documentation.

---

## 🏗 Architecture Overview

The system is designed with a modern decoupled architecture, separating the client interface from the backend API, the AI orchestration layer, and the isolated code evaluation environment.

### Sequence Diagram (Journey Generation)

```mermaid
sequenceDiagram
    autonumber

    actor U as Utilizator
    participant F as Frontend React
    participant N as Nginx Reverse Proxy
    participant B as Backend FastAPI
    participant LLM as Ollama Qwen Coder
    participant DB as PostgreSQL

    U->>F: Scrie promptul de invatare
    F->>N: POST /api/v1/journeys/generate
    N->>B: Forward catre containerul Python
    B->>B: Formateaza SYSTEM_PROMPT
    B->>LLM: Cerere cu format JSON
    Note over LLM: Agentul Master Planner proceseaza...
    LLM-->>B: Returneaza JSON structurat
    B->>DB: Salveaza Journey, DailyPlans si Tasks
    DB-->>B: Confirmare salvare
    B-->>N: 200 OK + Datele Roadmap-ului
    N-->>F: Forward raspuns
    F-->>U: Randeaza interfata grafic
