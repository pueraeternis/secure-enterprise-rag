from llama_index.core import Document as LlamaDocument
from llama_index.core.node_parser import SentenceSplitter

from src.domain.documents import DocumentChunk, IngestedDocument
from src.infrastructure.vector_db.factory import get_index


class IngestionService:
    def __init__(self) -> None:
        self.splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)

    async def ingest_text(self, filename: str, text: str) -> IngestedDocument:
        """
        Accept raw text, splits it into chunks, generates embeddings, and stores them in Milvus.
        """
        llama_doc = LlamaDocument(
            text=text,
            metadata={"filename": filename},
        )

        index = get_index()
        index.insert(llama_doc)

        nodes = self.splitter.get_nodes_from_documents([llama_doc])

        chunks = [
            DocumentChunk(
                content=node.get_content(),
                metadata=node.metadata,
            )
            for node in nodes
        ]

        return IngestedDocument(
            filename=filename,
            chunks=chunks,
        )


# Singleton service
ingestion_service = IngestionService()
