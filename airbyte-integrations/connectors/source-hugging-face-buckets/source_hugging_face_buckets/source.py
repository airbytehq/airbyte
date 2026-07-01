#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import json
import logging
import time
import traceback
from typing import Any, Iterable, Iterator, Mapping, MutableMapping

import pandas as pd
import pyarrow.parquet as pq
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
                        "examples": [
                            "hf://buckets/lhoestq/b/",
                            "hf://buckets/organization/dataset_name/"
                        ],
                        "order": 0
                    },
                    "file_format": {
                        "title": "File Format",
                        "type": "string",
                        "description": "The format of files in the bucket. Used for schema inference.",
                        "enum": ["parquet", "csv", "json", "jsonl"],
                        "default": "parquet",
                        "order": 1
                    },
                    "reader_options": {
                        "title": "Reader Options",
                        "type": "string",
                        "description": "JSON string with reader options (e.g., separators, encoding).",
                        "examples": ['{"sep": ",", "encoding": "utf-8"}'],
                        "order": 2
                    },
                    "token": {
                        "title": "Hugging Face Token",
                        "type": "string",
                        "description": "Your Hugging Face token for authentication. Required for private buckets.",
                        "airbyte_secret": True,
                        "order": 3
                    }
                }
            },
            documentationUrl="https://docs.airbyte.com/integrations/sources/hugging-face-buckets",
            supports_incremental=False,
            supported_destination_sync_modes=["overwrite"]
        )

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
            return AirbyteConnectionStatus(
                status=AirbyteStatus.FAILED,
                message=f"Connection check failed: {str(e)}"
            )


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
            reader_options_raw = config.get("reader_options", "{}")
            
            # Parse reader options
            try:
                reader_options = json.loads(reader_options_raw) if reader_options_raw else {}
            except json.JSONDecodeError:
                reader_options = {}
            
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
            
            # List all files in the bucket
            files = fs.ls(bucket_path)
            
            # Process only configured streams
            for file_info in files:
                if file_info["type"] != "file":
                    continue
                    
                file_name = file_info["name"].split("/")[-1]
                file_path = file_info['name']
                
                # Skip hidden files
                if file_name.startswith("."):
                    continue
                
                # Use the same stream name as discover
                stream_name = f"{file_name}_{file_path.replace('/', '_').replace('.', '_')}"
                
                if stream_name not in configured_streams:
                    continue
                
                airbyte_stream = configured_streams[stream_name]
                
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
                                emitted_at=int(time.time() * 1000)  # Use logger creation time
                            )
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
                        message=f"Failed to read {stream_name}: {str(e)}",
                        internal_message=str(e),
                        failure_type=FailureType.read_error
                    )
                
                logger.info(f"Read {record_count} records from {stream_name}")
                logger.info(f"Marking stream {stream_name} as COMPLETE")
                yield stream_status_as_airbyte_message(airbyte_stream, AirbyteStreamStatus.COMPLETE)
                
        except Exception as e:
            logger.error(f"Read operation failed: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def _read_file(self, file_path: str, file_format: str, reader_options: dict, logger: logging.Logger, fs: HfFileSystem) -> Iterable[Mapping[str, Any]]:
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
                    record = row.to_dict()
                    # Handle NaN values
                    for k, v in record.items():
                        if pd.isna(v):
                            record[k] = None
                    yield record
                        
        except Exception as e:
            logger.error(f"Failed to read hf://{file_path}: {str(e)}")
            raise

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
            
            # List all files in the bucket
            files = fs.ls(bucket_path, detail=True)
            
            streams = []
            for file_info in files:
                if file_info.get("type") == "file":
                    file_path = file_info.get("name", "")
                    # Extract filename without path
                    file_name = file_path.split("/")[-1]
                    stream_name = f"{file_name}_{file_path.replace('/', '_').replace('.', '_')}"
                    
                    # Infer schema from file
                    try:
                        schema = self._infer_schema(file_name, file_format, logger, fs)
                        streams.append(AirbyteStream(
                            name=stream_name,
                            json_schema=schema,
                            supported_sync_modes=[SyncMode.full_refresh]
                        ))
                    except Exception as e:
                        logger.warning(f"Failed to infer schema for {file_name}: {str(e)}")
                        # Create a basic schema
                        streams.append(AirbyteStream(
                            name=stream_name,
                            json_schema={
                                "$schema": "http://json-schema.org/draft-07/schema#",
                                "type": "object",
                                "properties": {
                                    "_airbyte_data": {"type": ["string", "null"]}
                                }
                            },
                            supported_sync_modes=[SyncMode.full_refresh]
                        ))
            
            return AirbyteCatalog(streams=streams)
            
        except Exception as e:
            logger.error(f"Failed to discover streams: {str(e)}")
            raise

    def _infer_schema(self, file_path: str, file_format: str, logger: logging.Logger, fs: HfFileSystem) -> dict:
        """Infer schema from a file."""
        try:
            if file_format == "parquet":
                with fs.open(file_path, "rb") as f:
                    schema = pq.read_schema(f)
                    properties = {}
                    for col in schema:
                        dtype = str(schema.field(col).type)
                        if "int" in dtype:
                            properties[col] = {"type": ["integer", "null"]}
                        elif "float" in dtype or "double" in dtype:
                            properties[col] = {"type": ["number", "null"]}
                        elif "bool" in dtype:
                            properties[col] = {"type": ["boolean", "null"]}
                        else:
                            properties[col] = {"type": ["string", "null"]}
                        
                    return {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "type": "object",
                        "properties": properties
                    }
                    
            elif file_format == "csv":
                with fs.open(file_path, "rb") as f:
                    df = pd.read_csv(f, nrows=10)
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
                            
                    return {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "type": "object",
                        "properties": properties
                    }
                    
            else:
                # For JSON/JSONL, return a generic schema
                return {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": {
                        "_airbyte_data": {"type": ["string", "null"]}
                    }
                }
                
        except Exception as e:
            logger.warning(f"Failed to infer schema for {file_path}: {str(e)}")
            return {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "_airbyte_data": {"type": ["string", "null"]}
                }
            }