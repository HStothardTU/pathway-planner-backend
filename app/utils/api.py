import requests

API_BASE = "http://localhost:8000/api/v1"

def list_scenarios():
    response = requests.get(f"{API_BASE}/scenarios/")
    if response.status_code == 200:
        return response.json()
    return []

def create_scenario(data):
    response = requests.post(f"{API_BASE}/scenarios/", json=data)
    if response.status_code == 201:
        return response.json()
    return None
