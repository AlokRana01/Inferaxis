"""Tabular data ingestion service for CSV and XLSX file formats.

Handles encoding detection, delimiter inference, schema sanitization, and security guardrails.
Never executes arbitrary code, macros, or spreadsheet formulas.
"""

from __future__ import annotations

import csv
import io
import logging
import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, BinaryIO, ClassVar

import chardet
import openpyxl
import pandas as pd

from app.core.config import get_settings

logger = logging.getLogger("inferaxis.ingestor")


class IngestionError(Exception):
    """Base exception for all ingestion-related errors."""


class EmptyFileError(IngestionError):
    """Raised when an ingested file has 0 bytes or contains no data rows."""


class UnsupportedFileFormatError(IngestionError):
    """Raised when the file format or extension is not supported."""


class FileParsingError(IngestionError):
    """Raised when parsing fails due to corrupted structure or invalid data."""


class RowCountLimitExceededError(IngestionError):
    """Raised when a dataset exceeds the configured maximum row count."""


class ColumnCountLimitExceededError(IngestionError):
    """Raised when a dataset exceeds the configured maximum column count."""


class EncodingDetectionError(IngestionError):
    """Raised when text encoding cannot be reliably detected or decoded."""


@dataclass(frozen=True)
class ColumnSchema:
    """Schema descriptor for a single tabular column."""

    name: str
    original_name: str
    dtype: str
    inferred_type: str
    nullable: bool


@dataclass
class IngestionResult:
    """Standardized output produced by DataIngestor."""

    dataframe: pd.DataFrame
    file_name: str
    file_size_bytes: int
    mime_type: str
    row_count: int
    col_count: int
    encoding: str | None = None
    delimiter: str | None = None
    sheets: list[str] = field(default_factory=list)
    selected_sheet: str | None = None
    original_columns: list[str] = field(default_factory=list)
    normalized_columns: list[str] = field(default_factory=list)
    column_schemas: list[ColumnSchema] = field(default_factory=list)
    import_warnings: list[str] = field(default_factory=list)

    def to_schema_metadata(self) -> dict[str, Any]:
        """Convert ingestion schema and format metadata to a JSON-serializable dictionary."""
        return {
            "file_name": self.file_name,
            "file_size_bytes": self.file_size_bytes,
            "mime_type": self.mime_type,
            "row_count": self.row_count,
            "col_count": self.col_count,
            "encoding": self.encoding,
            "delimiter": self.delimiter,
            "sheets": self.sheets,
            "selected_sheet": self.selected_sheet,
            "columns": [
                {
                    "name": col.name,
                    "original_name": col.original_name,
                    "dtype": col.dtype,
                    "inferred_type": col.inferred_type,
                    "nullable": col.nullable,
                }
                for col in self.column_schemas
            ],
            "import_warnings": self.import_warnings,
        }


