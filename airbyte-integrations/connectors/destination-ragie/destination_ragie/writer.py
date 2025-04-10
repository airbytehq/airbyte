import logging
import uuid
from typing import Any, Dict, List, Mapping, Optional, Set
import copy # For deep copying metadata
import json
import hashlib # For hashing

from airbyte_cdk.models import AirbyteRecordMessage, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode
from airbyte_cdk.utils.traced_exception import AirbyteTracedException, FailureType
# Assuming client.py and config.py are in the same directory or package
from .client import RagieClient
from .config import RagieConfig

logger = logging.getLogger("airbyte.destination_ragie.writer")


class RagieWriter:
    # !! CHANGED: Metadata key to avoid leading underscore !!
    METADATA_AIRBYTE_STREAM_FIELD = "airbyte_stream"
    METADATA_CONTENT_HASH_FIELD = "airbyte_content_hash" # Key for storing the hash

    # Define Ragie reserved keys - confirm these with Ragie docs
    # Adding our hash key here is debated - it's ours, but maybe avoid clashes? Let's assume it's okay for now.
    RESERVED_METADATA_KEYS = {
        "document_id", "document_type", "document_source", "document_name",
        "document_uploaded_at", "_source_created_at", "_source_updated_at",
        # Also avoid overwriting keys used in the payload structure if they were allowed in metadata
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
        # self.ids_to_delete: Set[str] = set() # REMOVED: No longer needed for hash-based dedup
        self.batch_size = config.batch_size
        self.static_metadata = self.config.metadata_static or {}


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
        all_internal_ids_to_delete = set() # Store internal Ragie IDs now
        for stream_name in streams_to_overwrite:
            logger.info(f"Finding existing documents for stream '{stream_name}' to delete...")
            # Filter by the stream metadata field
            filter_conditions = {self.METADATA_AIRBYTE_STREAM_FIELD: stream_name}
            try:
                # find_documents should return list of {'internal_id': ..., 'external_id': ...}
                stream_internal_ids = self.client.find_ids_by_metadata(filter_conditions)
                # stream_internal_ids = {doc['id'] for doc in found_docs if 'id' in doc}
                if stream_internal_ids:
                    logger.info(f"Found {len(stream_internal_ids)} existing documents for stream '{stream_name}' to delete.")
                    all_internal_ids_to_delete.update(stream_internal_ids)
                else:
                    logger.info(f"No existing documents found for stream '{stream_name}'.")
            except Exception as e:
                logger.error(f"Failed to find documents for stream '{stream_name}' during overwrite: {e}", exc_info=True)
                raise AirbyteTracedException(
                    message=f"Failed to query existing documents for stream '{stream_name}' during overwrite. Cannot guarantee overwrite.",
                    internal_message=str(e),
                    failure_type=FailureType.system_error
                ) from e

        if all_internal_ids_to_delete:
            logger.info(f"Attempting to delete {len(all_internal_ids_to_delete)} total documents for overwrite streams by internal ID.")
            try:
                # Use the client method that deletes by *internal* ID
                self.client.delete_documents_by_id(list(all_internal_ids_to_delete))
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
        """Helper to get a value from a nested dict using a path list."""
        current = data
        for key in path:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current

    def _stream_tuple_to_id(self, namespace: Optional[str], name: str) -> str:
        """Creates a unique string ID from namespace and stream name."""
        return f"{namespace}_{name}" if namespace else name

    def _calculate_content_hash(self, content: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """Calculates a SHA256 hash based on content and metadata dictionaries."""
        hasher = hashlib.sha256()
        # Ensure consistent serialization for hashing
        content_str = json.dumps(content, sort_keys=True, ensure_ascii=False)
        metadata_str = json.dumps(metadata, sort_keys=True, ensure_ascii=False)
        # Combine strings before hashing
        combined_str = content_str + "::" + metadata_str # Use a separator
        hasher.update(combined_str.encode('utf-8'))
        return hasher.hexdigest()

    def queue_write_operation(self, record: AirbyteRecordMessage) -> None:
        """Processes a record, calculates hash, checks for duplicates (if append_dedup), and adds to buffer."""
        stream_id = self._stream_tuple_to_id(record.namespace, record.stream)
        stream_config = self.streams.get(stream_id)
        if not stream_config:
            logger.warning(f"Stream configuration not found for '{stream_id}', skipping record.")
            return

        record_data = record.data
        if not isinstance(record_data, dict):
            logger.warning(f"Record data is not a dict for stream '{stream_id}', skipping.")
            return

        # --- 1. Extract Content ---
        content_to_send = {}
        if self.config.content_fields:
            for field_path in self.config.content_fields:
                 path_parts = field_path.split('.')
                 value = self._get_value_from_path(record_data, path_parts)
                 if value is not None:
                     content_to_send[field_path.replace('.', '_')] = value
            if not content_to_send:
                 logger.warning(f"Skipping record from stream '{stream_id}': None specified content_fields found.")
                 return
        else:
            content_to_send = record_data
            if not content_to_send:
                 logger.warning(f"Skipping record from stream '{stream_id}': Record data is empty.")
                 return

        # --- 2. Determine Document Name ---
        doc_name = None
        if self.config.document_name_field:
             path_parts = self.config.document_name_field.split('.')
             value = self._get_value_from_path(record_data, path_parts)
             if value is not None:
                 doc_name = str(value)
        if not doc_name:
             doc_name = f"ab_{stream_id}_{uuid.uuid4()}" # Changed default name prefix

        # --- 3. REMOVED External ID Determination ---

        # --- 4. Extract and Combine Metadata (BEFORE Hashing) ---
        combined_metadata = copy.deepcopy(self.static_metadata)
        if self.config.metadata_fields:
             for field_path in self.config.metadata_fields:
                 path_parts = field_path.split('.')
                 value = self._get_value_from_path(record_data, path_parts)
                 if value is not None:
                     key = field_path.replace('.', '_')
                     # Check types compatible with Ragie metadata filtering
                     if isinstance(value, (str, int, float, bool)):
                         combined_metadata[key] = value
                     elif isinstance(value, list) and all(isinstance(item, str) for item in value):
                         combined_metadata[key] = value
                     else:
                          logger.warning(f"Metadata field '{field_path}' (key '{key}') type {type(value)} might not be filterable in Ragie. Storing as JSON string.", exc_info=False)
                          # Store non-filterable types as strings if needed for context, but they won't work in $eq etc.
                          try:
                             combined_metadata[key] = json.dumps(value)
                          except TypeError:
                               logger.error(f"Could not JSON serialize metadata field '{key}'. Skipping.")

        combined_metadata[self.METADATA_AIRBYTE_STREAM_FIELD] = stream_id
        # Filter reserved keys *before* calculating hash based on final intended metadata
        final_metadata_for_payload = {k: v for k, v in combined_metadata.items() if k not in self.RESERVED_METADATA_KEYS}

        # --- 5. Calculate Content Hash ---
        content_hash = self._calculate_content_hash(content_to_send, final_metadata_for_payload)
        # Add the hash to the metadata that will be sent
        final_metadata_for_payload[self.METADATA_CONTENT_HASH_FIELD] = content_hash
        logger.debug(f"Calculated content hash for doc '{doc_name}': {content_hash}")

        # --- 6. Check for Duplicates if append_dedup ---
        if stream_config.destination_sync_mode == DestinationSyncMode.append_dedup:
            logger.debug(f"Append-dedup mode for stream '{stream_id}'. Checking for existing hash {content_hash}...")
            try:
                # Query Ragie for documents in this stream with the same hash
                filter_conditions = {
                    self.METADATA_AIRBYTE_STREAM_FIELD: stream_id,
                    # self.METADATA_CONTENT_HASH_FIELD: content_hash
                }
                
                existing_docs = self.client.find_ids_by_metadata(filter_conditions)
                # Check if any of the existing documents have the same hash

                if existing_docs:
                    # Found one or more documents with the same hash in this stream
                    logger.info(f"Skipping record for doc '{doc_name}' (stream '{stream_id}') - Duplicate hash '{content_hash}' already exists in Ragie.")
                    return # Skip adding this record to the buffer
                else:
                    logger.debug(f"No existing document found with hash '{content_hash}' for stream '{stream_id}'. Proceeding to queue.")

            except Exception as e:
                # Fail loudly if the check fails, as we can't guarantee deduplication
                logger.error(f"Failed to check for duplicate hash for doc '{doc_name}' (stream '{stream_id}'): {e}", exc_info=True)
                raise AirbyteTracedException(
                    message=f"Failed to check for duplicates via hash for stream '{stream_id}'. Cannot guarantee append-dedup behavior.",
                    internal_message=str(e),
                    failure_type=FailureType.system_error
                ) from e

        # --- 7. Construct Final Payload ---
        payload_data = {
            "name": doc_name,
            "data": content_to_send,
            "mode": self.config.processing_mode,
            # external_id is removed
        }
        if self.config.partition:
            payload_data["partition"] = self.config.partition
        if final_metadata_for_payload: # Ensure not empty
            payload_data["metadata"] = final_metadata_for_payload

        # --- 8. Add to Buffer ---
        self.write_buffer.append(payload_data)
        logger.debug(f"Added document '{doc_name}' (Hash: {content_hash}) to write buffer.")

        # --- 9. Flush if Buffer Full ---
        if len(self.write_buffer) >= self.batch_size:
            self.flush()


    


    def flush(self) -> None:
        """Flushes the buffer: indexes documents."""
        # Removed deletion step
        if not self.write_buffer:
            logger.debug("Flush called but write buffer is empty.")
            return

        buffer_size = len(self.write_buffer)
        logger.info(f"Flushing buffer: Indexing {buffer_size} documents.")

        # Index new versions from the buffer
        try:
            self.client.index_documents(self.write_buffer)
            logger.info(f"Successfully flushed and indexed {buffer_size} documents.")
        except Exception as e:
            logger.error(f"Failed to index batch of {buffer_size} documents during flush: {e}", exc_info=True)
            raise AirbyteTracedException(
                message=f"Failed to index batch of {buffer_size} documents.",
                internal_message=str(e),
                failure_type=FailureType.system_error
            ) from e

        # Clear buffer ONLY if indexing was successful
        self.write_buffer.clear()
        logger.debug("Write buffer cleared after successful flush.")