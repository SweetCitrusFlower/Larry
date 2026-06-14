import os
import sys
import asyncio
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.journey import Journey
from langchain_google_vertexai import VertexAIEmbeddings

async def test_sim():
    db = SessionLocal()
    
    prompt = "I want to learn Python basics in 3 days"
    target_days = 3
    
    embedding_model_name = os.getenv("VERTEX_EMBEDDING_MODEL", "text-embedding-004")
    embeddings = VertexAIEmbeddings(model=embedding_model_name)
    query_embedding = np.array(await embeddings.aembed_query(prompt))
    
    existing_journeys = db.query(Journey).filter(Journey.prompt_embedding.is_not(None)).all()
    
    best_match = None
    best_score = 0.0

    for existing in existing_journeys:
        existing_emb = np.array(existing.prompt_embedding)
        
        # Cosine similarity
        dot_product = np.dot(query_embedding, existing_emb)
        norm_q = np.linalg.norm(query_embedding)
        norm_e = np.linalg.norm(existing_emb)
        
        if norm_q == 0 or norm_e == 0:
            print(f"Skipping journey {existing.id} due to zero norm")
            continue
            
        cosine_sim = dot_product / (norm_q * norm_e)
        topic_score = max(0, cosine_sim) * 100
        
        # Duration compatibility
        existing_days = int(existing.target_days)
        duration_compatibility = (1 - abs(existing_days - target_days) / max(existing_days, target_days)) * 100
        
        total_score = (topic_score * 0.75) + (duration_compatibility * 0.25)
        
        print(f"Journey ID: {existing.id} | Topic Score: {topic_score:.2f} | Duration Score: {duration_compatibility:.2f} | Total Score: {total_score:.2f}")

        if total_score >= 90 and total_score > best_score:
            best_score = total_score
            best_match = existing

    if best_match:
        print(f"Found best match: Journey {best_match.id} with score {best_score:.2f}")
    else:
        print("No match found")
        
    db.close()

if __name__ == "__main__":
    asyncio.run(test_sim())
