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

Would you like me to generate the exact terminal commands for your setup, or do you want help with .gitignore files or initial commits? 