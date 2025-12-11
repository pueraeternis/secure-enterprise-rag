import logging
from pathlib import Path

import pypdf

logger = logging.getLogger(__name__)


def parse_pdf_sync(file_path: Path) -> str:
    """
    Parse PDF-files.
    Synchronous PDF parsing logic using pypdf.
    Designed to be run in a separate thread/executor.
    """
    try:
        reader = pypdf.PdfReader(str(file_path))
        text_content = [text for page in reader.pages if (text := page.extract_text())]
        return "\n".join(text_content)
    except Exception as e:
        logger.error("Failed to parse PDF %s: %s", file_path, e)
        raise ValueError(f"Failed to parse PDF file: {e}") from e
