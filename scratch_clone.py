import requests

api_url = "http://localhost:8000/api/v1"

try:
    resp = requests.post(f"{api_url}/auth/login", data={"username": "user@example.com", "password": "password"})
    token = resp.json().get("access_token")
    if not token:
        print("Login failed")
        exit()
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(f"{api_url}/journeys/", headers=headers)
    journeys = resp.json()
    if not journeys:
        print("No existing journeys found to clone")
        exit()
        
    j1 = journeys[0]
    print(f"Using Journey 1: {j1['id']}")

    resp = requests.post(f"{api_url}/journeys/clone", json={"source_journey_id": j1["id"]}, headers=headers)
    j2 = resp.json()
    print("Journey 2 created (cloned):", j2["id"])

    resp = requests.get(f"{api_url}/chat-messages/?journey_id={j2['id']}", headers=headers)
    msgs = resp.json()
    print("Messages in Journey 2:", [m["content"] for m in msgs])

except Exception as e:
    print(e)
