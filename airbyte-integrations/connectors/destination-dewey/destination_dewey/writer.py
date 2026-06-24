#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
import logging
import re
import uuid
from typing import Any, Dict, List, Mapping, Optional

import dpath.util

from airbyte_cdk.models import AirbyteRecordMessage, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode
from airbyte_cdk.utils.traced_exception import AirbyteTracedException, FailureType
from destination_dewey.client import (
    METADATA_NAMESPACE_FIELD,
    METADATA_PK_FIELD,
    METADATA_STREAM_FIELD,
    PK_TAG_PREFIX,
    STREAM_TAG_PREFIX,
    DeweyClient,
)


_FILENAME_SAFE = re.compile(r"[^A-Za-z0-9._-]+")


def _stream_identifier(record: AirbyteRecordMessage) -> str:
    namespace = record.namespace or "default"
    return f"{namespace}__{record.stream}"


def _sanitize_filename(value: str, *, max_len: int = 80) -> str:
    cleaned = _FILENAME_SAFE.sub("-", value).strip("-") or "record"
    return cleaned[:max_len]


class DeweyWriter:
    def __init__(
        self,
        client: DeweyClient,
        *,
        catalog: ConfiguredAirbyteCatalog,
        stream_collections: Mapping[str, str],
        auto_create_collections: bool,
        text_fields: Optional[List[str]],
        title_field: Optional[str],
        metadata_fields: Optional[List[str]],
        flush_interval: int,
        parallelize: bool,
    ):
        self.client = client
        self.text_fields = text_fields or []
        self.title_field = title_field or ""
        self.metadata_fields = metadata_fields or []
        self.flush_interval = flush_interval
        self.parallelize = parallelize
        self.auto_create_collections = auto_create_collections

        self.streams: Dict[str, ConfiguredAirbyteStream] = {_stream_identifier_from_stream(s): s for s in catalog.streams}
        self._stream_collections: Dict[str, str] = dict(stream_collections)

        self._buffer: List[Dict[str, Any]] = []
        # PKs to delete at flush time for append_dedup mode, keyed by collection_id
        self._dedup_targets: Dict[str, List[str]] = {}

    # ---- public API ---------------------------------------------------------------

    def resolve_collections(self) -> None:
        """Validate every configured stream maps to a Dewey collection (auto-create if needed)."""
        for stream_id, stream in self.streams.items():
            if stream_id in self._stream_collections:
                col_id = self._stream_collections[stream_id]
                col = self.client.get_collection(col_id)
                if col is None:
                    raise AirbyteTracedException(
                        internal_message=f"Collection {col_id} for stream {stream_id} not found",
                        message=f"Configured Dewey collection `{col_id}` for stream `{stream_id}` does not exist.",
                        failure_type=FailureType.config_error,
                    )
                continue
            if not self.auto_create_collections:
                raise AirbyteTracedException(
                    internal_message=f"No collection mapping for stream {stream_id}",
                    message=(
                        f"Stream `{stream_id}` is in the configured catalog but no Dewey collection is "
                        "mapped for it. Add it to `stream_collections` or enable `auto_create_collections`."
                    ),
                    failure_type=FailureType.config_error,
                )
            created = self.client.create_collection(name=f"airbyte_{stream_id}")
            new_id = created.get("id")
            if not new_id:
                raise AirbyteTracedException(
                    internal_message=f"Dewey returned no id for created collection: {created}",
                    message=f"Dewey did not return an id when creating a collection for stream `{stream_id}`.",
                    failure_type=FailureType.system_error,
                )
            self._stream_collections[stream_id] = new_id

    def delete_streams_to_overwrite(self) -> None:
        for stream_id, stream in self.streams.items():
            if stream.destination_sync_mode != DestinationSyncMode.overwrite:
                continue
            collection_id = self._stream_collections.get(stream_id)
            if not collection_id:
                continue
            tag = f"{STREAM_TAG_PREFIX}{stream_id}"
            doc_ids = self.client.find_document_ids_by_tag(collection_id, tag)
            if doc_ids:
                self.client.delete_documents(collection_id, doc_ids)

    def queue(self, record: AirbyteRecordMessage) -> None:
        stream_id = _stream_identifier(record)
        if stream_id not in self.streams:
            return
        collection_id = self._stream_collections.get(stream_id)
        if not collection_id:
            return

        primary_key = self._record_primary_key(record, stream_id)
        text = self._extract_text(record)
        metadata = self._extract_metadata(record, stream_id, primary_key)
        title = self._extract_title(record)
        filename = self._build_filename(title, primary_key, record)

        tags = [f"{STREAM_TAG_PREFIX}{stream_id}"]
        if primary_key is not None:
            tags.append(f"{PK_TAG_PREFIX}{primary_key}")

        # For append_dedup, queue a delete-by-PK before flush so updates replace the prior version.
        stream = self.streams[stream_id]
        if stream.destination_sync_mode == DestinationSyncMode.append_dedup and primary_key is not None:
            self._dedup_targets.setdefault(collection_id, []).append(f"{PK_TAG_PREFIX}{primary_key}")

        content = json.dumps(text, ensure_ascii=False, sort_keys=True).encode("utf-8")
        self._buffer.append(
            {
                "collection_id": collection_id,
                "filename": filename,
                "content": content,
                "content_type": "application/json",
                "tags": tags,
                "metadata": metadata,
            }
        )
        if len(self._buffer) >= self.flush_interval:
            self.flush()

    def flush(self) -> None:
        if self._dedup_targets:
            for collection_id, pk_tags in self._dedup_targets.items():
                ids: List[str] = []
                for tag in set(pk_tags):
                    ids.extend(self.client.find_document_ids_by_tag(collection_id, tag))
                if ids:
                    self.client.delete_documents(collection_id, ids)
            self._dedup_targets.clear()

        if not self._buffer:
            return

        # Group by collection_id; Dewey upload endpoint is per-collection.
        by_collection: Dict[str, List[Dict[str, Any]]] = {}
        for item in self._buffer:
            by_collection.setdefault(item["collection_id"], []).append(item)
        for collection_id, items in by_collection.items():
            uploads = [
                {
                    "collection_id": collection_id,
                    "filename": item["filename"],
                    "content": item["content"],
                    "content_type": item["content_type"],
                    "tags": item["tags"],
                    "metadata": item["metadata"],
                }
                for item in items
            ]
            self.client.upload_documents(uploads, parallelize=self.parallelize)
        self._buffer.clear()

    # ---- internals ----------------------------------------------------------------

    def _extract_text(self, record: AirbyteRecordMessage) -> Any:
        if not self.text_fields:
            return record.data
        relevant = self._project(record.data, self.text_fields)
        if not relevant:
            raise AirbyteTracedException(
                internal_message=f"No text fields found in record from stream {record.stream}",
                message=(
                    f"Record from stream `{record.stream}` does not contain any of the configured "
                    f"text_fields: {', '.join(self.text_fields)}."
                ),
                failure_type=FailureType.config_error,
            )
        return relevant

    def _extract_metadata(self, record: AirbyteRecordMessage, stream_id: str, primary_key: Optional[str]) -> Dict[str, Any]:
        metadata: Dict[str, Any] = {}
        if self.metadata_fields:
            metadata.update(self._project(record.data, self.metadata_fields))
        else:
            # Drop collections to keep metadata flat-ish; Dewey stores arbitrary JSON, but flat keys
            # work better for the metadata filter on /research and /query.
            for k, v in record.data.items():
                if isinstance(v, (str, int, float, bool)) or v is None:
                    metadata[k] = v
        metadata[METADATA_STREAM_FIELD] = stream_id
        metadata[METADATA_NAMESPACE_FIELD] = record.namespace or "default"
        if primary_key is not None:
            metadata[METADATA_PK_FIELD] = primary_key
        return metadata

    def _extract_title(self, record: AirbyteRecordMessage) -> Optional[str]:
        if not self.title_field:
            return None
        values = dpath.util.values(record.data, self.title_field, separator=".")
        if not values:
            return None
        return str(values[0])

    def _record_primary_key(self, record: AirbyteRecordMessage, stream_id: str) -> Optional[str]:
        stream = self.streams[stream_id]
        if not stream.primary_key:
            return None
        parts: List[str] = []
        for key_path in stream.primary_key:
            # primary_key is List[List[str]] — outer list = composite, inner list = path
            try:
                parts.append(str(dpath.util.get(record.data, key_path)))
            except KeyError:
                parts.append("__not_found__")
        return "_".join(parts)

    def _build_filename(self, title: Optional[str], primary_key: Optional[str], record: AirbyteRecordMessage) -> str:
        base = title or primary_key or uuid.uuid4().hex
        return f"{_sanitize_filename(base)}.json"

    @staticmethod
    def _project(data: Mapping[str, Any], fields: List[str]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for field in fields:
            values = dpath.util.values(data, field, separator=".")
            if values:
                result[field] = values[0] if len(values) == 1 else values
        return result


def _stream_identifier_from_stream(stream: ConfiguredAirbyteStream) -> str:
    namespace = stream.stream.namespace or "default"
    return f"{namespace}__{stream.stream.name}"
