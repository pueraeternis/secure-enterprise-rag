from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # API Config
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Secure Enterprise RAG"

    # Milvus Config
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_COLLECTION: str = "enterprise_rag"

    # vLLM Config (OpenAI Compatible)
    VLLM_API_BASE: str = "http://localhost:8000/v1"
    VLLM_MODEL_NAME: str = "google/gemma-2-27b-it"

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)


settings = Settings()
