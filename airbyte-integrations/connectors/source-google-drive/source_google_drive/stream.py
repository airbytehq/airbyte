#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

from typing import Dict, Iterable, Optional, Set

from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.stream import DefaultFileBasedStream


class GoogleDriveFileBasedStream(DefaultFileBasedStream):
    """Stream implementation that filters files whose type does not align with the configured format."""

    _FILETYPE_EXTENSIONS: Dict[str, Set[str]] = {
        "csv": {".csv"},
        "jsonl": {".jsonl", ".ndjson"},
        "parquet": {".parquet"},
        "avro": {".avro"},
        "excel": {".xls", ".xlsx", ".xlsm", ".xlsb", ".ods"},
        "unstructured": {".pdf", ".docx", ".pptx", ".md", ".txt"},
    }

    _FILETYPE_MIME_TYPES: Dict[str, Set[str]] = {
        "csv": {"text/csv"},
        "jsonl": {"application/json", "application/x-ndjson", "application/jsonl"},
        "parquet": {"application/x-parquet", "application/vnd.apache.parquet"},
        "avro": {"application/avro"},
        "excel": {
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel",
            "application/vnd.ms-excel.sheet.macroenabled.12",
            "application/vnd.ms-excel.sheet.binary.macroenabled.12",
            "application/vnd.oasis.opendocument.spreadsheet",
        },
        "unstructured": {
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "text/markdown",
            "text/plain",
        },
    }

    _FILETYPE_ORIGINAL_MIME_TYPES: Dict[str, Set[str]] = {
        "excel": {"application/vnd.google-apps.spreadsheet"},
        "unstructured": {
            "application/vnd.google-apps.document",
            "application/vnd.google-apps.presentation",
            "application/vnd.google-apps.drawing",
        },
    }

    def get_files(self) -> Iterable[RemoteFile]:  # noqa: D401
        for remote_file in self.stream_reader.get_matching_files(
            self.config.globs or [],
            self.config.legacy_prefix,
            self.logger,
        ):
            if self._file_matches_configured_type(remote_file):
                yield remote_file
            else:
                configured_filetype = self._configured_filetype() or "unknown"
                self.logger.info(
                    "Skipping file %s because it does not match the configured file type '%s' (%s). Modify the stream's glob pattern, adjust the file type, or move the file outside the matched path and try again.",
                    remote_file.uri,
                    configured_filetype,
                    self._describe_file(remote_file),
                )

    def _file_matches_configured_type(self, remote_file: RemoteFile) -> bool:
        configured_filetype = self._configured_filetype()
        if not configured_filetype:
            return True

        if configured_filetype not in self._FILETYPE_EXTENSIONS:
            # Unknown configuration, do not filter
            return True

        extension = self._get_extension(remote_file.uri)
        mime_candidates = {value.lower() for value in [remote_file.mime_type, getattr(remote_file, "original_mime_type", None)] if value}

        if extension and extension in self._FILETYPE_EXTENSIONS[configured_filetype]:
            return True

        if mime_candidates.intersection(self._FILETYPE_MIME_TYPES.get(configured_filetype, set())):
            return True

        if mime_candidates.intersection(self._FILETYPE_ORIGINAL_MIME_TYPES.get(configured_filetype, set())):
            return True

        return False

    def _configured_filetype(self) -> Optional[str]:
        filetype = getattr(self.config.format, "filetype", None)
        if isinstance(filetype, str):
            return filetype.lower()
        return None

    @staticmethod
    def _get_extension(uri: str) -> Optional[str]:
        filename = uri.rsplit("/", 1)[-1]
        if "." not in filename:
            return None
        extension = "." + filename.lower().split(".")[-1]
        return extension

    @staticmethod
    def _describe_file(remote_file: RemoteFile) -> str:
        parts = []
        extension = GoogleDriveFileBasedStream._get_extension(remote_file.uri)
        if extension:
            parts.append(f"extension {extension}")
        original_mime = getattr(remote_file, "original_mime_type", None)
        if original_mime:
            parts.append(f"original mime type {original_mime}")
        mime_type = remote_file.mime_type
        if mime_type and mime_type != original_mime:
            parts.append(f"mime type {mime_type}")
        return ", ".join(parts) if parts else "type unknown"
