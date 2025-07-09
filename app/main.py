from fastapi import FastAPI
from app.api.v1 import endpoints
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Pathway Planner Backend",
    version="1.0.0"
)

# CORS for local frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router, prefix="/api/v1") 