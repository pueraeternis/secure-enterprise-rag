import asyncio
import logging
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Annotated

import aiofiles
from fastapi import APIRouter, File, HTTPException, UploadFile

from src.app.schemas.ingest import IngestResponse
from src.infrastructure.parsers.pdf import parse_pdf_sync
from src.services.ingestion import ingestion_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/ingest/file")
async def ingest_file(
    file: Annotated[UploadFile, File(...)],
) -> IngestResponse:
    """
    Upload a PDF/TXT/MD file, parse it, and index it into Milvus.
    """
    filename = Path(file.filename or "unknown")
    if filename.suffix.lower() not in (".pdf", ".txt", ".md"):
        raise HTTPException(status_code=400, detail="Only PDF, TXT, MD files supported")

    with NamedTemporaryFile(delete=False, suffix=filename.suffix) as temp_file:
        temp_path = Path(temp_file.name)

    try:
        async with aiofiles.open(temp_path, "wb") as out_file:
            while content := await file.read(1024 * 1024):
                await out_file.write(content)

        text_content = ""
        loop = asyncio.get_running_loop()

        if filename.suffix.lower() == ".pdf":
            try:
                text_content = await loop.run_in_executor(
                    None,
                    parse_pdf_sync,
                    temp_path,
                )
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e)) from e
        else:
            async with aiofiles.open(temp_path, encoding="utf-8") as f:
                text_content = await f.read()

        if not text_content.strip():
            raise HTTPException(status_code=400, detail="File is empty")

        doc = await ingestion_service.ingest_text(file.filename, text_content)

        return IngestResponse(
            filename=doc.filename,
            status="success",
            chunks_count=len(doc.chunks),
        )

    except Exception as e:
        logger.exception("Error during file ingestion")
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Error: {e!s}") from e

    finally:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except OSError as e:
                logger.warning("Failed to delete temp file %s: %s", temp_path, e)
