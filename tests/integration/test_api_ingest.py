from unittest.mock import AsyncMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from src.app.main import app
from src.domain.documents import DocumentChunk, IngestedDocument
from src.services.ingestion import ingestion_service

client = TestClient(app)

# Constant for expected chunks count
EXPECTED_CHUNKS_COUNT = 2


@pytest.fixture
def mock_ingestion_service(mocker: MockerFixture) -> AsyncMock:
    """
    Fixture replaces the real ingest_text method with a mocked one.
    """
    fake_doc = IngestedDocument(
        filename="test.pdf",
        chunks=[
            DocumentChunk(content="chunk1"),
            DocumentChunk(content="chunk2"),
        ],
    )

    mock = mocker.patch.object(
        ingestion_service,
        "ingest_text",
        new_callable=AsyncMock,
    )
    mock.return_value = fake_doc
    return mock


def test_ingest_file_success(mock_ingestion_service: AsyncMock) -> None:
    """
    Tests successful file upload.
    """
    files = {
        "file": ("test.txt", b"Test content", "text/plain"),
    }

    response = client.post("/api/v1/ingest/file", files=files)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["filename"] == "test.pdf"
    assert data["status"] == "success"
    assert data["chunks_count"] == EXPECTED_CHUNKS_COUNT

    mock_ingestion_service.assert_called_once()


def test_ingest_file_invalid_extension() -> None:
    """
    Tests file extension validation.
    """
    files = {
        "file": ("test.exe", b"Binary", "application/octet-stream"),
    }

    response = client.post("/api/v1/ingest/file", files=files)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Only PDF, TXT, MD files supported" in response.json()["detail"]
