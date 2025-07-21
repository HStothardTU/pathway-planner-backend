# Pathway Planner Backend

This is the backend service for the Pathway Planner – Teesside Transport Decarbonization tool.

## Tech Stack
- FastAPI (Python)
- SQLAlchemy (ORM)
- PostgreSQL (or SQLite for dev)
- Pydantic

## Directory Structure

```
app/
  api/
    v1/
      endpoints.py
  core/
    config.py
  db/
    base.py
    models.py
  services/
    scenario.py
  main.py
requirements.txt
.env
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the server:**
   ```bash
   uvicorn app.main:app --reload
   ```
3. **Test health endpoint:**
   Visit [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

## Next Steps
- Add endpoints for scenarios, parameters, and results
- Set up database migrations (Alembic)
- Implement business logic in `services/`
- Secure API (auth, CORS, etc.) 

---

## **Next: Setting Up GitHub Repositories**

### 1. **Initialize Git Repos Locally**

From your project root (`/Users/hannahstothard/Rehip/09072025`):

```bash
cd ../09072025
git init
# (optional) git add . && git commit -m "Initial backend scaffold"
```

For the frontend:
```bash
cd ../pathway-planner-frontend
git init
# (optional) git add . && git commit -m "Initial Streamlit frontend scaffold"
```

---

### 2. **Create GitHub Repositories**

- Go to [github.com/new](https://github.com/new) and create:
  - `pathway-planner-backend`
  - `pathway-planner-frontend`

---

### 3. **Connect Local to Remote**

For each repo, after creation, follow GitHub’s instructions, e.g.:

```bash
<code_block_to_apply_changes_from>
```

Repeat for the backend.

---



- **Frontend:** [https://github.com/HStothardTU/pathway-planner-frontend.git](https://github.com/HStothardTU/pathway-planner-frontend.git)
- **Backend:** [https://github.com/HStothardTU/pathway-planner-backend.git](https://github.com/HStothardTU/pathway-planner-backend.git)

Here are the exact commands to initialize, commit, and push your local code to these remotes:

---

## **1. Backend: pathway-planner-backend**

From your backend directory (`09072025`):

```bash
cd /Users/hannahstothard/Rehip/09072025
git init
git remote add origin https://github.com/HStothardTU/pathway-planner-backend.git
git add .
git commit -m "Initial backend scaffold"
git branch -M main
git push -u origin main
```

---

## **2. Frontend: pathway-planner-frontend**

From your frontend directory (`pathway-planner-frontend`):

```bash
cd /Users/hannahstothard/Rehip/09072025/pathway-planner-frontend
git init
git remote add origin https://github.com/HStothardTU/pathway-planner-frontend.git
git add .
git commit -m "Initial Streamlit frontend scaffold"
git branch -M main
git push -u origin main
```

---

## **.gitignore Recommendations**

Before pushing, you may want to add a `.gitignore` file to each repo to avoid committing unnecessary files:

**Backend (`09072025/.gitignore`):**
```
__pycache__/
*.pyc
.env
*.sqlite3
```

**Frontend (`pathway-planner-frontend/.gitignore`):**
```
__pycache__/
*.pyc
.env
```

---

 
([Frontend repo link][1], [Backend repo link][2])

[1]: https://github.com/HStothardTU/pathway-planner-frontend.git
[2]: https://github.com/HStothardTU/pathway-planner-backend.git 

---

To connect your Streamlit frontend to the scenario management endpoints, you’ll use the `requests` library to interact with your FastAPI backend. Here’s how you can do it step by step:

---

## 1. **Set Up API URL**

Add a variable in your frontend code for the backend API base URL:
```python
API_BASE = "http://localhost:8000/api/v1"
```

---

## 2. **Example Functions for Scenario CRUD**

Add these helper functions to your frontend (e.g., in a new `utils/api.py` file or directly in your page):

```python
import requests

API_BASE = "http://localhost:8000/api/v1"

def list_scenarios():
    response = requests.get(f"{API_BASE}/scenarios/")
    response.raise_for_status()
    return response.json()

def get_scenario(scenario_id):
    response = requests.get(f"{API_BASE}/scenarios/{scenario_id}")
    response.raise_for_status()
    return response.json()

def create_scenario(data):
    response = requests.post(f"{API_BASE}/scenarios/", json=data)
    response.raise_for_status()
    return response.json()

def update_scenario(scenario_id, data):
    response = requests.put(f"{API_BASE}/scenarios/{scenario_id}", json=data)
    response.raise_for_status()
    return response.json()

def delete_scenario(scenario_id):
    response = requests.delete(f"{API_BASE}/scenarios/{scenario_id}")
    response.raise_for_status()
    return response.status_code == 204
```

---

## 3. **Integrate with Streamlit UI**

For example, in your `pages/scenario_builder.py`:

```python
import streamlit as st
from utils.api import list_scenarios, create_scenario, update_scenario, delete_scenario

def show():
    st.title("Scenario Builder")

    # List scenarios
    scenarios = list_scenarios()
    scenario_names = [s["name"] for s in scenarios]
    selected = st.selectbox("Select a scenario", scenario_names)

    # Show details
    scenario = next((s for s in scenarios if s["name"] == selected), None)
    if scenario:
        st.write("Description:", scenario.get("description", ""))
        st.write("Tags:", scenario.get("tags", ""))
        st.write("Parameters:", scenario.get("parameters", {}))

    # Create new scenario
    with st.expander("Create new scenario"):
        name = st.text_input("Name")
        description = st.text_area("Description")
        tags = st.text_input("Tags")
        if st.button("Create"):
            data = {"name": name, "description": description, "tags": tags, "parameters": {}}
            create_scenario(data)
            st.success("Scenario created!")
            st.experimental_rerun()

    # Delete scenario
    if scenario and st.button("Delete this scenario"):
        delete_scenario(scenario["id"])
        st.success("Scenario deleted!")
        st.experimental_rerun()
```

---

## 4. **Next Steps**

- Expand the UI to allow editing/updating scenarios.
- Add error handling and user feedback.
- Optionally, cache or refresh scenario lists after changes.

---

**Would you like me to update your `scenario_builder.py` with a basic version of this, or help you build a more advanced scenario management UI?** 