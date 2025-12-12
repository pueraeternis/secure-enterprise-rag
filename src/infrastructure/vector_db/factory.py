from functools import lru_cache

from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.milvus import MilvusVectorStore

from src.core.config import settings


@lru_cache
def get_embedding_model() -> HuggingFaceEmbedding:
    """
    Load the BGE-M3 embedding model into memory (CPU).
    Singleton: loaded once at startup.
    """
    print(
        f"⏳ Loading Embedding Model: {settings.EMBEDDING_MODEL_NAME} on {settings.EMBEDDING_DEVICE}...",
    )
    embed_model = HuggingFaceEmbedding(
        model_name=settings.EMBEDDING_MODEL_NAME,
        device=settings.EMBEDDING_DEVICE,
        trust_remote_code=True,
    )
    print("✅ Embedding Model Loaded.")
    return embed_model


def get_vector_store() -> MilvusVectorStore:
    """
    Create a Milvus client with predefined settings.
    """
    return MilvusVectorStore(
        uri=settings.MILVUS_URI,
        collection_name=settings.MILVUS_COLLECTION,
        dim=settings.MILVUS_DIM,
        overwrite=False,
        enable_sparse=True,
        hybrid_ranker="RRFRanker",
        hybrid_ranker_params={"k": 60},
    )


def get_index(vector_store: MilvusVectorStore = None) -> VectorStoreIndex:
    """
    Return a configured LlamaIndex instance bound to Milvus.
    """
    if vector_store is None:
        vector_store = get_vector_store()

    embed_model = get_embedding_model()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    return VectorStoreIndex.from_vector_store(
        vector_store,
        storage_context=storage_context,
        embed_model=embed_model,
    )
