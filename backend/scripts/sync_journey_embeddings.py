import os
import sys
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.journey import Journey
from langchain_google_vertexai import VertexAIEmbeddings

async def sync_embeddings():
    print("Starting embedding sync for existing journeys...")
    db = SessionLocal()
    try:
        # Get journeys without embeddings
        journeys = db.query(Journey).filter(Journey.prompt_embedding.is_(None)).all()
        
        if not journeys:
            print("All journeys already have embeddings. Nothing to do.")
            return

        print(f"Found {len(journeys)} journeys without embeddings.")
        
        embedding_model_name = os.getenv("VERTEX_EMBEDDING_MODEL", "text-embedding-004")
        embeddings = VertexAIEmbeddings(model=embedding_model_name)

        for journey in journeys:
            print(f"Generating embedding for journey {journey.id}: '{journey.original_prompt}'")
            emb = await embeddings.aembed_query(journey.original_prompt)
            journey.prompt_embedding = emb
            db.commit()
            print(f"Successfully updated journey {journey.id}")

        print("Finished syncing embeddings!")
    except Exception as e:
        print(f"Error during sync: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(sync_embeddings())
