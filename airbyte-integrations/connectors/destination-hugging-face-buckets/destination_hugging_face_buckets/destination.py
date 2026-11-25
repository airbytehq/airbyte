#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import json
import logging
import uuid
from typing import Any, Iterable, Mapping

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from huggingface_hub import HfFileSystem

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    ConfiguredAirbyteCatalog,
    FailureType,
    Status,
    Type,
)
from airbyte_cdk.utils import AirbyteTracedException


class DestinationHuggingFaceBuckets(Destination):
    """A destination that writes data to Hugging Face Buckets using the hf:// protocol.

    This destination supports writing data to HF Buckets in Parquet format.
    It uses the huggingface_hub library's fsspec integration to read and write
    files to HF Buckets.

    Supported URL formats:
    - hf://buckets/{username}/{bucket}/{path}/{file.parquet}
    """

    def write(
        self,
        config: Mapping[str, Any],
        configured_catalog: ConfiguredAirbyteCatalog,
        input_messages: Iterable[AirbyteMessage],
    ) -> Iterable[AirbyteMessage]:
        """Write data to Hugging Face Buckets.

        Args:
            config: Configuration dictionary for the destination.
            configured_catalog: The catalog describing how to write data.
            input_messages: Stream of Airbyte messages containing records.

        Returns:
            Iterable of Airbyte messages, including state messages.
        """
        destination_path = config.get("destination_path", "")
        file_format = config.get("file_format", "parquet")
        token = config.get("token", None)

        # Ensure destination_path has no hf:// scheme
        if destination_path.startswith("hf://"):
            destination_path = destination_path[5:]
        if not destination_path.endswith("/"):
            destination_path += "/"

        # Track which streams/files we're writing to
        active_writers: dict = {}

        # Get the filesystem to write the files
        fs = HfFileSystem(token=token)

        try:
            for message in input_messages:
                if message.type == Type.STATE:
                    # Emit state messages as-is
                    yield message
                elif message.type == Type.RECORD:
                    if message.record is None:
                        continue
                    stream_name = message.record.stream or "default"
                    record_data = message.record.data or {}

                    # Build file path for this stream
                    if file_format == "parquet":
                        file_path = f"{destination_path}{stream_name}.parquet"
                    else:
                        file_path = f"{destination_path}{stream_name}.jsonl"

                    if file_path not in active_writers:
                        active_writers[file_path] = self._open_writer(file_path, file_format, fs)

                    writer = active_writers[file_path]
                    writer.write(record_data)

                elif message.type == Type.TRACE:
                    # Forward trace messages
                    yield message
                else:
                    # Ignore other message types
                    continue

        finally:
            # Close all open writers. A writer uploads on close, so a failing close means
            # the records of that file never landed and must fail the sync.
            failures: list[Exception] = []
            for file_path, writer in active_writers.items():
                try:
                    writer.close()
                except Exception as e:
                    logging.error(f"Failed to write {file_path}: {type(e).__name__}: {e}")
                    failures.append(e)
            if failures:
                raise AirbyteTracedException(
                    message=f"Failed to write {len(failures)} file(s) to the bucket: {failures[0]}",
                    internal_message=str(failures[0]),
                    failure_type=FailureType.transient_error,
                )

    def _open_writer(self, file_path: str, file_format: str, fs: HfFileSystem):
        """Open a file writer for the given path and format.

        Args:
            file_path: The full path to write to.
            file_format: The format ('parquet' or 'jsonl').
            fs: The filesystem to use.

        Returns:
            A writer object appropriate for the format.
        """
        if file_format == "parquet":
            return _ParquetWriter(file_path, fs)
        elif file_format == "jsonl":
            return _JsonlWriter(file_path, fs)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """Test the connection by checking if we can list and write to the bucket.

        Args:
            logger: Logger for the connector.
            config: The configuration dictionary.

        Returns:
            AirbyteConnectionStatus indicating success or failure.
        """
        try:
            destination_path = config.get("destination_path", "")
            token = config.get("token", None)

            if destination_path.startswith("hf://"):
                destination_path = destination_path[5:]
            if not destination_path.endswith("/"):
                destination_path += "/"

            # Get the filesystem to test connectivity
            fs = HfFileSystem(token=token)

            # Test write by creating a temporary file
            temp_file = f"{destination_path}_airbyte_check_{uuid.uuid4().hex}.parquet"

            test_table = pa.table({"check": [True]})

            with fs.open(temp_file, "wb") as f:
                pq.write_table(
                    test_table,
                    f,
                    write_page_index=True,
                    use_content_defined_chunking=True,
                )

            # Clean up
            fs.rm(temp_file)

            return AirbyteConnectionStatus(status=Status.SUCCEEDED)

        except Exception as e:
            return AirbyteConnectionStatus(
                status=Status.FAILED,
                message=f"Connection check failed: {e}",
            )


class _ParquetWriter:
    """Writer for Parquet files in HF Buckets."""

    def __init__(self, file_path: str, fs: HfFileSystem):
        self.file_path = file_path
        self.fs = fs
        self._buffers: list = []

    def write(self, record: dict):
        """Append a record to the file.

        Args:
            record: The record to append.
        """
        self._buffers.append(record)

    def close(self):
        """Flush and close the file."""
        if not self._buffers:
            return

        # Upload the whole file at once: buckets have no append mode.
        records, self._buffers = self._buffers, []
        with self.fs.open(self.file_path, "wb") as f:
            pq.write_table(
                self._table_from_records(records),
                f,
                write_page_index=True,
                use_content_defined_chunking=True,
            )

    @staticmethod
    def _table_from_records(records: list) -> pa.Table:
        """Build a Parquet table from records, keeping nested values as they are.

        PyArrow infers the schema from the records directly. The pandas round trip is only used
        as a fallback because it turns nested values into Python objects PyArrow rejects.
        """
        try:
            return pa.Table.from_pylist(records)
        except Exception as error:
            logging.warning(f"Could not infer a Parquet schema from the records, falling back on pandas: {error}")
            return pa.Table.from_pandas(pd.DataFrame(records))


class _JsonlWriter:
    """Writer for JSONL files in HF Buckets."""

    def __init__(self, file_path: str, fs: HfFileSystem):
        self.file_path = file_path
        self.fs = fs
        self._buffers: list = []

    def write(self, record: dict):
        """Append a record to the file.

        Args:
            record: The record to append.
        """
        self._buffers.append(record)

    def close(self):
        """Flush and close the file."""
        if self._buffers:
            # Write all buffered records to the file
            with self.fs.open(f"{self.file_path}", "wb") as f:
                for record in self._buffers:
                    f.write(json.dumps(record).encode("utf-8") + b"\n")

            self._buffers = []
