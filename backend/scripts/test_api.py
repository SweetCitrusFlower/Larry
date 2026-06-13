import requests
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.db.database import SessionLocal
from app.models.user import User
from app.core.security import create_access_token
from datetime import timedelta

db = SessionLocal()
user = db.query(User).first()
if not user:
    print("No user found")
    sys.exit(1)

access_token_expires = timedelta(minutes=60)
token = create_access_token(
    str(user.id), expires_delta=access_token_expires
)

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
data = {"prompt": "I want to learn Python basics in 3 days", "target_days": 3}

response = requests.post("http://localhost:8000/api/v1/journeys/check-similarity", headers=headers, json=data)

print(f"Status Code: {response.status_code}")
print("Response Text:")
print(response.text)
