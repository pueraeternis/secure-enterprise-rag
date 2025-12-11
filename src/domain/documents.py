import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    """Atomic information unit for retrieval."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    score: float | None = None  # Filled during search


class IngestedDocument(BaseModel):
    """Document ingested into the system."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    chunks: list[DocumentChunk] = []
