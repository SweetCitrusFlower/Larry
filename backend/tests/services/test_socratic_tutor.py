import pytest
from app.services.socratic_tutor import detect_code_leakage, FALLBACK_RESPONSE
from unittest.mock import patch, AsyncMock
from app.services import socratic_tutor

def test_detect_code_leakage_markdown_block():
    text = "Here is how you do it:\n```python\nprint('hello')\n```\nHope this helps."
    assert detect_code_leakage(text) is True

def test_detect_code_leakage_inline_code():
    text = "You should use `print()` for that."
    assert detect_code_leakage(text) is True

def test_detect_code_leakage_keywords():
    text1 = "You can create a def my_function():"
    assert detect_code_leakage(text1) is True
    
    text2 = "Try to define a class MyClass:"
    assert detect_code_leakage(text2) is True
    
    text3 = "You need a function calculateTotal"
    assert detect_code_leakage(text3) is True

def test_detect_code_leakage_clean_text():
    text = "Have you considered what happens to the variables inside the loop based on the materials we studied?"
    assert detect_code_leakage(text) is False

@pytest.mark.asyncio
@patch('app.services.socratic_tutor.ChatVertexAI')
async def test_get_socratic_hint_clean_response(mock_chat_vertex_ai):
    # Mock the chain invocation to return a clean string
    mock_llm_instance = AsyncMock()
    mock_llm_instance.ainvoke.return_value = type('Response', (), {'content': "What concept from the notes applies here?"})()
    
    # We need to patch the chain directly since prompt | llm is what is invoked
    with patch('app.services.socratic_tutor.ChatPromptTemplate') as mock_prompt:
        mock_chain = AsyncMock()
        mock_chain.ainvoke.return_value = type('Response', (), {'content': "What concept from the notes applies here?"})()
        # Mock the `|` operator
        mock_prompt.from_messages.return_value.__or__.return_value = mock_chain
        
        response = await socratic_tutor.get_socratic_hint("I'm stuck", "Some context", "", "", "")
        assert response == "What concept from the notes applies here?"

@pytest.mark.asyncio
@patch('app.services.socratic_tutor.ChatVertexAI')
async def test_get_socratic_hint_code_leakage(mock_chat_vertex_ai):
    with patch('app.services.socratic_tutor.ChatPromptTemplate') as mock_prompt:
        mock_chain = AsyncMock()
        # Mock an LLM response containing code
        mock_chain.ainvoke.return_value = type('Response', (), {'content': "Here is the answer: `print(1)`"})()
        mock_prompt.from_messages.return_value.__or__.return_value = mock_chain
        
        response = await socratic_tutor.get_socratic_hint("I'm stuck", "Some context", "", "", "")
        assert response == FALLBACK_RESPONSE
