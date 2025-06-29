# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
import logging
import re
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Mapping, Optional, Union
from uuid import uuid4

from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.exceptions import BucketNotFoundException, CouchbaseException, DocumentExistsException, KeyspaceNotFoundException
from couchbase.options import ClusterOptions, ClusterTimeoutOptions, UpsertMultiOptions
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteErrorTraceMessage,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteTraceMessage,
    ConfiguredAirbyteCatalog,
    DestinationSyncMode,
    Status,
    TraceType,
    Type,
)


logger = logging.getLogger("airbyte")


class DestinationCouchbase(Destination):
    MAX_BATCH_SIZE = 1000
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the destination.
        """
        try:
            cluster = self._get_cluster(config)
            bucket_name = config["bucket"]
            scope_name = config.get("scope", "_default")

            # First verify bucket exists
            try:
                bucket = cluster.bucket(bucket_name)
                bucket.collections()
                logger.info(f"Successfully accessed bucket '{bucket_name}'")
            except BucketNotFoundException:
                return AirbyteConnectionStatus(
                    status=Status.FAILED, message=f"Bucket '{bucket_name}' does not exist. Please create the bucket first."
                )
            except CouchbaseException as e:
                return AirbyteConnectionStatus(status=Status.FAILED, message=f"Error accessing bucket '{bucket_name}': {str(e)}")

            # Create a temporary collection for testing
            temp_collection_name = f"airbyte_check_{uuid4().hex[:8]}"
            try:
                self._setup_collection(cluster, bucket_name, scope_name, temp_collection_name)
                logger.info(f"Successfully created test collection: {temp_collection_name}")

                # Test write operation
                test_doc = {"test": "data"}
                collection = bucket.scope(scope_name).collection(temp_collection_name)
                collection.upsert("test_doc", test_doc)

                # Test read operation
                collection.get("test_doc")

                # Cleanup
                bucket.collections().drop_collection(scope_name, temp_collection_name)
                logger.info(f"Successfully cleaned up test collection: {temp_collection_name}")

                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
            except Exception as e:
                return AirbyteConnectionStatus(status=Status.FAILED, message=f"Failed to verify write/read operations: {str(e)}")
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"Error establishing connection: {repr(e)}")

    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        """
        Reads the input stream of messages, config, and catalog to write data to Couchbase.
        """
        cluster = self._get_cluster(config)
        bucket_name = config["bucket"]
        scope_name = config.get("scope", "_default")
        batch_size = min(config.get("batch_size", 1000), self.MAX_BATCH_SIZE)

        logger.info(f"Starting sync with config: {{'bucket': '{bucket_name}', 'scope': '{scope_name}', 'batch_size': {batch_size}}}")

        # Initialize stream configurations
        stream_configs = {}
        for stream in configured_catalog.streams:
            stream_configs[stream.stream.name] = {
                "collection_name": self._sanitize_collection_name(stream.stream.name),
                "sync_mode": stream.destination_sync_mode,
                "schema": stream.stream.json_schema,
                "primary_key": stream.primary_key if stream.primary_key else [],
            }
            logger.info(
                f"Configured stream {stream.stream.name}: "
                f"sync_mode={stream.destination_sync_mode}, "
                f"primary_key={stream.primary_key if stream.primary_key else []}"
            )

        # Set up collections
        collections = {}
        for stream_name, stream_config in stream_configs.items():
            try:
                collection = self._setup_collection(cluster, bucket_name, scope_name, stream_config["collection_name"])

                # Handle overwrite sync mode
                if stream_config["sync_mode"] == DestinationSyncMode.overwrite:
                    logger.info(f"Clearing collection '{stream_config['collection_name']}' for overwrite sync mode")
                    self._clear_collection(cluster, bucket_name, scope_name, stream_config["collection_name"])

                collections[stream_name] = collection

            except Exception as e:
                error_msg = f"Failed to setup collection for stream {stream_name}: {str(e)}"
                logger.error(error_msg)
                yield self._emit_trace_message(error_msg, "config_error")
                raise

        # Initialize buffers and state tracking
        buffer: Dict[str, List[Dict]] = {}
        latest_state: Optional[AirbyteMessage] = None
        records_processed = 0

        try:
            for message in input_messages:
                if message.type == Type.STATE:
                    # Flush buffer before processing state message
                    self._flush_all_buffers(collections, buffer, stream_configs)
                    latest_state = message
                    yield message

                elif message.type == Type.RECORD:
                    stream_name = message.record.stream

                    try:
                        if stream_name not in stream_configs:
                            yield self._emit_trace_message(f"Skipping record from unknown stream: {stream_name}", "config_error")
                            continue

                        # Initialize buffer for stream if needed
                        if stream_name not in buffer:
                            buffer[stream_name] = []

                        # Validate and prepare record
                        document = self._prepare_record(message.record, stream_configs[stream_name])

                        if document:
                            buffer[stream_name].append(document)
                            records_processed += 1

                            # Flush if batch size reached
                            if len(buffer[stream_name]) >= batch_size:
                                self._flush_buffer(
                                    collections[stream_name], buffer[stream_name], stream_name, stream_configs[stream_name]["sync_mode"]
                                )
                                buffer[stream_name] = []

                    except Exception as e:
                        yield self._emit_trace_message(f"Error processing record for stream {stream_name}: {str(e)}", "system_error")
                        raise

            # Final flush of any remaining records
            if any(buffer.values()):
                self._flush_all_buffers(collections, buffer, stream_configs)

            logger.info(f"Sync completed successfully. Processed {records_processed} records.")

            # Return final state message if exists
            if latest_state:
                yield latest_state

        except Exception as e:
            error_msg = f"Fatal error during sync: {repr(e)}"
            logger.error(error_msg)
            yield self._emit_trace_message(error_msg, "system_error")
            raise

    def _get_cluster(self, config: Mapping[str, Any]) -> Cluster:
        """
        Creates and returns a configured Couchbase cluster instance.
        """
        auth = PasswordAuthenticator(config["username"], config["password"])
        timeout_options = ClusterTimeoutOptions(kv_timeout=timedelta(seconds=5), query_timeout=timedelta(seconds=10))
        cluster = Cluster(config["connection_string"], ClusterOptions(auth, timeout_options=timeout_options))
        cluster.wait_until_ready(timedelta(seconds=5))
        return cluster

    @staticmethod
    def _sanitize_collection_name(name: str) -> str:
        """
        Ensures collection name meets Couchbase requirements.
        """
        # Replace invalid characters with underscores
        sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", name)
        # Ensure name starts with a letter
        if not sanitized[0].isalpha():
            sanitized = "c_" + sanitized
        return sanitized

    def _setup_collection(self, cluster, bucket_name: str, scope_name: str, collection_name: str):
        """
        Sets up a collection with retries and proper error handling.
        """
        try:
            bucket = cluster.bucket(bucket_name)
            bucket_manager = bucket.collections()

            # Check if collection exists
            collections = bucket_manager.get_all_scopes()
            collection_exists = any(
                scope.name == scope_name and collection_name in [col.name for col in scope.collections] for scope in collections
            )

            if not collection_exists:
                logger.info(f"Creating collection '{collection_name}'...")
                bucket_manager.create_collection(scope_name, collection_name)
                logger.info(f"Collection '{collection_name}' created successfully.")

            collection = bucket.scope(scope_name).collection(collection_name)

            # Ensure primary index with retries
            for attempt in range(self.MAX_RETRIES):
                try:
                    query = f"CREATE PRIMARY INDEX IF NOT EXISTS ON `{bucket_name}`.`{scope_name}`.`{collection_name}`"
                    cluster.query(query).execute()
                    logger.info(f"Primary index created/verified for collection '{collection_name}'")
                    break
                except KeyspaceNotFoundException as e:
                    if attempt < self.MAX_RETRIES - 1:
                        delay = self.RETRY_DELAY * (2**attempt)  # Exponential backoff
                        logger.warning(f"Retrying index creation in {delay}s... ({str(e)})")
                        time.sleep(delay)
                    else:
                        raise

            return collection

        except Exception as e:
            raise RuntimeError(f"Error setting up collection: {str(e)}")

    def _clear_collection(self, cluster, bucket_name: str, scope_name: str, collection_name: str):
        """
        Clears all documents from a collection.
        """
        try:
            query = f"DELETE FROM `{bucket_name}`.`{scope_name}`.`{collection_name}`"
            cluster.query(query).execute()
            logger.info(f"Cleared all documents from collection '{collection_name}'")
        except Exception as e:
            logger.warning(f"Error clearing collection: {str(e)}")

    def _prepare_record(self, record: AirbyteRecordMessage, stream_config: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Prepares a record for insertion, including validation and ID generation.
        Handles nullable fields in schema validation.
        """
        try:
            # Make a deep copy of the schema to avoid modifying the original
            schema = json.loads(json.dumps(stream_config["schema"]))

            # Modify schema to allow null values for string fields
            if "properties" in schema:
                required_fields = set(schema.get("required", []))
                for prop_name, prop_schema in schema["properties"].items():
                    if isinstance(prop_schema, dict) and prop_schema.get("type") == "string" and prop_name not in required_fields:
                        # Allow null for optional string fields
                        prop_schema["type"] = ["string", "null"]

            # Clean null values in the data before validation
            cleaned_data = record.data.copy()
            for field_name, field_value in record.data.items():
                if field_name in schema.get("properties", {}) and field_value is None and field_name not in schema.get("required", []):
                    # Convert null to empty string for non-required string fields
                    if schema["properties"][field_name].get("type") in ["string", ["string", "null"]]:
                        cleaned_data[field_name] = ""

            # Validate record against modified schema
            try:
                validate(instance=cleaned_data, schema=schema)
            except ValidationError as e:
                logger.debug(f"Validation error details for {record.stream}:")
                logger.debug(f"Error: {str(e)}")
                logger.debug(f"Failed property: {e.path}")
                logger.debug(f"Schema: {e.schema}")
                logger.debug(f"Instance: {e.instance}")

                # If it's a required field, raise the error
                if isinstance(e.path, list) and len(e.path) > 0:
                    field_name = e.path[-1]
                    if field_name in schema.get("required", []):
                        raise
                else:
                    raise

                # For non-required fields, continue with the cleaned data
                logger.info(f"Proceeding with cleaned data for stream {record.stream}")

            # Generate document ID based on sync mode
            if stream_config["sync_mode"] == DestinationSyncMode.append_dedup and stream_config["primary_key"]:
                doc_id = self._generate_primary_key_id(cleaned_data, stream_config["primary_key"], record.stream)
            elif stream_config["sync_mode"] == DestinationSyncMode.append:
                doc_id = f"{record.stream}::{str(uuid4())}"
            else:  # DestinationSyncMode.overwrite
                doc_id = (
                    self._generate_primary_key_id(cleaned_data, stream_config["primary_key"], record.stream)
                    if stream_config["primary_key"]
                    else f"{record.stream}::{str(uuid4())}"
                )

            # Prepare document
            document = {
                "id": doc_id,
                "type": "airbyte_record",
                "stream": record.stream,
                "emitted_at": record.emitted_at,
                "data": cleaned_data,
                "_ab_sync_mode": str(stream_config["sync_mode"]),
            }

            if record.namespace:
                document["namespace"] = record.namespace

            return document
        except ValidationError as e:
            logger.warning(f"Record validation failed for stream {record.stream}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error preparing record for stream {record.stream}: {str(e)}")
            raise

    def _clean_null_values(self, data: Mapping[str, Any], schema: Mapping[str, Any]) -> Dict[str, Any]:
        """
        Recursively clean null values in the data according to the schema.
        """
        cleaned = {}
        for key, value in data.items():
            if value is None:
                if key in schema.get("required", []):
                    cleaned[key] = value  # Keep null for required fields
                else:
                    prop_schema = schema.get("properties", {}).get(key, {})
                    if prop_schema.get("type") == "string":
                        cleaned[key] = ""  # Convert null to empty string for optional string fields
                    else:
                        cleaned[key] = value  # Keep null for non-string fields
            elif isinstance(value, dict) and key in schema.get("properties", {}):
                # Recursively clean nested objects
                cleaned[key] = self._clean_null_values(value, schema["properties"][key])
            else:
                cleaned[key] = value
        return cleaned

    def _generate_primary_key_id(self, data: Mapping[str, Any], primary_key: List[List[str]], stream: str) -> str:
        """
        Generates a document ID from primary key fields.
        """
        try:
            key_values = []
            for key_path in primary_key:
                value = data
                for key in key_path:
                    if not isinstance(value, Mapping) or key not in value:
                        raise ValueError(f"Primary key path {key_path} not found in record")
                    value = value[key]
                if value is None:
                    raise ValueError(f"Primary key {key_path} contains null value")
                key_values.append(str(value))

            return f"{stream}::{':'.join(key_values)}"
        except Exception as e:
            raise ValueError(f"Error generating primary key ID: {str(e)}")

    def _flush_buffer(self, collection, buffer: List[Dict], stream_name: str, sync_mode: DestinationSyncMode, retry_count: int = 0):
        """
        Flushes a buffer of documents to Couchbase with retry logic.
        Handles different behaviors for append, append_dedup, and overwrite modes.
        """
        if not buffer:
            return

        try:
            batch = {doc["id"]: doc for doc in buffer}
            timeout = timedelta(seconds=len(batch) * 2.5)
            options = UpsertMultiOptions(timeout=timeout)

            result = collection.upsert_multi(batch, options)

            if not result.all_ok:
                failed_docs = []
                for doc_id, ex in result.exceptions.items():
                    if isinstance(ex, DocumentExistsException):
                        if sync_mode == DestinationSyncMode.append_dedup:
                            # For append_dedup, existing documents are expected
                            logger.info(f"Skipping duplicate document '{doc_id}' (append_dedup mode)")
                        elif sync_mode == DestinationSyncMode.append:
                            # For append, this shouldn't happen as we always use new UUIDs
                            logger.warning(f"Unexpected duplicate document '{doc_id}' in append mode")
                            failed_docs.append((doc_id, ex))
                        else:  # overwrite mode
                            # For overwrite, try individual upsert
                            try:
                                collection.upsert(doc_id, batch[doc_id])
                                logger.info(f"Overwrote existing document '{doc_id}'")
                            except Exception as e:
                                logger.error(f"Failed to overwrite document '{doc_id}': {str(e)}")
                                failed_docs.append((doc_id, e))
                    else:
                        failed_docs.append((doc_id, ex))

                if failed_docs:
                    failed_count = len(failed_docs)
                    if retry_count < self.MAX_RETRIES:
                        delay = self.RETRY_DELAY * (2**retry_count)
                        logger.warning(f"Retrying {failed_count} failed documents in {delay}s...")
                        time.sleep(delay)

                        # Retry failed documents
                        retry_buffer = [doc for doc in buffer if doc["id"] in dict(failed_docs)]
                        self._flush_buffer(collection, retry_buffer, stream_name, sync_mode, retry_count + 1)
                    else:
                        error_msg = f"Failed to write {failed_count} documents after {self.MAX_RETRIES} retries"
                        logger.error(error_msg)
                        raise RuntimeError(error_msg)

            logger.info(f"Successfully wrote {len(batch)} documents to stream {stream_name} ({sync_mode} mode)")

        except Exception as e:
            error_msg = f"Error flushing buffer for stream {stream_name}: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def _emit_trace_message(self, error_message: str, failure_type: str) -> AirbyteMessage:
        """
        Emits an AirbyteTraceMessage for error reporting.
        """
        return AirbyteMessage(
            type=Type.TRACE,
            trace=AirbyteTraceMessage(
                type=TraceType.ERROR,
                emitted_at=int(datetime.now().timestamp() * 1000),
                error=AirbyteErrorTraceMessage(message=error_message, failure_type=failure_type),
            ),
        )

    def _flush_all_buffers(self, collections: Dict[str, Any], buffer: Dict[str, list], stream_configs: Dict[str, dict]):
        """
        Flushes all buffers for all streams.
        """
        for stream_name, docs in buffer.items():
            if docs:
                try:
                    self._flush_buffer(collections[stream_name], docs, stream_name, stream_configs[stream_name]["sync_mode"])
                except Exception as e:
                    logger.error(f"Error flushing buffer for stream {stream_name}: {str(e)}")
                    raise
        buffer.clear()
