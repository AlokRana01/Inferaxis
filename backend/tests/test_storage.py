"""Unit tests for LocalStorageService."""

import io
from pathlib import Path

import pytest
from app.core.storage import (
    FileSizeLimitExceededError,
    LocalStorageService,
    StoragePathTraversalError,
)


def test_storage_directory_creation(tmp_path: Path):
    """Verify that storage initialization creates expected directory layout."""
    storage = LocalStorageService(base_path=tmp_path / "custom_storage")
    assert storage.base_path.exists()
    assert storage.datasets_dir.exists()


def test_path_traversal_prevention(tmp_path: Path):
    """Verify that path traversal attempts raise StoragePathTraversalError."""
    storage = LocalStorageService(base_path=tmp_path)

    with pytest.raises(StoragePathTraversalError):
        storage.resolve_secure_path("../../etc/passwd")

    with pytest.raises(StoragePathTraversalError):
        storage.resolve_secure_path("datasets/../../../secret.txt")


def test_save_bytes_and_file_exists(tmp_path: Path):
    """Verify writing bytes and existence checks."""
    storage = LocalStorageService(base_path=tmp_path)
    rel_path = "datasets/test_file.csv"
    payload = b"id,val\n1,10\n"

    result_path = storage.save_bytes(payload, rel_path)
    assert result_path == "datasets/test_file.csv"
    assert storage.file_exists(rel_path) is True
    assert storage.get_path(rel_path).read_bytes() == payload


def test_save_stream_with_size_limit(tmp_path: Path):
    """Verify streaming write enforces max_size_bytes and cleans up on breach."""
    storage = LocalStorageService(base_path=tmp_path)
    stream = io.BytesIO(b"A" * 1000)

    # 1. Under limit
    path, written = storage.save_stream(
        stream, "datasets/small.txt", max_size_bytes=2000
    )
    assert written == 1000
    assert storage.file_exists(path)

    # 2. Over limit
    oversized = io.BytesIO(b"B" * 5000)
    with pytest.raises(FileSizeLimitExceededError):
        storage.save_stream(oversized, "datasets/oversized.txt", max_size_bytes=2000)

    # Assert cleaned up
    assert storage.file_exists("datasets/oversized.txt") is False


def test_delete_file(tmp_path: Path):
    """Verify deleting file returns True on success and False when not found."""
    storage = LocalStorageService(base_path=tmp_path)
    rel_path = "datasets/to_delete.txt"
    storage.save_bytes(b"content", rel_path)

    assert storage.delete_file(rel_path) is True
    assert storage.file_exists(rel_path) is False
    assert storage.delete_file(rel_path) is False
