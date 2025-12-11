import json
import time
from collections.abc import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.services.rag_service import rag_service

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]
    model: str | None = None
    stream: bool = True


class ModelCard(BaseModel):
    id: str
    object: str = "model"
    created: int = 1677610602
    owned_by: str = "openai"


class ModelList(BaseModel):
    object: str = "list"
    data: list[ModelCard]


@router.get("/models")
async def list_models() -> ModelList:
    """
    List models.
    """
    return ModelList(
        data=[
            ModelCard(id="secure-rag", owned_by="enterprise"),
        ],
    )


@router.post("/chat/completions")
async def chat_completions(request: ChatRequest) -> StreamingResponse:
    """
    OpenAI-compatible endpoint for RAG.
    """
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    last_message = request.messages[-1]
    history = [m.model_dump() for m in request.messages[:-1]]
    query = last_message.content

    async def openai_stream_generator() -> AsyncGenerator[str, None]:
        async for token in rag_service.chat_stream(query, history):
            chunk_data = {
                "id": "chatcmpl-123",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": request.model or "secure-rag",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": token},
                        "finish_reason": None,
                    },
                ],
            }
            yield f"data: {json.dumps(chunk_data)}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        openai_stream_generator(),
        media_type="text/event-stream",
    )
