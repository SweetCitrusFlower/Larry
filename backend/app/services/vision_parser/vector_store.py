import os
import chromadb
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from typing import List
import asyncio

async def store_chunks_in_chroma(chunks: List[Document], original_filename: str):
    """
    Stores LangChain Documents into a local ChromaDB instance via HTTP,
    using Google Vertex AI Embeddings.
    """
    chroma_host = os.getenv("CHROMA_HOST", "localhost")
    chroma_port = int(os.getenv("CHROMA_PORT", "8000"))
    
    # Initialize the HTTP Client
    chroma_client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
    
    # Initialize Google Embeddings (e.g., text-embedding-004)
    embedding_model_name = os.getenv("VERTEX_EMBEDDING_MODEL", "text-embedding-004")
    embeddings = VertexAIEmbeddings(model_name=embedding_model_name)
    
    # Inject source filename into metadata
    for chunk in chunks:
        if chunk.metadata is None:
            chunk.metadata = {}
        chunk.metadata["source_filename"] = original_filename
        
    # LangChain integration with Chroma HTTP Client
    vectorstore = Chroma(
        client=chroma_client,
        collection_name="larry_knowledge_base",
        embedding_function=embeddings,
    )
    
    # Add documents. LangChain's Chroma wrapper handles embedding computation.
    # Note: add_documents is synchronous, we run it in a threadpool to not block the FastAPI event loop.
    await asyncio.to_thread(vectorstore.add_documents, chunks)
