import asyncio
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_community.chat_models import ChatOllama
from langchain_google_vertexai import ChatVertexAI
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.crud.crud_user import get_user_by_email
from app.agents.experimental.autonomous_student import run_demo_student

router = APIRouter()

# Global queue to stream events from the background task to the SSE endpoint
demo_event_queue = asyncio.Queue()

@router.post("/start", status_code=status.HTTP_202_ACCEPTED)
async def start_demo(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Start the autonomous student demo in the background.
    """
    demo_email = "demo_student@aicoach.com"
    demo_user = get_user_by_email(db, email=demo_email)
    
    if not demo_user:
        raise HTTPException(status_code=404, detail="Demo student user not found. Did the seeder run?")
    
    # Put an initial event
    await demo_event_queue.put({"event": "start", "data": "Starting Autonomous Student Demo..."})
    
    # Trigger background task
    background_tasks.add_task(run_demo_student, demo_user.id, demo_event_queue)
    
    return {"message": "Demo started. Connect to /api/v1/demo/stream to watch."}

@router.get("/stream")
async def stream_demo():
    """
    SSE endpoint to stream the agent's progress.
    """
    async def event_generator():
        while True:
            # Wait for an event from the queue
            event_data = await demo_event_queue.get()
            
            # If the event is a shutdown/end signal, we can optionally break
            if event_data.get("event") == "end":
                yield f"event: end\ndata: {event_data.get('data')}\n\n"
                break
                
            # SSE format: event: <type>\ndata: <json/string>\n\n
            event_type = event_data.get("event", "message")
            data = event_data.get("data", "")
            # Ensure multi-line data is properly formatted for SSE (replace \n with \ndata: )
            data_lines = str(data).replace("\n", "\\n")
            
            yield f"event: {event_type}\ndata: {data_lines}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

from typing import Optional

class SolveTaskRequest(BaseModel):
    task_description: str
    starter_code: Optional[str] = None

@router.post("/solve-task")
async def solve_task(req: SolveTaskRequest):
    """
    Endpoint for the Visual Ghost Mode frontend orchestrator to get the code 
    to type out, acting as the 'brain'.
    """
    if req.starter_code and req.starter_code.strip():
        prompt = f"Write ONLY valid Python code to solve the following task. You MUST use and complete the provided starter code. Do not change the function signature if one is provided. No markdown blocks, no explanations, just the raw code.\n\nTask: {req.task_description}\n\nStarter Code:\n{req.starter_code}"
    else:
        prompt = f"Write ONLY valid Python code to solve the following task. No markdown blocks, no explanations, just the raw code.\nTask: {req.task_description}"
    
    try:
        # Use Gemini 2.5 Pro as requested
        llm = ChatVertexAI(model="gemini-2.5-pro", temperature=0.2)
        response = await llm.ainvoke(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    code = response.content.strip()
    # Clean up markdown blocks if present
    if code.startswith("```python"):
        code = code.replace("```python", "")
    if code.startswith("```"):
        code = code[3:]
    if code.endswith("```"):
        code = code[:-3]
    code = code.strip()
    
    return {"code": code}
