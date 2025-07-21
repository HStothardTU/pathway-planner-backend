from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.dialects.postgresql import JSONB
from app.db.base import Base
import os

# Use JSONB for Postgres, fallback to SQLite JSON for dev
if os.getenv("DATABASE_URL", "").startswith("postgres"):
    JSONType = JSONB
else:
    JSONType = SQLiteJSON

class Scenario(Base):
    __tablename__ = "scenarios"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    tags = Column(String, nullable=True)  # Or use JSONType for structured tags
    parameters = Column(JSONType, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 