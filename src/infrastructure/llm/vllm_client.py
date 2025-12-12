from collections.abc import AsyncGenerator

from openai import AsyncOpenAI

from src.core.config import settings


class VLLMClient:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            base_url=settings.VLLM_API_BASE,
            api_key=settings.VLLM_API_KEY,
        )
        self.model = settings.VLLM_MODEL_NAME

    async def stream_chat(self, messages: list[dict]) -> AsyncGenerator[str, None]:
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                temperature=0.1,
                max_tokens=2048,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            yield (
                f"\n[System Error: Could not connect to LLM Engine at {settings.VLLM_API_BASE}. Details: {e!s}]"
            )


vllm_client = VLLMClient()
