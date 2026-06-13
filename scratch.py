import asyncio
from langchain_google_vertexai import VertexAIEmbeddings
import numpy as np
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/adc.json"

async def main():
    embeddings = VertexAIEmbeddings(model="text-embedding-004", project="project-43919676-77f2-42ed-8b8")
    
    emb1 = np.array(await embeddings.aembed_query("i want to learn python"))
    emb2 = np.array(await embeddings.aembed_query("I am interested in learning the amazing python programming language"))
    
    dot_product = np.dot(emb1, emb2)
    norm_1 = np.linalg.norm(emb1)
    norm_2 = np.linalg.norm(emb2)
    cosine_sim = dot_product / (norm_1 * norm_2)
    
    topic_score = max(0, cosine_sim) * 100
    
    existing_days = 15
    target_days = 13
    day_diff = abs(existing_days - target_days)
    duration_compatibility = max(0, 100 - (day_diff * 2))
    
    total_score = (topic_score * 0.85) + (duration_compatibility * 0.15)
    
    print(f"Topic Score: {topic_score}")
    print(f"Duration Score: {duration_compatibility}")
    print(f"Total Score: {total_score}")

asyncio.run(main())
