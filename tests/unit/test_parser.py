from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.infrastructure.parsers.pdf import parse_pdf_sync


def test_parse_pdf_sync_success() -> None:
    mock_reader = MagicMock()

    page1 = MagicMock()
    page1.extract_text.return_value = "Hello"

    page2 = MagicMock()
    page2.extract_text.return_value = "World"

    page3 = MagicMock()
    page3.extract_text.return_value = ""

    mock_reader.pages = [page1, page2, page3]

    with patch(
        "src.infrastructure.parsers.pdf.pypdf.PdfReader",
        return_value=mock_reader,
    ):
        result = parse_pdf_sync(Path("dummy.pdf"))

    assert result == "Hello\nWorld"


def test_parse_pdf_sync_error() -> None:
    with (
        patch(
            "src.infrastructure.parsers.pdf.pypdf.PdfReader",
            side_effect=Exception("Corrupted file"),
        ),
        pytest.raises(ValueError, match="Failed to parse PDF file"),
    ):
        parse_pdf_sync(Path("bad.pdf"))
