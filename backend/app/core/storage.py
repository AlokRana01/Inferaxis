"""Storage abstraction layer for managing uploaded tabular datasets and artifacts."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import BinaryIO

from app.core.config import get_settings

logger = logging.getLogger("inferaxis.storage")


class StorageError(Exception):
    """Base exception for storage operations."""


class StoragePathTraversalError(StorageError):
    """Raised when a path escapes the configured root storage directory."""


class FileSizeLimitExceededError(StorageError):
    """Raised when an uploaded file exceeds the configured maximum byte size."""


class LocalStorageService:
    """Configurable local filesystem storage service.

    Stores files outside the database using sanitized, relative paths.
    Enforces directory boundary validation to prevent path traversal vulnerabilities.
    """

    def __init__(self, base_path: str | Path | None = None) -> None:
        settings = get_settings()
        self.base_path = Path(base_path or settings.STORAGE_PATH).resolve()
        self.datasets_dir = self.base_path / "datasets"
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create storage root and default subdirectories if not present."""
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.datasets_dir.mkdir(parents=True, exist_ok=True)

    def resolve_secure_path(self, relative_path: str | Path) -> Path:
        """Resolve a relative path against base_path and assert it does not escape root.

        Args:
            relative_path: Relative storage path (e.g., 'datasets/uuid.csv').

        Returns:
            Resolved absolute Path object within base_path.

        Raises:
            StoragePathTraversalError: If path escapes the configured storage root.
        """
        # Normalize relative path separators
        clean_rel = str(relative_path).lstrip("/\\")
        candidate = (self.base_path / clean_rel).resolve()
        try:
            candidate.relative_to(self.base_path)
        except ValueError as err:
            raise StoragePathTraversalError(
                f"Path traversal attempt detected: '{relative_path}' escapes storage root"
            ) from err
        return candidate

    def save_bytes(self, data: bytes, relative_path: str) -> str:
        """Write raw byte content to a relative destination path.

        Args:
            data: Raw file payload.
            relative_path: Relative destination path within storage.

        Returns:
            Normalized POSIX relative path for database storage.
        """
        target = self.resolve_secure_path(relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return Path(relative_path).as_posix()

    def save_stream(
        self,
        stream: BinaryIO,
        relative_path: str,
        max_size_bytes: int | None = None,
        chunk_size: int = 65536,
    ) -> tuple[str, int]:
        """Stream data from file-like object to storage with bounded memory and size limit.

        Args:
            stream: Readable binary stream.
            relative_path: Target relative path within storage.
            max_size_bytes: Optional upper bound on bytes allowed.
            chunk_size: Buffer size for streamed copying (default 64KB).

        Returns:
            Tuple of (normalized_relative_path, total_bytes_written).

        Raises:
            FileSizeLimitExceededError: If stream length exceeds max_size_bytes.
        """
        target = self.resolve_secure_path(relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        total_written = 0

        try:
            with target.open("wb") as out_file:
                while True:
                    chunk = stream.read(chunk_size)
                    if not chunk:
                        break
                    total_written += len(chunk)
                    if max_size_bytes is not None and total_written > max_size_bytes:
                        raise FileSizeLimitExceededError(
                            f"File size exceeds allowed maximum of {max_size_bytes} bytes "
                            f"(processed {total_written} bytes)"
                        )
                    out_file.write(chunk)
        except Exception:
            # Clean up partially written file on failure
            if target.exists():
                try:
                    target.unlink()
                except OSError:
                    pass
            raise

        return Path(relative_path).as_posix(), total_written

    def get_path(self, relative_path: str) -> Path:
        """Return resolved Path verifying existence.

        Args:
            relative_path: Relative storage path.

        Returns:
            Absolute Path.

        Raises:
            FileNotFoundError: If the target file does not exist.
        """
        target = self.resolve_secure_path(relative_path)
        if not target.exists() or not target.is_file():
            raise FileNotFoundError(f"Stored file not found: {relative_path}")
        return target

    def file_exists(self, relative_path: str) -> bool:
        """Check whether a file exists at the given relative path."""
        try:
            target = self.resolve_secure_path(relative_path)
            return target.is_file()
        except (StoragePathTraversalError, ValueError):
            return False

    def delete_file(self, relative_path: str) -> bool:
        """Safely delete a stored file if it exists.

        Args:
            relative_path: Relative storage path.

        Returns:
            True if file was deleted, False if it did not exist.
        """
        try:
            target = self.resolve_secure_path(relative_path)
            if target.is_file():
                target.unlink()
                return True
            return False
        except OSError as exc:
            logger.warning("Error deleting file %s: %s", relative_path, exc)
            return False


# Singleton storage instance
_storage_service: LocalStorageService | None = None


def get_storage_service() -> LocalStorageService:
    """Retrieve or initialize singleton storage service."""
    global _storage_service
    if _storage_service is None:
        _storage_service = LocalStorageService()
    return _storage_service
