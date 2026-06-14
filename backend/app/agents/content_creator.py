import os
import asyncio
import random
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.models.daily_plan import DailyPlan
from app.models.task import Task
from app.models.coding_problem import CodingProblem

from langchain_google_vertexai import ChatVertexAI, VertexAIEmbeddings
from langchain_chroma import Chroma
import chromadb
from langchain_core.prompts import ChatPromptTemplate

async def generate_daily_lesson(daily_plan_id: int, db: Session):
    """
    Content Creator Agent:
    1. Fetches the DailyPlan.
    2. Queries ChromaDB for RAG context.
    3. Generates a structured Markdown lesson using Gemini 1.5 Pro.
    4. Selects a random CodingProblem and attaches it as a Task.
    """
    # 1. Fetch DailyPlan and Update State
    daily_plan = db.query(DailyPlan).filter(DailyPlan.id == daily_plan_id).first()
    if not daily_plan:
        raise ValueError(f"DailyPlan with id {daily_plan_id} not found.")

    daily_plan.content_status = "GENERATING"
    db.commit()

    try:
        title = str(daily_plan.title)
        concepts_list = daily_plan.concepts_to_cover
        concepts = ", ".join(concepts_list) if concepts_list else ""

        # 2. Query ChromaDB for RAG Context
        chroma_host = os.getenv("CHROMA_HOST", "vectordb")
        chroma_port = int(os.getenv("CHROMA_PORT", "8000"))
        chroma_client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
        
        embedding_model_name = os.getenv("VERTEX_EMBEDDING_MODEL", "gemini-embedding-001")
        embeddings = VertexAIEmbeddings(model=embedding_model_name)
        
        vectorstore = Chroma(
            client=chroma_client,
            collection_name="larry_knowledge_base",
            embedding_function=embeddings,
        )
        
        search_query = f"{title}. Topics: {concepts}"
        # Run the similarity search in a threadpool to prevent blocking the async event loop
        retrieved_docs = await asyncio.to_thread(vectorstore.similarity_search, search_query, k=3)
        rag_context = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])

        # 3. Generate Markdown Lesson using Gemini 1.5 Pro
        llm = ChatVertexAI(
            model="gemini-2.5-pro",
            temperature=0.3  # Low temperature for educational accuracy
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert AI coding instructor. 
You must generate a comprehensive Markdown lesson divided STRICTLY into two sections:
## Teorie Generală
[Write a clean, beginner-friendly explanation of the topic here]

## Din Materialele Tale
[Write a synthesis applying the topic specifically based on the provided Context from course materials]

Respond ONLY with valid Markdown text. Do not include introductory conversational fillers."""),
            ("human", "Topic: {title}\nConcepts to cover: {concepts}\n\nContext from course materials:\n{rag_context}")
        ])
        
        chain = prompt | llm
        
        # Execute the LLM chain
        response = await chain.ainvoke({
            "title": title,
            "concepts": concepts,
            "rag_context": rag_context
        })
        
        generated_markdown = str(response.content)

        # 4. Save the generated lesson to the DailyPlan
        daily_plan.theoretical_topic_content = generated_markdown
        daily_plan.rag_context_payload = rag_context

        # 5. Smart Problem Selection
        recommended_tags = daily_plan.recommended_problem_tags or []
        problem = None
        
        if recommended_tags:
            all_problems = db.query(CodingProblem).all()
            scored_problems = []
            rec_tags_set = set(recommended_tags)
            
            for p in all_problems:
                p_tags = set(p.tags) if p.tags else set()
                if not rec_tags_set:
                    continue
                overlap = p_tags.intersection(rec_tags_set)
                match_percentage = len(overlap) / len(rec_tags_set)
                
                if match_percentage >= 0.5:
                    scored_problems.append((p, len(overlap)))
                    
            if scored_problems:
                # Group/Sort the remaining problems by their match count (highest overlap first)
                scored_problems.sort(key=lambda x: x[1], reverse=True)
                highest_score = scored_problems[0][1]
                best_matches = [p for p, score in scored_problems if score == highest_score]
                
                # Pick a random problem from the group with the highest score
                problem = random.choice(best_matches)

        # Fallback if no matching problem found or no recommended tags
        if not problem:
            problem = db.query(CodingProblem).order_by(func.random()).first()

        if problem:
            # 6. Create a Task record linked to the DailyPlan
            new_task = Task(
                daily_plan_id=daily_plan.id,
                title=problem.title,
                problem_id=problem.problem_id,
                description=problem.description,
                starter_code=problem.starter_code,
                hidden_solution=problem.hidden_solution
            )
            db.add(new_task)
        else:
            print("Warning: No CodingProblem found in the database. Task skipped.")

        daily_plan.content_status = "COMPLETED"

    except Exception as e:
        daily_plan.content_status = "FAILED"
        db.commit()
        raise e

    # 7. Commit changes to the database
    db.commit()
    db.refresh(daily_plan)
    
    return daily_plan