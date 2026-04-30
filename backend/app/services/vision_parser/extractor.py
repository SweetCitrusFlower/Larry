import os
from vertexai.generative_models import GenerativeModel, Part

async def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Sends raw PDF bytes to Vertex AI Gemini for multimodal extraction.
    """
    # Use environment variable with fallback
    model_name = os.getenv("VERTEX_MODEL_NAME", "gemini-1.5-flash-preview-0409")
    model = GenerativeModel(model_name)
    
    # Load raw bytes as inline data
    pdf_part = Part.from_data(data=pdf_bytes, mime_type="application/pdf")
    
    prompt = (
        "You are an expert data extraction parser. "
        "Extract all text, format tables beautifully in Markdown, and describe any diagrams/images in highly detailed paragraphs. "
        "Return strictly valid Markdown. Do not include any conversational filler like 'Here is the text'."
    )
    
    # Non-blocking async call
    response = await model.generate_content_async([prompt, pdf_part])
    return response.text
