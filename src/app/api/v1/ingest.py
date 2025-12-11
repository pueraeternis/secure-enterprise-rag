import asyncio
import logging
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Annotated

import aiofiles
import pypdf
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from src.services.ingestion import ingestion_service

router = APIRouter()
logger = logging.getLogger(__name__)


class IngestResponse(BaseModel):
    filename: str
    status: str
    chunks_count: int


def _parse_pdf_sync(file_path: Path) -> str:
    """
    Run in a separate thread to avoid blocking the event loop.
    """
    try:
        reader = pypdf.PdfReader(str(file_path))
        text_content = [text for page in reader.pages if (text := page.extract_text())]
        return "\n".join(text_content)
    except Exception as e:
        logger.error("Failed to parse PDF %s: %s", file_path, e)
        raise ValueError(f"Failed to parse PDF file: {e}") from e


@router.post("/ingest/file")
async def ingest_file(
    file: Annotated[UploadFile, File(...)],
) -> IngestResponse:
    """
    Upload a PDF/TXT/MD file, parse it, and index it into Milvus.
    """
    filename = Path(file.filename or "unknown")
    if filename.suffix.lower() not in (".pdf", ".txt", ".md"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF, TXT, MD files supported",
        )

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
                    _parse_pdf_sync,
                    temp_path,
                )
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e)) from e
        else:
            async with aiofiles.open(temp_path, encoding="utf-8") as f:
                text_content = await f.read()

        if not text_content.strip():
            raise HTTPException(
                status_code=400,
                detail="File is empty or text could not be extracted",
            )

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
        raise HTTPException(
            status_code=500,
            detail=f"Internal processing error: {e!s}",
        ) from e

    finally:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except OSError as e:
                logger.warning("Failed to delete temp file %s: %s", temp_path, e)
