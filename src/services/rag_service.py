from collections.abc import AsyncGenerator

from llama_index.core.schema import NodeWithScore

from src.infrastructure.llm.vllm_client import vllm_client
from src.infrastructure.vector_db.factory import get_index


class RAGService:
    async def chat_stream(
        self,
        query: str,
        history: list[dict] | None = None,
    ) -> AsyncGenerator[str, None]:
        """
        Chat with RAG: Retrieval -> Prompt Construction -> Generation
        """
        if history is None:
            history = []

        context_nodes = await self._retrieve(query)
        system_prompt = self._build_prompt(context_nodes)

        messages = (
            {"role": "system", "content": system_prompt},
            *history,
            {"role": "user", "content": query},
        )

        async for chunk in vllm_client.stream_chat(messages):
            yield chunk

    async def _retrieve(self, query_str: str, top_k: int = 5) -> list[NodeWithScore]:
        """Hybrid search in Milvus"""
        index = get_index()
        retriever = index.as_retriever(
            vector_store_query_mode="hybrid",
            similarity_top_k=top_k,
        )
        return retriever.retrieve(query_str)

    def _build_prompt(self, nodes: list[NodeWithScore]) -> str:
        """Build context with citations"""
        context_parts = []
        for node in nodes:
            filename = node.metadata.get("filename", "unknown source")
            content = node.get_content()
            context_parts.append(f"--- SOURCE ({filename}) ---\n{content}")

        context_str = "\n\n".join(context_parts)

        return f"""You are a secure AI assistant for an enterprise company.
Use the following pieces of retrieved context to answer the user's question.
If the answer is not in the context, say that you don't know based on internal documents.
Always cite the source filename when using information.

CONTEXT:
{context_str}
"""


rag_service = RAGService()