class DataIngestor:
    """Autonomous tabular data ingestion engine for Inferaxis."""

    SUPPORTED_EXTENSIONS: ClassVar[set[str]] = {".csv", ".tsv", ".xlsx"}
    DEFAULT_DELIMITERS: ClassVar[list[str]] = [",", ";", "\t", "|"]
    FALLBACK_ENCODINGS: ClassVar[list[str]] = [
        "utf-8",
        "utf-8-sig",
        "latin1",
        "cp1252",
        "iso-8859-1",
    ]

    def __init__(
        self,
        max_file_size_bytes: int | None = None,
        max_rows: int = 1_000_000,
        max_cols: int = 500,
    ) -> None:
        settings = get_settings()
        self.max_file_size_bytes = max_file_size_bytes or settings.MAX_UPLOAD_SIZE_BYTES
        self.max_rows = max_rows
        self.max_cols = max_cols

    def ingest_file(
        self,
        file_path: str | Path,
        original_filename: str | None = None,
        sheet_name: str | None = None,
    ) -> IngestionResult:
        """Ingest a tabular file from the local storage path.

        Args:
            file_path: Absolute or storage-resolved path to the file.
            original_filename: Optional user-supplied filename. Defaults to path name.
            sheet_name: Optional target worksheet for Excel files.

        Returns:
            IngestionResult containing DataFrame and schema metadata.
        """
        path = Path(file_path).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"File not found for ingestion: {file_path}")

        file_size = path.stat().st_size
        if file_size == 0:
            raise EmptyFileError(f"File is empty (0 bytes): {path.name}")

        if file_size > self.max_file_size_bytes:
            raise IngestionError(
                f"File size ({file_size} bytes) exceeds limit of {self.max_file_size_bytes} bytes"
            )

        name = original_filename or path.name
        suffix = Path(name).suffix.lower()

        if suffix not in self.SUPPORTED_EXTENSIONS:
            raise UnsupportedFileFormatError(
                f"Unsupported file format '{suffix}'. Allowed: {', '.join(sorted(self.SUPPORTED_EXTENSIONS))}"
            )

        if suffix in {".csv", ".tsv"}:
            return self._ingest_csv(path, name, file_size)
        elif suffix == ".xlsx":
            return self._ingest_xlsx(path, name, file_size, sheet_name=sheet_name)
        else:
            raise UnsupportedFileFormatError(f"Format handler not found for '{suffix}'")

    def ingest_bytes(
        self,
        data: bytes,
        file_name: str,
        sheet_name: str | None = None,
    ) -> IngestionResult:
        """Ingest tabular data directly from in-memory bytes."""
        if not data:
            raise EmptyFileError(f"Supplied data is empty (0 bytes): {file_name}")

        file_size = len(data)
        if file_size > self.max_file_size_bytes:
            raise IngestionError(
                f"Payload size ({file_size} bytes) exceeds limit of {self.max_file_size_bytes} bytes"
            )

        suffix = Path(file_name).suffix.lower()
        if suffix not in self.SUPPORTED_EXTENSIONS:
            raise UnsupportedFileFormatError(
                f"Unsupported file format '{suffix}'. Allowed: {', '.join(sorted(self.SUPPORTED_EXTENSIONS))}"
            )

        buffer = io.BytesIO(data)
        if suffix in {".csv", ".tsv"}:
            return self._ingest_csv_stream(buffer, file_name, file_size)
        else:
            return self._ingest_xlsx_stream(
                buffer, file_name, file_size, sheet_name=sheet_name
            )

    # -------------------------------------------------------------------------
    # CSV / TSV Parsing
    # -------------------------------------------------------------------------

    def detect_encoding(self, sample_bytes: bytes) -> str:
        """Detect encoding using BOM sniffing with chardet fallback."""
        if sample_bytes.startswith(b"\xef\xbb\xbf"):
            return "utf-8-sig"
        if sample_bytes.startswith((b"\xff\xfe", b"\xfe\xff")):
            return "utf-16"

        detected = chardet.detect(sample_bytes)
        encoding = detected.get("encoding")
        confidence = detected.get("confidence", 0.0) or 0.0

        if encoding and confidence >= 0.7:
            # Normalize common names
            clean_enc = encoding.lower().strip()
            if clean_enc in {"ascii", "utf-8"}:
                return "utf-8"
            return clean_enc

        # Test fallback encodings in priority order
        for enc in self.FALLBACK_ENCODINGS:
            try:
                sample_bytes.decode(enc)
                return enc
            except (UnicodeDecodeError, LookupError):
                continue

        return "utf-8"

    def detect_delimiter(self, text_sample: str) -> str:
        """Infer CSV delimiter using csv.Sniffer with line-frequency heuristic fallback."""
        if not text_sample.strip():
            return ","

        lines = [line for line in text_sample.splitlines() if line.strip()][:10]
        if not lines:
            return ","

        sample_block = "\n".join(lines)
        try:
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample_block, delimiters=",\t;|")
            if dialect.delimiter in self.DEFAULT_DELIMITERS:
                return dialect.delimiter
        except (csv.Error, TypeError):
            pass

        # Fallback: Count frequency of candidate delimiters across sample lines
        delimiter_scores: dict[str, int] = {}
        for delim in self.DEFAULT_DELIMITERS:
            counts = [line.count(delim) for line in lines]
            # Must appear in the first row and have non-zero consistency
            if counts and counts[0] > 0 and len(set(counts)) == 1:
                delimiter_scores[delim] = counts[0] * 10
            elif counts and counts[0] > 0:
                delimiter_scores[delim] = sum(counts)

        if delimiter_scores:
            return max(delimiter_scores, key=delimiter_scores.get)  # type: ignore

        return ","

    def _ingest_csv(
        self, path: Path, file_name: str, file_size: int
    ) -> IngestionResult:
        with path.open("rb") as f:
            sample = f.read(65536)  # Read first 64KB for sniffer
        return self._ingest_csv_from_bytes(
            path.read_bytes(), sample, file_name, file_size
        )

    def _ingest_csv_stream(
        self, stream: io.BytesIO, file_name: str, file_size: int
    ) -> IngestionResult:
        stream.seek(0)
        sample = stream.read(65536)
        stream.seek(0)
        return self._ingest_csv_from_bytes(stream.read(), sample, file_name, file_size)

    def _ingest_csv_from_bytes(
        self, full_bytes: bytes, sample_bytes: bytes, file_name: str, file_size: int
    ) -> IngestionResult:
        if not full_bytes.strip():
            raise EmptyFileError(f"CSV file contains no content: {file_name}")

        encoding = self.detect_encoding(sample_bytes)
        warnings: list[str] = []

        try:
            text_sample = sample_bytes.decode(encoding, errors="replace")
        except (UnicodeDecodeError, LookupError):
            text_sample = sample_bytes.decode("latin1", errors="replace")
            encoding = "latin1"
            warnings.append("Fell back to latin1 encoding after initial decode issue.")

        delimiter = self.detect_delimiter(text_sample)

        try:
            buffer = io.BytesIO(full_bytes)
            # Use pandas read_csv with low_memory=False and safe type inference
            df = pd.read_csv(
                buffer,
                sep=delimiter,
                encoding=encoding,
                encoding_errors="replace",
                on_bad_lines="warn",
                nrows=self.max_rows + 1,
            )
        except (pd.errors.ParserError, ValueError, OSError, TypeError) as exc:
            logger.warning("Primary CSV parse failed (%s); trying fallback engine", exc)
            try:
                buffer.seek(0)
                df = pd.read_csv(
                    buffer,
                    sep=None,
                    engine="python",
                    encoding=encoding,
                    encoding_errors="replace",
                    on_bad_lines="skip",
                    nrows=self.max_rows + 1,
                )
                warnings.append("Used python engine fallback for CSV parsing.")
            except (pd.errors.ParserError, ValueError, OSError, TypeError) as inner_exc:
                raise FileParsingError(
                    f"Failed to parse CSV file: {inner_exc}"
                ) from inner_exc

        if df.empty and len(df.columns) == 0:
            raise EmptyFileError(f"Parsed CSV contains no rows or columns: {file_name}")

        if len(df) > self.max_rows:
            raise RowCountLimitExceededError(
                f"Dataset row count ({len(df)}) exceeds maximum limit of {self.max_rows}"
            )

        if len(df.columns) > self.max_cols:
            raise ColumnCountLimitExceededError(
                f"Dataset column count ({len(df.columns)}) exceeds maximum limit of {self.max_cols}"
            )

        original_columns = [str(c) for c in df.columns]
        normalized_columns = self._normalize_column_names(original_columns)
        df.columns = normalized_columns

        column_schemas = self._build_column_schemas(
            df, original_columns, normalized_columns
        )

        return IngestionResult(
            dataframe=df,
            file_name=file_name,
            file_size_bytes=file_size,
            mime_type="text/csv"
            if not file_name.endswith(".tsv")
            else "text/tab-separated-values",
            row_count=len(df),
            col_count=len(df.columns),
            encoding=encoding,
            delimiter=delimiter,
            sheets=[],
            selected_sheet=None,
            original_columns=original_columns,
            normalized_columns=normalized_columns,
            column_schemas=column_schemas,
            import_warnings=warnings,
        )

    # -------------------------------------------------------------------------
    # XLSX Parsing (Secure & Deterministic)
    # -------------------------------------------------------------------------

    def _ingest_xlsx(
        self, path: Path, file_name: str, file_size: int, sheet_name: str | None = None
    ) -> IngestionResult:
        with path.open("rb") as f:
            return self._ingest_xlsx_stream(
                f, file_name, file_size, sheet_name=sheet_name
            )

    def _ingest_xlsx_stream(
        self,
        stream: BinaryIO | io.BytesIO,
        file_name: str,
        file_size: int,
        sheet_name: str | None = None,
    ) -> IngestionResult:
        warnings: list[str] = []

        # Guard against zip bomb attacks and verify zip structure
        try:
            if hasattr(stream, "seek"):
                stream.seek(0)
            if not zipfile.is_zipfile(stream):
                raise FileParsingError(
                    f"File '{file_name}' is not a valid zip/xlsx archive"
                )
            if hasattr(stream, "seek"):
                stream.seek(0)
            with zipfile.ZipFile(stream) as zf:
                total_uncompressed = sum(info.file_size for info in zf.infolist())
                max_uncompressed = self.max_file_size_bytes * 10
                if total_uncompressed > max_uncompressed:
                    raise FileParsingError(
                        f"Excel archive exceeds maximum safe uncompressed size limit "
                        f"({total_uncompressed} > {max_uncompressed} bytes)"
                    )
            if hasattr(stream, "seek"):
                stream.seek(0)
        except zipfile.BadZipFile as exc:
            raise FileParsingError(
                f"Corrupted or invalid Excel zip container: {exc}"
            ) from exc

        try:
            # openpyxl with data_only=True evaluates formulas to cached values and ignores VBA macros
            wb = openpyxl.load_workbook(stream, read_only=True, data_only=True)
            available_sheets = wb.sheetnames
        except Exception as exc:
            raise FileParsingError(
                f"Invalid or corrupted Excel workbook: {exc}"
            ) from exc

        if not available_sheets:
            raise EmptyFileError(f"Excel workbook contains no sheets: {file_name}")

        selected_sheet = sheet_name
        if not selected_sheet:
            selected_sheet = available_sheets[0]
            if len(available_sheets) > 1:
                warnings.append(
                    f"Workbook has multiple sheets: {available_sheets}. Defaulted to first sheet: '{selected_sheet}'."
                )
        elif selected_sheet not in available_sheets:
            raise IngestionError(
                f"Requested sheet '{selected_sheet}' not found. Available sheets: {available_sheets}"
            )

        # Read sheet content into memory
        ws = wb[selected_sheet]
        rows_iter = ws.iter_rows(values_only=True)

        try:
            first_row = next(rows_iter, None)
        except Exception as exc:
            raise FileParsingError(
                f"Failed reading sheet '{selected_sheet}': {exc}"
            ) from exc

        if first_row is None:
            raise EmptyFileError(f"Sheet '{selected_sheet}' is completely empty")

        # First row is treated as header
        raw_headers = [str(cell) if cell is not None else "" for cell in first_row]

        if len(raw_headers) > self.max_cols:
            wb.close()
            raise ColumnCountLimitExceededError(
                f"Excel sheet '{selected_sheet}' exceeds column limit of {self.max_cols}"
            )

        # Read data rows bounded by max_rows
        data_rows: list[list[Any]] = []
        for i, row in enumerate(rows_iter):
            if i >= self.max_rows + 1:
                break
            # Trim or pad row to match header length
            row_data = list(row[: len(raw_headers)])
            if len(row_data) < len(raw_headers):
                row_data.extend([None] * (len(raw_headers) - len(row_data)))
            data_rows.append(row_data)

        wb.close()

        if len(data_rows) > self.max_rows:
            raise RowCountLimitExceededError(
                f"Excel sheet '{selected_sheet}' exceeds row limit of {self.max_rows}"
            )

        normalized_headers = self._normalize_column_names(raw_headers)
        df = pd.DataFrame(data_rows, columns=normalized_headers)

        if df.empty and len(df.columns) == 0:
            raise EmptyFileError(
                f"Excel sheet '{selected_sheet}' contains no tabular records"
            )

        # Strip rows that are entirely null
        df = df.dropna(how="all").reset_index(drop=True)

        column_schemas = self._build_column_schemas(df, raw_headers, normalized_headers)

        return IngestionResult(
            dataframe=df,
            file_name=file_name,
            file_size_bytes=file_size,
            mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            row_count=len(df),
            col_count=len(df.columns),
            encoding=None,
            delimiter=None,
            sheets=available_sheets,
            selected_sheet=selected_sheet,
            original_columns=raw_headers,
            normalized_columns=normalized_headers,
            column_schemas=column_schemas,
            import_warnings=warnings,
        )

    # -------------------------------------------------------------------------
    # Normalization & Type Helpers
    # -------------------------------------------------------------------------

    def _normalize_column_names(self, raw_columns: list[str]) -> list[str]:
        """Normalize column names according to Inferaxis schema policy.

        Rules:
        1. Strip leading and trailing whitespace.
        2. Replace newlines, tabs, and control characters with a single space.
        3. Replace empty strings or whitespace-only names with 'unnamed_N'.
        4. Deduplicate identically named columns by appending '_1', '_2', etc.
        """
        seen: dict[str, int] = {}
        normalized: list[str] = []

        for i, raw in enumerate(raw_columns):
            # Clean control characters
            cleaned = re.sub(r"[\r\n\t]+", " ", str(raw)).strip()
            if not cleaned or re.match(r"^unnamed(:\s*\d+)?$", cleaned, re.IGNORECASE):
                cleaned = f"unnamed_{i + 1}"
            elif re.search(r"\.\d+$", cleaned):
                cleaned = re.sub(r"\.\d+$", "", cleaned)

            # Deduplicate
            lower_key = cleaned.lower()
            if lower_key in seen:
                seen[lower_key] += 1
                unique_name = f"{cleaned}_{seen[lower_key]}"
            else:
                seen[lower_key] = 0
                unique_name = cleaned

            normalized.append(unique_name)

        return normalized

    def _build_column_schemas(
        self,
        df: pd.DataFrame,
        original_cols: list[str],
        normalized_cols: list[str],
    ) -> list[ColumnSchema]:
        """Build schema definitions for all columns with conservative type classification."""
        schemas: list[ColumnSchema] = []

        for orig_name, norm_name in zip(original_cols, normalized_cols):
            series = df[norm_name]
            dtype_str = str(series.dtype)
            inferred = self._classify_inferred_type(series)
            has_nulls = bool(series.isna().any())

            schemas.append(
                ColumnSchema(
                    name=norm_name,
                    original_name=orig_name,
                    dtype=dtype_str,
                    inferred_type=inferred,
                    nullable=has_nulls,
                )
            )

        return schemas

    @staticmethod
    def _classify_inferred_type(series: pd.Series) -> str:
        """Conservatively infer broad semantic type from pandas Series."""
        if pd.api.types.is_numeric_dtype(series):
            if pd.api.types.is_integer_dtype(series):
                return "integer"
            return "float"
        elif pd.api.types.is_datetime64_any_dtype(series):
            return "datetime"
        elif pd.api.types.is_bool_dtype(series):
            return "boolean"
        else:
            return "string"
