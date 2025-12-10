from fastapi import FastAPI

app = FastAPI(title="Secure Enterprise RAG", docs_url="/docs", openapi_url="/openapi.json")


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
