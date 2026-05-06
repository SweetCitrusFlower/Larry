import os
import httpx
import asyncio
from typing import Dict, Any, Optional

JUDGE0_API_URL = os.getenv("JUDGE0_API_URL", "http://host.docker.internal:2358")

async def submit_code(source_code: str, language_id: int, expected_output: Optional[str] = None, stdin: Optional[str] = None) -> str:
    """
    Submits code to Judge0 for execution and returns the submission token.
    """
    payload = {
        "source_code": source_code,
        "language_id": language_id,
    }
    if expected_output:
        payload["expected_output"] = expected_output
    if stdin:
        payload["stdin"] = stdin

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{JUDGE0_API_URL}/submissions/?base64_encoded=false&wait=false",
            json=payload,
            timeout=5.0
        )
        response.raise_for_status()
        data = response.json()
        return data["token"]

async def poll_submission(token: str, max_retries: int = 10, delay: float = 1.0) -> Dict[str, Any]:
    """
    Polls the Judge0 API for the result of a submission.
    """
    url = f"{JUDGE0_API_URL}/submissions/{token}?base64_encoded=false"
    
    async with httpx.AsyncClient() as client:
        for _ in range(max_retries):
            response = await client.get(url, timeout=5.0)
            response.raise_for_status()
            data = response.json()
            
            # Status IDs 1 (In Queue) and 2 (Processing) mean it's not done yet.
            status_id = data.get("status", {}).get("id")
            if status_id not in [1, 2]:
                return data
                
            await asyncio.sleep(delay)
            
    raise TimeoutError("Judge0 execution timed out during polling.")

async def execute_code(source_code: str, language_id: int, expected_output: Optional[str] = None, stdin: Optional[str] = None) -> Dict[str, Any]:
    """
    End-to-end flow: submits code and polls for the result without blocking the event loop.
    """
    token = await submit_code(source_code, language_id, expected_output, stdin)
    result = await poll_submission(token, max_retries=10, delay=1.0) # 10 seconds total polling timeout
    return result
