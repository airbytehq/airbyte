# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""Simple JSONL file writer for pgvector destination."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from airbyte_cdk.models import AirbyteRecordMessage


class JsonlWriter:
    """A simple JSONL file writer that writes records to JSONL files."""

    def __init__(
        self,
        cache_dir: Path,
        cleanup: bool = True,
    ) -> None:
        """Initialize the JSONL writer.
        
        Args:
            cache_dir: Directory to write JSONL files to
            cleanup: Whether to clean up files after processing (not implemented yet)
        """
        self.cache_dir = cache_dir
        self.cleanup = cleanup
        self._stream_files: dict[str, Path] = {}
        self._file_handles: dict[str, object] = {}
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def process_record_message(
        self,
        record_msg: AirbyteRecordMessage,
        stream_schema: dict,
    ) -> None:
        """Write a record to the appropriate JSONL file.
        
        Args:
            record_msg: The Airbyte record message to write
            stream_schema: The JSON schema for the stream (unused but kept for compatibility)
        """
        _ = stream_schema  # Unused but kept for API compatibility
        
        stream_name = record_msg.stream
        
        if stream_name not in self._stream_files:
            file_path = self.cache_dir / f"{stream_name}.jsonl"
            self._stream_files[stream_name] = file_path
            self._file_handles[stream_name] = open(file_path, "a")
        
        file_handle = self._file_handles[stream_name]
        json.dump(record_msg.data, file_handle)
        file_handle.write("\n")
        file_handle.flush()
    
    def flush_active_batches(self) -> None:
        """Flush all open file handles."""
        for file_handle in self._file_handles.values():
            file_handle.flush()
    
    def get_pending_batches(self, stream_name: str) -> list:
        """Get pending batches for a stream.
        
        For this simple implementation, we return a single batch handle
        containing the JSONL file for the stream.
        """
        from destination_pgvector.common.destinations.record_processor import BatchHandle
        
        if stream_name not in self._stream_files:
            return []
        
        if stream_name in self._file_handles:
            self._file_handles[stream_name].close()
            del self._file_handles[stream_name]
        
        file_path = self._stream_files[stream_name]
        
        batch = BatchHandle(
            batch_id=stream_name,
            files=[file_path],
        )
        
        return [batch]
    
    def cleanup_all(self) -> None:
        """Clean up all resources."""
        for file_handle in self._file_handles.values():
            file_handle.close()
        self._file_handles.clear()
        
        if self.cleanup:
            for file_path in self._stream_files.values():
                if file_path.exists():
                    file_path.unlink()
        
        self._stream_files.clear()
