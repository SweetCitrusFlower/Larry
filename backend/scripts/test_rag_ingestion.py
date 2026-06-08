import sys
import os
import asyncio
import chromadb
from langchain_community.vectorstores import Chroma
from langchain_google_vertexai import VertexAIEmbeddings

# Add backend directory to sys.path so we can import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.vision_parser.extractor import extract_text_from_pdf
from app.services.vision_parser.chunker import chunk_markdown
from app.services.vision_parser.vector_store import store_chunks_in_chroma

async def main():
    print("--- Starting End-to-End RAG Ingestion Test ---")
    
    # 1. Define the PDF path (expecting sample_manual.pdf in the backend root)
    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    pdf_path = os.path.join(backend_root, "C:\\Users\\minas\\Downloads\\python_test.pdf")
    
    if not os.path.exists(pdf_path):
        print(f"Error: Could not find test PDF at {pdf_path}")
        print("Please place a 'sample_manual.pdf' in the 'backend' folder and run again.")
        return

    print(f"\n1. Reading PDF from: {pdf_path}")
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    # 2. Extract Text (Gemini Multimodal)
    print("\n2. Extracting text via Vertex AI Gemini...")
    markdown_text = await extract_text_from_pdf(pdf_bytes)
    print(f"   -> Extracted {len(markdown_text)} characters of Markdown.")

    # 3. Chunk the Markdown
    print("\n3. Chunking Markdown...")
    chunks = chunk_markdown(markdown_text)
    print(f"   -> Generated {len(chunks)} Document chunks.")

    # 4. Store in ChromaDB
    print("\n4. Embedding and storing chunks in ChromaDB...")
    await store_chunks_in_chroma(chunks, original_filename="sample_manual.pdf")
    print("   -> Successfully stored in ChromaDB 'larry_knowledge_base' collection.")

    # 5. Verification Step: Query ChromaDB
    print("\n--- Verification: Querying ChromaDB ---")
    
    # Re-initialize the vector store for querying
    chroma_host = os.getenv("CHROMA_HOST", "localhost")
    chroma_port = int(os.getenv("CHROMA_PORT", "8000"))
    
    chroma_client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
    
    embedding_model_name = os.getenv("VERTEX_EMBEDDING_MODEL", "text-embedding-004")
    embeddings = VertexAIEmbeddings(model_name=embedding_model_name)
    
    vectorstore = Chroma(
        client=chroma_client,
        collection_name="larry_knowledge_base",
        embedding_function=embeddings,
    )
    
    test_query = "What is the main topic or objective of this document?"
    print(f"Querying for: '{test_query}'")
    
    # Run a similarity search (synchronously, wrapping in to_thread is safe practice but not strictly required here)
    retrieved_docs = await asyncio.to_thread(vectorstore.similarity_search, test_query, k=2)
    
    for i, doc in enumerate(retrieved_docs):
        print(f"\n=== Top Result {i + 1} ===")
        print(f"Metadata: {doc.metadata}")
        # Print first 200 characters to avoid flooding the console
        content_preview = doc.page_content[:200].replace('\n', ' ')
        print(f"Content Preview: {content_preview}...")

    print("\n--- End-to-End Test Complete ---")

if __name__ == "__main__":
    # Ensure Google Cloud ADC is authenticated before running
    asyncio.run(main())
