import httpx
from typing import Dict, Any

JUDGE0_URL = "http://localhost:2358"

async def submit_code(source_code: str, language_id: int) -> Dict[str, Any]:
    """
    Submits code to Judge0 for execution and waits for the result.
    """
    url = f"{JUDGE0_URL}/submissions?base64_encoded=false&wait=true"
    payload = {
        "source_code": source_code,
        "language_id": language_id
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()
