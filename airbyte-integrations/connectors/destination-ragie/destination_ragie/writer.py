# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import copy
import hashlib
import json
import logging
import mimetypes
import os
import uuid
from typing import Any, Dict, List, Optional, Set, Tuple

from airbyte_cdk.models import AirbyteRecordMessage, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode
from airbyte_cdk.utils.traced_exception import AirbyteTracedException, FailureType

from .client import RagieClient
from .config import RagieConfig


logger = logging.getLogger("airbyte.destination_ragie.writer")


class RagieWriter:
    METADATA_AIRBYTE_STREAM_FIELD = "airbyte_stream"
    METADATA_CONTENT_HASH_FIELD = "airbyte_content_hash"

    # Update RESERVED_METADATA_KEYS based on the provided API docs for POST /documents
    RESERVED_METADATA_KEYS = {
        "document_id",
        "document_type",
        "document_source",
        "document_name",
        "document_uploaded_at",
        "start_time",
        "end_time",  # Keys from docs
        # Include our internal keys
        METADATA_AIRBYTE_STREAM_FIELD,
        METADATA_CONTENT_HASH_FIELD,
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
            self._stream_tuple_to_id(s.stream.namespace, s.stream.name): s for s in catalog.streams
        }
        self.static_metadata = self.config.metadata_static_dict or {}
        self.seen_hashes: Dict[str, Set[str]] = {}
        self.hashes_preloaded: Set[str] = set()
        logger.info("RagieWriter initialized.")
        # Log relevant config settings (excluding secrets)
        logger.debug(f"Configured Partition: {self.config.partition}")
        logger.debug(f"Configured Metadata Fields: {self.config.metadata_fields}")
        logger.debug(f"Configured Doc Name Field: {self.config.document_name_field}")
        logger.debug(f"Configured External ID Field: {self.config.external_id_field}")
        logger.debug(f"Configured Processing Mode: {self.config.processing_mode}")
        logger.debug(f"Static Metadata Keys: {list(self.static_metadata.keys())}")

    def _stream_tuple_to_id(self, namespace: Optional[str], name: str) -> str:
        return f"{namespace}_{name}" if namespace else name

    # --- Overwrite Logic (delete_streams_to_overwrite) - No changes needed ---
    def delete_streams_to_overwrite(self) -> None:
        streams_to_overwrite = [(sid, sc) for sid, sc in self.streams.items() if sc.destination_sync_mode == DestinationSyncMode.overwrite]
        if not streams_to_overwrite:
            return
        stream_names = [sid for sid, _ in streams_to_overwrite]
        logger.info(f"OVERWRITE mode for streams: {stream_names}. Deleting existing data...")
        all_internal_ids_to_delete: Set[str] = set()
        for stream_id, stream_config in streams_to_overwrite:
            logger.info(f"Finding existing documents for stream '{stream_id}'...")
            filter_conditions = {self.METADATA_AIRBYTE_STREAM_FIELD: stream_id}
            try:
                internal_ids = self.client.find_ids_by_metadata(filter_conditions)
                if internal_ids:
                    logger.info(f"Found {len(internal_ids)} document IDs for stream '{stream_id}'.")
                    all_internal_ids_to_delete.update(internal_ids)
                else:
                    logger.info(f"No existing documents found for stream '{stream_id}'.")
            except Exception as e:
                logger.error(f"Failed to find documents for overwrite stream '{stream_id}': {e}", exc_info=True)
                raise AirbyteTracedException(
                    message=f"Failed to query existing documents for overwrite stream '{stream_id}'.",
                    internal_message=str(e),
                    failure_type=FailureType.system_error,
                ) from e
        if all_internal_ids_to_delete:
            logger.info(f"Attempting deletion of {len(all_internal_ids_to_delete)} documents for streams: {stream_names}")
            try:
                self.client.delete_documents_by_id(list(all_internal_ids_to_delete))
                logger.info(f"Successfully processed deletion requests for overwrite streams.")
            except Exception as e:
                logger.error(f"Failed during document deletion for streams {stream_names}: {e}", exc_info=True)
                raise AirbyteTracedException(
                    message=f"Failed to delete documents during overwrite for streams {stream_names}.",
                    internal_message=str(e),
                    failure_type=FailureType.system_error,
                ) from e
        else:
            logger.info("No documents found to delete across overwrite streams.")

    # --- Helper Methods (_get_value_from_path, _calculate_content_hash, _preload_hashes_if_needed) - No changes needed ---
    def _get_value_from_path(self, data: Dict[str, Any], path_str: Optional[str]) -> Any:
        if not path_str or not isinstance(data, dict):
            return None
        path = path_str.split(".")
        current = data
        for i, key in enumerate(path):
            if isinstance(current, dict):
                if key in current:
                    current = current[key]
                else:
                    return None
            elif isinstance(current, list):
                if key.isdigit():
                    try:
                        index = int(key)
                        if 0 <= index < len(current):
                            current = current[index]
                        else:
                            return None
                    except (ValueError, IndexError):
                        return None
                else:
                    logger.debug(f"Attempted list access with non-integer key '{key}' in path '{path_str}'.")
                    return None
            else:
                return None
        return current

    def _calculate_content_hash(
        self, metadata: Dict[str, Any], content: Optional[Dict[str, Any]] = None, file_info: Optional[Dict[str, Any]] = None
    ) -> str:
        hasher = hashlib.sha256()
        content_part = ""
        metadata_part = ""
        if file_info:
            stable_file_info = {
                "path": file_info.get("file_relative_path"),
                "modified": file_info.get("modified"),
                "size": file_info.get("bytes"),
            }
            stable_file_info = {k: v for k, v in stable_file_info.items() if v is not None}
            content_part = json.dumps(stable_file_info, sort_keys=True, ensure_ascii=False)
        elif content:
            content_part = json.dumps(content, sort_keys=True, ensure_ascii=False)
        hashable_metadata = {
            k: v for k, v in metadata.items() if k not in [self.METADATA_AIRBYTE_STREAM_FIELD, self.METADATA_CONTENT_HASH_FIELD]
        }
        metadata_part = json.dumps(hashable_metadata, sort_keys=True, ensure_ascii=False)
        combined_str = content_part + "::" + metadata_part
        hasher.update(combined_str.encode("utf-8"))
        hash_result = hasher.hexdigest()
        # logger.debug(f"Calculated content hash: {hash_result} (File: {bool(file_info)}, Metadata Keys: {list(hashable_metadata.keys())})")
        return hash_result

    def _preload_hashes_if_needed(self, stream_id: str) -> None:
        if stream_id in self.hashes_preloaded:
            return
        logger.info(f"Preloading hashes for stream '{stream_id}'...")
        try:
            filter_conditions = {self.METADATA_AIRBYTE_STREAM_FIELD: stream_id}
            metadata_hash_field_path = f"metadata.{self.METADATA_CONTENT_HASH_FIELD}"
            existing_docs = self.client.find_docs_by_metadata(filter_conditions, fields=["id", "metadata"])
            hashes = set()
            found_hashes = 0
            docs_without_hash = 0
            for doc in existing_docs:
                doc_metadata = doc.get("metadata", {})
                content_hash = doc_metadata.get(self.METADATA_CONTENT_HASH_FIELD)
                if content_hash:
                    hashes.add(content_hash)
                    found_hashes += 1
                else:
                    docs_without_hash += 1
            self.seen_hashes[stream_id] = hashes
            self.hashes_preloaded.add(stream_id)
            log_msg = f"Finished preloading for '{stream_id}'. Found {len(hashes)} existing hashes."
            if docs_without_hash > 0:
                log_msg += f" ({docs_without_hash} docs missing hash)."
            logger.info(log_msg)
        except Exception as e:
            logger.error(f"Failed to preload hashes for stream '{stream_id}': {e}", exc_info=True)
            self.hashes_preloaded.add(stream_id)
            self.seen_hashes[stream_id] = set()
            logger.warning(f"Deduplication for '{stream_id}' may be incomplete due to hash preload failure.")

    def _prepare_metadata(self, record_data: Dict[str, Any], stream_id: str) -> Dict[str, Any]:
        """Extracts, combines, and cleans metadata. Ensures values are suitable types."""
        combined_metadata = copy.deepcopy(self.static_metadata)
        if self.config.metadata_fields:
            for field_path_str in self.config.metadata_fields:
                value = self._get_value_from_path(record_data, field_path_str)
                if value is not None:
                    key = field_path_str.replace(".", "_")
                    # Ragie metadata values: string, number, boolean, list of strings.
                    if isinstance(value, (str, bool)):
                        combined_metadata[key] = value
                    elif isinstance(value, (int, float)):
                        # Ensure it's finite (not NaN or Infinity)
                        if isinstance(value, float) and not all(map(float.isfinite, [value])):
                            logger.warning(f"Skipping non-finite float metadata field '{key}' (path: {field_path_str}). Value: {value}")
                            continue
                        combined_metadata[key] = value
                    elif isinstance(value, list) and all(isinstance(item, str) for item in value):
                        combined_metadata[key] = value
                    else:
                        # Try converting other types to string as fallback
                        try:
                            str_value = str(value)
                            combined_metadata[key] = str_value
                            logger.debug(f"Converted metadata field '{key}' (type: {type(value)}) to string.")
                        except Exception as str_err:
                            logger.warning(
                                f"Could not convert metadata field '{key}' from path '{field_path_str}' to string (type: {type(value)}). Error: {str_err}. Skipping."
                            )

        final_metadata = {}
        for key, value in combined_metadata.items():
            new_key = key
            # Clean key: remove leading/trailing spaces, handle reserved/internal names
            clean_key = key.strip()
            if not clean_key:
                logger.warning(f"Skipping metadata field with empty key (original: '{key}').")
                continue
            new_key = clean_key

            if new_key in self.RESERVED_METADATA_KEYS or new_key.startswith("_"):
                temp_key = new_key.lstrip("_")
                new_key = f"{temp_key}_" if temp_key else "_"  # Handle case of key being only underscores
                if new_key != key:
                    logger.debug(f"Adjusted reserved/internal metadata key '{key}' to '{new_key}'")

            # replace common problematic chars like '.', '$', space
            problematic_chars = [".", "$", " "]
            if any(char in new_key for char in problematic_chars):
                original_key = new_key
                for char in problematic_chars:
                    new_key = new_key.replace(char, "_")
                logger.warning(f"Adjusted metadata key '{original_key}' to '{new_key}' due to problematic characters.")

            # Final check if cleaned key is empty or reserved again
            if not new_key:
                logger.warning(f"Skipping metadata field - key became empty after cleaning (original: '{key}').")
                continue
            if new_key in self.RESERVED_METADATA_KEYS:
                new_key = f"{new_key}_"
                logger.debug(f"Post-cleaning key '{key}' resulted in reserved key, appended underscore -> '{new_key}'")

            final_metadata[new_key] = value

        final_metadata[self.METADATA_AIRBYTE_STREAM_FIELD] = stream_id

        # Check metadata size limits (optional but good practice)
        if len(final_metadata) > 1000:  # Approximation, actual limit counts list items individually
            logger.warning(f"Metadata for record exceeds ~1000 key-value pairs ({len(final_metadata)}). Ragie might truncate or reject.")

        return final_metadata

    def queue_write_operation(self, record: AirbyteRecordMessage) -> None:
        """
        Processes Airbyte record, prepares payload for Ragie client (JSON only).
        """
        stream_id = self._stream_tuple_to_id(record.namespace, record.stream)
        stream_config = self.streams.get(stream_id)
        if not stream_config:
            logger.warning(f"Stream config not found for '{stream_id}', skipping.")
            return
        if not isinstance(record.data, dict):
            logger.warning(f"Record data is not dict in stream '{stream_id}', skipping.")
            return

        record_data = record.data
        # Payload dictionary passed to the client.
        payload: Dict[str, Any] = {}
        content_to_send: Optional[Dict[str, Any]] = None

        # --- 1. Extract Content Based on Config ---
        if self.config.content_fields:
            # Extract specified keys, supporting dot notation for nested fields
            content_to_send = {}
            for key in self.config.content_fields:
                value = self._get_value_from_path(record_data, key)
                if value is not None:
                    content_to_send[key] = value
                else:
                    logger.warning(f"Key '{key}' not found in record data for stream '{stream_id}'.")
        else:
            # Use the entire record data
            content_to_send = record_data

        if not content_to_send:
            logger.warning(f"Content data is empty in stream '{stream_id}'. Skipping.")
            return
        payload["data"] = content_to_send  # Key for JSON data

        # --- 2. Prepare Metadata ---
        final_metadata = self._prepare_metadata(record_data, stream_id)

        # --- 3. Determine Name ---
        doc_name = None
        if self.config.document_name_field:
            value = self._get_value_from_path(record_data, self.config.document_name_field)
            if value is not None:
                doc_name = str(value)
        if not doc_name:  # Fallback if no name
            doc_name = f"airbyte_{stream_id}_{uuid.uuid4()}"
        payload["name"] = doc_name  # Include name in payload for client

        # --- 4. Determine External ID ---
        external_id = None
        if self.config.external_id_field:
            value = self._get_value_from_path(record_data, self.config.external_id_field)
            if value is not None:
                external_id = str(value)
                payload["external_id"] = external_id  # Include external_id for client

        # --- 5. Calculate Content Hash ---
        temp_metadata_for_hashing = copy.deepcopy(final_metadata)
        content_hash = self._calculate_content_hash(metadata=temp_metadata_for_hashing, content=content_to_send)
        final_metadata[self.METADATA_CONTENT_HASH_FIELD] = content_hash
        payload["metadata"] = final_metadata  # Store final metadata dict in payload

        # --- 6. Deduplication Check ---
        if stream_config.destination_sync_mode == DestinationSyncMode.append_dedup:
            self._preload_hashes_if_needed(stream_id)
            if content_hash in self.seen_hashes.get(stream_id, set()):
                logger.info(f"Skipping duplicate record in stream '{stream_id}' (Hash: {content_hash}, Name: '{doc_name}').")
                return
            else:
                self.seen_hashes.setdefault(stream_id, set()).add(content_hash)

        # --- 7. Add Other Parameters ---
        payload["mode"] = self.config.processing_mode
        payload["partition"] = self.config.partition

        # --- 8. Send to Client ---
        try:
            logger.debug(f"Queueing JSON payload for '{doc_name}' (Stream: {stream_id}, Hash: {content_hash})")
            self.client.index_documents([payload])
        except Exception as e:
            logger.error(f"Error during client indexing call: {e}", exc_info=True)
            raise e  # Re-raise for destination write loop
