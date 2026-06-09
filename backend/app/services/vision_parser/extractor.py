import os
import fitz  # PyMuPDF
import asyncio
from vertexai.generative_models import GenerativeModel, Part

async def extract_text_from_pdf(pdf_bytes: bytes, batch_size: int = 20) -> str:
    """
    Sends raw PDF bytes to Vertex AI Gemini for multimodal extraction.
    Splits large PDFs into smaller batches of pages to avoid hitting output token limits.
    """
    # CPU-bound synchronous function to split PDF into byte chunks
    def _split_pdf(raw_bytes: bytes, chunk_size: int):
        doc = fitz.open(stream=raw_bytes, filetype="pdf")
        total_pages = len(doc)
        batches = []
        
        for i in range(0, total_pages, chunk_size):
            start = i
            end = min(i + chunk_size, total_pages) - 1
            
            # Create a new blank PDF
            sub_doc = fitz.open()
            sub_doc.insert_pdf(doc, from_page=start, to_page=end)
            
            # Save to bytes
            sub_bytes = sub_doc.write()
            sub_doc.close()
            batches.append(sub_bytes)
            
        doc.close()
        return batches

    # Run the CPU-bound split operation in a thread to avoid blocking the event loop
    pdf_batches = await asyncio.to_thread(_split_pdf, pdf_bytes, batch_size)
    
    # Use environment variable with fallback
    model_name = os.getenv("VERTEX_MODEL_NAME", "gemini-2.5-pro")
    model = GenerativeModel(model_name)
    
    prompt = (
        "You are an expert data extraction parser. "
        "Extract all text, format tables beautifully in Markdown, and describe any diagrams/images in highly detailed paragraphs. "
        "Return strictly valid Markdown. Do not include any conversational filler like 'Here is the text'."
    )
    
    extracted_text_chunks = []
    
    # Send each chunk sequentially to Vertex AI
    # (Sequential avoids hitting quota limits instantly for large books)
    for idx, batch_bytes in enumerate(pdf_batches):
        print(f"Processing batch {idx+1}/{len(pdf_batches)} of PDF...")
        pdf_part = Part.from_data(data=batch_bytes, mime_type="application/pdf")
        try:
            response = await model.generate_content_async([prompt, pdf_part])
            if response.text:
                extracted_text_chunks.append(response.text)
        except Exception as e:
            print(f"Error extracting batch {idx+1}: {str(e)}")
            # We continue processing the remaining batches
            continue
            
    return "\n\n".join(extracted_text_chunks)
