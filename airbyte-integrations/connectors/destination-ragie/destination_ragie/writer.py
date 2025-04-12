import logging
import uuid
from typing import Any, Dict, List, Optional
import copy
import json
import hashlib

from airbyte_cdk.models import AirbyteRecordMessage, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode
from airbyte_cdk.utils.traced_exception import AirbyteTracedException, FailureType

from .client import RagieClient
from .config import RagieConfig

logger = logging.getLogger("airbyte.destination_ragie.writer")


class RagieWriter:
    METADATA_AIRBYTE_STREAM_FIELD = "airbyte_stream"
    METADATA_CONTENT_HASH_FIELD = "airbyte_content_hash"

    RESERVED_METADATA_KEYS = {
        "document_id", "document_type", "document_source", "document_name",
        "document_uploaded_at", "_source_created_at", "_source_updated_at",
        "data", "partition", "external_id", "name", "mode"
    }

    def __init__(
        self,
        client: RagieClient,
        config: RagieConfig,
        catalog: ConfiguredAirbyteCatalog,
    ):
        self.client = client
        self.config = config
        self.catalog = catalog
        self.streams: Dict[str, ConfiguredAirbyteStream] = {
            self._stream_tuple_to_id(s.stream.namespace, s.stream.name): s
            for s in catalog.streams
        }
        self.write_buffer: List[Dict[str, Any]] = []
        self.batch_size = config.batch_size
        self.static_metadata = self.config.metadata_static or {}

        # New: Hash cache for dedup
        self.seen_hashes: Dict[str, set] = {}

    def delete_streams_to_overwrite(self) -> None:
        """Finds streams with overwrite mode and deletes existing documents."""
        streams_to_overwrite = [
            stream_id
            for stream_id, stream_config in self.streams.items()
            if stream_config.destination_sync_mode == DestinationSyncMode.overwrite
        ]
        if not streams_to_overwrite:
            return

        logger.info(f"Overwrite mode detected for streams: {streams_to_overwrite}. Deleting existing data...")
        all_ids_to_delete = set() # Store internal Ragie IDs now
        for stream_name in streams_to_overwrite:
            logger.info(f"Finding existing documents for stream '{stream_name}' to delete...")
            # Filter by the stream metadata field
            filter_conditions = {self.METADATA_AIRBYTE_STREAM_FIELD: stream_name}
            try:
                # find_documents should return list of {'internal_id': ..., 'external_id': ...}
                stream_ids = self.client.find_ids_by_metadata(filter_conditions)
                # stream_internal_ids = {doc['id'] for doc in found_docs if 'id' in doc}
                if stream_ids:
                    logger.info(f"Found {len(stream_ids)} existing documents for stream '{stream_name}' to delete.")
                    all_ids_to_delete.update(stream_ids)
                else:
                    logger.info(f"No existing documents found for stream '{stream_name}'.")
            except Exception as e:
                logger.error(f"Failed to find documents for stream '{stream_name}' during overwrite: {e}", exc_info=True)
                raise AirbyteTracedException(
                    message=f"Failed to query existing documents for stream '{stream_name}' during overwrite. Cannot guarantee overwrite.",
                    internal_message=str(e),
                    failure_type=FailureType.system_error
                ) from e

        if all_ids_to_delete:
            logger.info(f"Attempting to delete {len(all_ids_to_delete)} total documents for overwrite streams by internal ID.")
            try:
                # Use the client method that deletes by *internal* ID
                self.client.delete_documents_by_id(list(all_ids_to_delete))
                logger.info(f"Successfully processed deletion requests for overwrite streams: {streams_to_overwrite}")
            except Exception as e:
                logger.error(f"Failed to delete documents for streams {streams_to_overwrite}: {e}", exc_info=True)
                raise AirbyteTracedException(
                    message=f"Failed to delete documents during overwrite for streams {streams_to_overwrite}",
                    internal_message=str(e),
                    failure_type=FailureType.system_error
                ) from e
        else:
             logger.info("No documents found to delete for overwrite streams.")

    def _get_value_from_path(self, data: Dict[str, Any], path: List[str]) -> Any:
        current = data
        for key in path:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current

    def _stream_tuple_to_id(self, namespace: Optional[str], name: str) -> str:
        return f"{namespace}_{name}" if namespace else name

    def _calculate_content_hash(self, content: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        hasher = hashlib.sha256()
        content_str = json.dumps(content, sort_keys=True, ensure_ascii=False)
        metadata_str = json.dumps(metadata, sort_keys=True, ensure_ascii=False)
        combined_str = content_str + "::" + metadata_str
        hasher.update(combined_str.encode('utf-8'))
        return hasher.hexdigest()

    def _preload_hashes_if_needed(self, stream_id: str) -> None:
        """Load all content hashes for the stream if not already cached."""
        if stream_id in self.seen_hashes:
            return

        logger.info(f"Preloading existing content hashes for stream '{stream_id}'...")
        try:
            filter_conditions = {self.METADATA_AIRBYTE_STREAM_FIELD: stream_id}
            existing_docs = self.client.find_docs_by_metadata(filter_conditions)

            hashes = {
                doc["metadata"].get(self.METADATA_CONTENT_HASH_FIELD)
                for doc in existing_docs
                if "metadata" in doc and self.METADATA_CONTENT_HASH_FIELD in doc["metadata"]
            }

            self.seen_hashes[stream_id] = hashes
            logger.info(f"Loaded {len(hashes)} content hashes for stream '{stream_id}'.")
        except Exception as e:
            logger.error(f"Failed to preload hashes for stream '{stream_id}': {e}", exc_info=True)
            raise AirbyteTracedException(
                message=f"Failed to preload hashes for stream '{stream_id}'.",
                internal_message=str(e),
                failure_type=FailureType.system_error
            ) from e

    def queue_write_operation(self, record: AirbyteRecordMessage) -> None:
        stream_id = self._stream_tuple_to_id(record.namespace, record.stream)
        stream_config = self.streams.get(stream_id)
        if not stream_config:
            logger.warning(f"Stream config not found for '{stream_id}', skipping record.")
            return

        record_data = record.data
        if not isinstance(record_data, dict):
            logger.warning(f"Invalid record data in stream '{stream_id}', skipping.")
            return

        # Extract content
        content_to_send = {}
        if self.config.content_fields:
            for field_path in self.config.content_fields:
                value = self._get_value_from_path(record_data, field_path.split('.'))
                if value is not None:
                    content_to_send[field_path.replace('.', '_')] = value
            if not content_to_send:
                logger.warning(f"No valid content fields found in record for stream '{stream_id}'.")
                return
        else:
            content_to_send = record_data

        # Determine doc name
        doc_name = None
        if self.config.document_name_field:
            value = self._get_value_from_path(record_data, self.config.document_name_field.split('.'))
            if value is not None:
                doc_name = str(value)
        if not doc_name:
            doc_name = f"ab_{stream_id}_{uuid.uuid4()}"

        # Extract metadata
        combined_metadata = copy.deepcopy(self.static_metadata)
        if self.config.metadata_fields:
            for field_path in self.config.metadata_fields:
                value = self._get_value_from_path(record_data, field_path.split('.'))
                if value is not None:
                    key = field_path.replace('.', '_')
                    if isinstance(value, (str, int, float, bool)):
                        combined_metadata[key] = value
                    elif isinstance(value, list) and all(isinstance(item, str) for item in value):
                        combined_metadata[key] = value
                    else:
                        try:
                            combined_metadata[key] = json.dumps(value)
                        except Exception:
                            logger.warning(f"Could not serialize metadata field '{key}'")

        combined_metadata[self.METADATA_AIRBYTE_STREAM_FIELD] = stream_id
        final_metadata = {
            k: v for k, v in combined_metadata.items()
            if k not in self.RESERVED_METADATA_KEYS
        }

        # Calculate content hash
        content_hash = self._calculate_content_hash(content_to_send, final_metadata)
        final_metadata[self.METADATA_CONTENT_HASH_FIELD] = content_hash

        # Dedup check
        if stream_config.destination_sync_mode == DestinationSyncMode.append_dedup:
            self._preload_hashes_if_needed(stream_id)
            if content_hash in self.seen_hashes[stream_id]:
                logger.info(f"Skipping duplicate record with hash {content_hash} in stream '{stream_id}'.")
                return
            else:
                self.seen_hashes[stream_id].add(content_hash)  # include hash immediately to prevent same-run duplicates

        # Build payload
        payload = {
            "name": doc_name,
            "data": content_to_send,
            "mode": self.config.processing_mode
        }
        if self.config.partition:
            payload["partition"] = self.config.partition
        if final_metadata:
            payload["metadata"] = final_metadata

        self.write_buffer.append(payload)
        logger.debug(f"Queued document '{doc_name}' (hash: {content_hash})")

        # Flush if needed
        if len(self.write_buffer) >= self.batch_size:
            self.flush()

    def flush(self) -> None:
        if not self.write_buffer:
            logger.debug("Flush called but buffer is empty.")
            return

        try:
            logger.info(f"Flushing {len(self.write_buffer)} documents.")
            self.client.index_documents(self.write_buffer)
            self.write_buffer.clear()
            logger.debug("Buffer cleared after flush.")
        except Exception as e:
            logger.error(f"Flush failed: {e}", exc_info=True)
            raise AirbyteTracedException(
                message="Failed to index documents in Ragie.",
                internal_message=str(e),
                failure_type=FailureType.system_error
            ) from e
