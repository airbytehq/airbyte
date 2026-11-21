#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import base64
from datetime import datetime, timezone
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

from google.cloud import datastore

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream


# Number of entities sampled per Kind during discover() to infer schema columns.
_SCHEMA_SAMPLE_SIZE = 100


def _serialize_value(value: Any) -> Any:
    """Convert Datastore-specific types to JSON-serializable equivalents."""
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()
    if isinstance(value, datastore.Key):
        return "/".join(str(part) for part in value.flat_path)
    if isinstance(value, bytes):
        return base64.b64encode(value).decode("utf-8")
    if isinstance(value, dict):
        return {k: _serialize_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_serialize_value(v) for v in value]
    return value


def _key_to_str(key: datastore.Key) -> str:
    return "/".join(str(part) for part in key.flat_path)


def _infer_json_type(value: Any) -> Mapping[str, Any]:
    """Map a Python value to its JSON Schema type declaration."""
    # bool must be checked before int (bool is a subclass of int in Python)
    if isinstance(value, bool):
        return {"type": ["null", "boolean"]}
    if isinstance(value, int):
        return {"type": ["null", "integer"]}
    if isinstance(value, float):
        return {"type": ["null", "number"]}
    if isinstance(value, datetime):
        return {"type": ["null", "string"], "format": "date-time"}
    if isinstance(value, bytes):
        return {"type": ["null", "string"], "contentEncoding": "base64"}
    if isinstance(value, datastore.Key):
        return {"type": ["null", "string"]}
    if isinstance(value, list):
        return {"type": ["null", "array"]}
    if isinstance(value, dict):
        return {"type": ["null", "object"]}
    return {"type": ["null", "string"]}


class DatastoreStream(Stream):
    """One stream per Datastore Kind.

    The cursor field is NOT source-defined: the user selects it per stream in
    the Airbyte connection UI. This allows different cursor fields per Kind
    without any source-level configuration.
    """

    primary_key = "_key"
    # Let the Airbyte UI expose cursor field selection per stream.
    source_defined_cursor = False

    def __init__(
        self,
        client: datastore.Client,
        kind: str,
        namespace: Optional[str],
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._client = client
        self._kind = kind
        self._namespace = namespace or None
        # Set by read_records() from the Airbyte-provided cursor_field parameter.
        self._active_cursor: Optional[str] = None

    @property
    def name(self) -> str:
        return self._kind.lower().replace(" ", "_").replace("-", "_")

    @property
    def cursor_field(self) -> str:
        return self._active_cursor or ""

    @property
    def supported_sync_modes(self) -> List[SyncMode]:
        return [SyncMode.full_refresh, SyncMode.incremental]

    def get_json_schema(self) -> Mapping[str, Any]:
        """Sample up to _SCHEMA_SAMPLE_SIZE entities to infer property columns."""
        props: MutableMapping[str, Any] = {
            "_key": {
                "description": "Flat string representation of the Datastore entity key path.",
                "type": ["null", "string"],
            },
            "_kind": {
                "description": "Datastore Kind this entity belongs to.",
                "type": ["null", "string"],
            },
            "_namespace": {
                "description": "Datastore namespace this entity belongs to.",
                "type": ["null", "string"],
            },
        }
        query = self._client.query(kind=self._kind, namespace=self._namespace)
        for entity in query.fetch(limit=_SCHEMA_SAMPLE_SIZE):
            for field, value in entity.items():
                if field not in props:
                    props[field] = _infer_json_type(value)

        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": ["null", "object"],
            "properties": props,
            # Keep true so new properties on entities not in the sample still flow through.
            "additionalProperties": True,
        }

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        if not self._active_cursor:
            return {}
        latest = str(latest_record.get(self._active_cursor, ""))
        current = str(current_stream_state.get(self._active_cursor, ""))
        return {self._active_cursor: max(latest, current)}

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        # Airbyte passes cursor_field as List[str], e.g. ["updated_at"].
        self._active_cursor = cursor_field[0] if cursor_field else None

        query = self._client.query(kind=self._kind, namespace=self._namespace)

        if sync_mode == SyncMode.incremental and self._active_cursor and stream_state and stream_state.get(self._active_cursor):
            query.add_filter(filter=datastore.query.PropertyFilter(self._active_cursor, ">=", stream_state[self._active_cursor]))

        # Datastore's fetch() handles server-side pagination transparently.
        for entity in query.fetch():
            record: MutableMapping[str, Any] = {
                "_key": _key_to_str(entity.key),
                "_kind": self._kind,
                "_namespace": self._namespace or "",
            }
            for field, value in entity.items():
                record[field] = _serialize_value(value)
            yield record
