import re
import logging
from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)

# Fallback response when code leakage is detected
FALLBACK_RESPONSE = "Could you review how the concepts in your reference materials apply to this step?"

# Regex pattern to detect:
# 1. Markdown code blocks: ```...```
# 2. Inline code: `...`
# 3. Common code keywords: def, class, function
CODE_REGEX = re.compile(r'(```[\s\S]*?```|`[^`]+`|\bdef\s+\w+\b|\bclass\s+\w+\b|\bfunction\s+\w+\b)', re.IGNORECASE)

def detect_code_leakage(text: str) -> bool:
    """
    Returns True if code leakage is detected in the text.
    """
    if CODE_REGEX.search(text):
        return True
    return False

async def get_socratic_hint(user_query: str, rag_context: str) -> str:
    """
    Invokes the LLM to act as a Socratic Tutor.
    If the response contains code, it falls back to a generic question.
    """
    llm = ChatVertexAI(
        model="gemini-2.5-pro",
        temperature=0.2  # Keep it focused
    )
    
    system_prompt = """You are a Socratic Tutor. The user is stuck on a programming/technical task.
Review the provided RAG context below.

[Inherited RAG Context]
{rag_context}

DO NOT provide code solutions, code snippets, or direct answers under any circumstance.
Ask exactly one or two strategic, guiding questions that use the exact terminology from the RAG context to nudge the user toward the solution.
"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{user_query}")
    ])
    
    chain = prompt | llm
    
    try:
        response = await chain.ainvoke({
            "rag_context": rag_context or "No context provided.",
            "user_query": user_query
        })
        
        response_text = str(response.content)
        
        # Guardrail Check
        if detect_code_leakage(response_text):
            logger.warning("Code leakage detected in Socratic Tutor response. Blocking and using fallback.")
            return FALLBACK_RESPONSE
            
        return response_text
    except Exception as e:
        logger.error(f"Error in Socratic Tutor service: {str(e)}")
        return FALLBACK_RESPONSE
