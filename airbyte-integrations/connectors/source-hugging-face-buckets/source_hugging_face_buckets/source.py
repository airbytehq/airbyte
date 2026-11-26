#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import base64
import json
import logging
import math
import re
import time
import traceback
from datetime import date, datetime, timedelta
from datetime import time as time_type
from decimal import Decimal
from typing import Any, Iterable, Iterator, Mapping, MutableMapping

import pandas as pd
import pyarrow.parquet as pq
import pyarrow.types as pa_types
from huggingface_hub import HfFileSystem

from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    AirbyteStreamStatus,
    ConfiguredAirbyteCatalog,
    ConnectorSpecification,
    DestinationSyncMode,
    FailureType,
    SyncMode,
    Type,
)
from airbyte_cdk.models import (
    Status as AirbyteStatus,
)
from airbyte_cdk.sources import Source
from airbyte_cdk.utils import AirbyteTracedException
from airbyte_cdk.utils.stream_status_utils import as_airbyte_message as stream_status_as_airbyte_message


class SourceHuggingFaceBuckets(Source):
    """A source connector that reads data from Hugging Face Buckets.

    This connector reads files from Hugging Face Buckets (file storage on Hugging Face Hub)
    using the huggingface_hub library's HfFileSystem.

    Supports the following file formats:
    - Parquet (.parquet)
    - JSON/JSONL (.json, .jsonl)
    - CSV (.csv)
    - Text files (.txt)

    URL Format: hf://buckets/{username}/{bucket}/{path}/{filename}
    """

    def spec(self, logger: logging.Logger) -> ConnectorSpecification:
        """Returns the JSON schema for the connector configuration."""
        return ConnectorSpecification(
            connectionSpecification={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "title": "Source Hugging Face Buckets",
                "type": "object",
                "required": ["bucket_path"],
                "additionalProperties": False,
                "properties": {
                    "bucket_path": {
                        "title": "Bucket Path",
                        "type": "string",
                        "description": "The path to the Hugging Face Bucket. Format: hf://buckets/{username}/{bucket}/{path}/",
                        "examples": ["hf://buckets/lhoestq/b/", "hf://buckets/organization/dataset_name/"],
                        "order": 0,
                    },
                    "file_format": {
                        "title": "File Format",
                        "type": "string",
                        "description": "The format of files in the bucket. Used for schema inference.",
                        "enum": ["parquet", "csv", "json", "jsonl"],
                        "default": "parquet",
                        "order": 1,
                    },
                    "reader_options": {
                        "title": "Reader Options",
                        "type": "string",
                        "description": "JSON string with reader options (e.g., separators, encoding).",
                        "examples": ['{"sep": ",", "encoding": "utf-8"}'],
                        "order": 2,
                    },
                    "token": {
                        "title": "Hugging Face Token",
                        "type": "string",
                        "description": "Your Hugging Face token for authentication. Required for private buckets.",
                        "airbyte_secret": True,
                        "order": 3,
                    },
                },
            },
            documentationUrl="https://docs.airbyte.com/integrations/sources/hugging-face-buckets",
            supportsIncremental=False,
            supported_destination_sync_modes=[DestinationSyncMode.append, DestinationSyncMode.overwrite],
        )

    @staticmethod
    def _parse_reader_options(config: Mapping[str, Any]) -> dict:
        """Read the extra reader options, which the UI holds as a JSON string."""
        raw = config.get("reader_options") or "{}"
        try:
            options = json.loads(raw)
        except json.JSONDecodeError:
            logging.warning(f"Ignoring the reader options: {raw!r} is not valid JSON")
            return {}
        return options if isinstance(options, dict) else {}

    @staticmethod
    def _list_files(fs: HfFileSystem, bucket_path: str) -> list[str]:
        """List the files of a bucket path, sorted and without the hidden ones."""
        entries = fs.ls(bucket_path, detail=True)
        files = [entry["name"] for entry in entries if entry.get("type") == "file" and not entry["name"].rsplit("/", 1)[-1].startswith(".")]
        return sorted(files)

    def _files_by_stream_name(self, fs: HfFileSystem, bucket_path: str) -> dict:
        """Map the stream name of every file of the bucket to its path.

        A stream is named after its file, relative to the configured path, because that is the part
        of the path the user reads as the name of a file. Files are listed sorted, and discover names
        them the same way, so a stream keeps its name from one sync to the next.
        """
        prefix = f"{bucket_path.rstrip('/')}/"
        used: dict = {}
        files_by_stream: dict = {}
        for file_path in self._list_files(fs, bucket_path):
            relative = file_path[len(prefix) :] if file_path.startswith(prefix) else file_path.rsplit("/", 1)[-1]
            name = re.sub(r"[^a-zA-Z0-9_-]+", "_", relative)
            used[name] = used.get(name, 0) + 1
            if used[name] > 1:  # two file names can sanitize to the same stream name
                name = f"{name}__{used[name]}"
            files_by_stream[name] = file_path
        return files_by_stream

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """Test the connection by checking if we can list files in the bucket."""
        try:
            bucket_path = config.get("bucket_path", "")
            token = config.get("token", None)

            # Ensure bucket_path has no hf:// scheme
            if bucket_path.startswith("hf://"):
                bucket_path = bucket_path[5:]

            # Remove trailing slash for listing
            if bucket_path.endswith("/"):
                bucket_path = bucket_path[:-1]

            fs = HfFileSystem(token=token)

            # Try to list the bucket contents
            fs.ls(bucket_path)

            return AirbyteConnectionStatus(status=AirbyteStatus.SUCCEEDED)

        except Exception as e:
            return AirbyteConnectionStatus(status=AirbyteStatus.FAILED, message=f"Connection check failed: {str(e)}")

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: MutableMapping[str, Any] = None,
    ) -> Iterator[AirbyteMessage]:
        """Read data from the bucket files."""
        try:
            bucket_path = config.get("bucket_path", "")
            file_format = config.get("file_format", "parquet")
            token = config.get("token", None)
            reader_options = self._parse_reader_options(config)

            # Get the configured streams
            if not catalog or not catalog.streams:
                logger.warning("No streams configured in catalog")
                return

            # Extract stream names from ConfiguredAirbyteCatalog
            # Each element is a ConfiguredAirbyteStream with a 'stream' attribute
            configured_streams = {}
            for configured_stream in catalog.streams:
                stream_name = configured_stream.stream.name
                configured_streams[stream_name] = configured_stream.stream

            # Ensure bucket_path has no hf:// scheme
            if bucket_path.startswith("hf://"):
                bucket_path = bucket_path[5:]

            # Remove trailing slash for listing
            if bucket_path.endswith("/"):
                bucket_path = bucket_path[:-1]

            fs = HfFileSystem(token=token)

            # The stream names are the ones discovery advertised, so the bucket is listed the same way
            files_by_stream = self._files_by_stream_name(fs, bucket_path)

            for stream_name, airbyte_stream in configured_streams.items():
                file_path = files_by_stream.get(stream_name)
                if file_path is None:
                    logger.warning(f"Stream {stream_name} has no file in hf://{bucket_path}: skipping")
                    continue

                logger.info(f"Reading stream: {stream_name} from hf://{file_path}")

                yield stream_status_as_airbyte_message(airbyte_stream, AirbyteStreamStatus.STARTED)

                # Read the file and emit records
                record_count = 0
                try:
                    for record in self._read_file(file_path, file_format, reader_options, logger, fs):
                        yield AirbyteMessage(
                            type=Type.RECORD,
                            record=AirbyteRecordMessage(
                                stream=stream_name,
                                data=record,
                                emitted_at=int(time.time() * 1000),
                            ),
                        )
                        record_count += 1

                        if record_count == 1:
                            logger.info(f"Marking stream {stream_name} as RUNNING")
                            yield stream_status_as_airbyte_message(airbyte_stream, AirbyteStreamStatus.RUNNING)

                except Exception as e:
                    logger.error(f"Failed to read {stream_name}: {str(e)}")
                    logger.error(traceback.format_exc())
                    yield stream_status_as_airbyte_message(airbyte_stream, AirbyteStreamStatus.INCOMPLETE)
                    raise AirbyteTracedException(
                        message=f"Failed to read {stream_name}: {str(e)}", internal_message=str(e), failure_type=FailureType.transient_error
                    )

                logger.info(f"Read {record_count} records from {stream_name}")
                logger.info(f"Marking stream {stream_name} as COMPLETE")
                yield stream_status_as_airbyte_message(airbyte_stream, AirbyteStreamStatus.COMPLETE)

        except Exception as e:
            logger.error(f"Read operation failed: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def _read_file(
        self, file_path: str, file_format: str, reader_options: dict, logger: logging.Logger, fs: HfFileSystem
    ) -> Iterable[Mapping[str, Any]]:
        """Read records from a file."""
        try:
            with fs.open(file_path, "rb") as f:
                if file_format == "parquet":
                    df = pq.read_table(f).to_pandas()
                elif file_format == "csv":
                    df = pd.read_csv(f, **reader_options)
                elif file_format in ["json", "jsonl"]:
                    if file_format == "jsonl":
                        records = [json.loads(line) for line in f.readlines()]
                        for record in records:
                            if isinstance(record, dict):
                                yield record
                            else:
                                yield {"value": record}
                    else:
                        records = json.load(f)

                        if isinstance(records, list):
                            for record in records:
                                if isinstance(record, dict):
                                    yield record
                                else:
                                    yield {"value": record}
                        elif isinstance(records, dict):
                            yield records
                        else:
                            yield {"value": records}
                    return
                else:
                    # Default to reading as text
                    text = f.read().decode("utf-8", errors="ignore")
                    yield {"content": text}
                    return

                # Yield DataFrame records
                for _, row in df.iterrows():
                    yield self._to_json_safe(row.to_dict())

        except Exception as e:
            logger.error(f"Failed to read hf://{file_path}: {str(e)}")
            raise

    @staticmethod
    def _to_json_safe(value: Any) -> Any:
        """Convert a value read from a file into something the Airbyte protocol can serialize as JSON.

        Pandas hands back numpy scalars and NaN, which are not valid JSON values.
        """
        if value is None or isinstance(value, (bool, int, str)):
            return value
        if isinstance(value, float):
            return value if math.isfinite(value) else None
        if isinstance(value, (bytes, bytearray, memoryview)):
            return base64.b64encode(bytes(value)).decode("ascii")
        if isinstance(value, Mapping):
            return {str(key): SourceHuggingFaceBuckets._to_json_safe(item) for key, item in value.items()}
        if isinstance(value, (list, tuple, set)):
            return [SourceHuggingFaceBuckets._to_json_safe(item) for item in value]
        if isinstance(value, (datetime, date, time_type, timedelta)):
            return value.isoformat()
        if isinstance(value, Decimal):
            return float(value)
        if hasattr(value, "tolist"):  # numpy scalars and arrays
            return SourceHuggingFaceBuckets._to_json_safe(value.tolist())
        if pd.isna(value):
            return None
        return str(value)

    def discover(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteCatalog:
        """Discover available streams (files) in the bucket."""
        try:
            bucket_path = config.get("bucket_path", "")
            file_format = config.get("file_format", "parquet")
            token = config.get("token", None)

            # Ensure bucket_path has no hf:// scheme
            if bucket_path.startswith("hf://"):
                bucket_path = bucket_path[5:]

            # Remove trailing slash
            if bucket_path.endswith("/"):
                bucket_path = bucket_path[:-1]

            fs = HfFileSystem(token=token)
            reader_options = self._parse_reader_options(config)

            streams = [
                AirbyteStream(
                    name=stream_name,
                    json_schema=self._infer_schema(file_path, file_format, reader_options, logger, fs),
                    supported_sync_modes=[SyncMode.full_refresh],
                )
                for stream_name, file_path in self._files_by_stream_name(fs, bucket_path).items()
            ]

            return AirbyteCatalog(streams=streams)

        except Exception as e:
            logger.error(f"Failed to discover streams: {str(e)}")
            raise

    def _infer_schema(self, file_path: str, file_format: str, reader_options: dict, logger: logging.Logger, fs: HfFileSystem) -> dict:
        """Infer schema from a file."""
        try:
            if file_format == "parquet":
                with fs.open(file_path, "rb") as f:
                    properties = {field.name: self._json_schema_for(field.type) for field in pq.read_schema(f)}
                    return {"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "properties": properties}

            elif file_format == "csv":
                with fs.open(file_path, "rb") as f:
                    df = pd.read_csv(f, nrows=10, **reader_options)
                    properties = {}
                    for col in df.columns:
                        dtype = str(df[col].dtype)
                        if "int" in dtype:
                            properties[col] = {"type": ["integer", "null"]}
                        elif "float" in dtype:
                            properties[col] = {"type": ["number", "null"]}
                        elif "bool" in dtype:
                            properties[col] = {"type": ["boolean", "null"]}
                        else:
                            properties[col] = {"type": ["string", "null"]}

                    return {"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "properties": properties}

            else:
                # The shape of JSON and JSONL files is only known per record, so any object is accepted.
                return self._permissive_schema()

        except Exception as e:
            logger.warning(f"Failed to infer schema for {file_path}: {str(e)}")
            return self._permissive_schema()

    @staticmethod
    def _json_schema_for(arrow_type: Any) -> dict:
        """Map the type of a Parquet column to the type its records hold once serialized."""
        if pa_types.is_signed_integer(arrow_type) or pa_types.is_unsigned_integer(arrow_type):
            return {"type": ["integer", "null"]}
        if pa_types.is_floating(arrow_type) or pa_types.is_decimal(arrow_type):
            return {"type": ["number", "null"]}
        if pa_types.is_boolean(arrow_type):
            return {"type": ["boolean", "null"]}
        if pa_types.is_list(arrow_type) or pa_types.is_large_list(arrow_type) or pa_types.is_fixed_size_list(arrow_type):
            return {"type": ["array", "null"], "items": {}}
        if pa_types.is_struct(arrow_type) or pa_types.is_map(arrow_type):
            return {"type": ["object", "null"]}
        # Strings, dates, timestamps and binary data (base64 encoded) travel as strings.
        return {"type": ["string", "null"]}

    @staticmethod
    def _permissive_schema() -> dict:
        """Schema of a file whose columns are not known upfront: any object is accepted."""
        return {"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "additionalProperties": True}
