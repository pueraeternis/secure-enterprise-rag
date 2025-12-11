from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # API Config
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Secure Enterprise RAG"

    # Milvus Config
    MILVUS_HOST: str = "milvus-standalone"
    MILVUS_PORT: int = 19530
    MILVUS_URI: str = f"http://{MILVUS_HOST}:{MILVUS_PORT}"
    MILVUS_COLLECTION: str = "enterprise_rag_hybrid"
    MILVUS_DIM: int = 1024

    # Embedding Model (Local CPU)
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-m3"
    EMBEDDING_DEVICE: str = "cpu"

    # vLLM Config
    VLLM_API_BASE: str = "http://vllm:8000/v1"
    VLLM_MODEL_NAME: str = "google/gemma-3-27b-it"
    VLLM_API_KEY: str = "secure-llm-key"

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)


settings = Settings()
