from typing import Any, Iterable, List, Mapping, MutableMapping, Dict, Optional
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import IncrementalMixin
from couchbase.cluster import Cluster
from logging import getLogger

from .queries import get_documents_query, get_incremental_documents_query

logger = getLogger(__name__)

class CouchbaseStream(Stream):
    def __init__(self, cluster: Cluster, bucket: str, scope: str, collection: str):
        super().__init__()
        self.cluster = cluster
        self.bucket = bucket
        self.scope = scope
        self.collection = collection
        self._name = f"{bucket}.{scope}.{collection}"

    @property
    def name(self) -> str:
        return self._name

    @property
    def primary_key(self) -> str:
        return "_id"

    def get_json_schema(self) -> Dict[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "_id": {"type": "string"},
                "content": {"type": "object", "additionalProperties": True}
            }
        }

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = get_documents_query(self.bucket, self.scope, self.collection)
        for row in self.cluster.query(query):
            yield self._process_row(row)

    def _process_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "_id": row["_id"],
            "content": {k: v for k, v in row.items() if k != "_id"}
        }

class IncrementalCouchbaseStream(CouchbaseStream, IncrementalMixin):
    cursor_field = "_ab_cdc_updated_at"

    def __init__(self, cluster: Cluster, bucket: str, scope: str, collection: str, state: MutableMapping[str, Any] = None):
        super().__init__(cluster, bucket, scope, collection)
        self._state = state or {}

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        self._state = value

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        latest_benchmark = latest_record.get(self.cursor_field)
        if latest_benchmark:
            current_stream_state[self.cursor_field] = max(
                latest_benchmark,
                current_stream_state.get(self.cursor_field, 0)
            )
        return current_stream_state

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {}
        cursor_value = stream_state.get(self.cursor_field, 0)
        query = get_incremental_documents_query(self.bucket, self.scope, self.collection, cursor_value)
        for row in self.cluster.query(query):
            record = self._process_row(row)
            self.state = self.get_updated_state(self.state, record)
            yield record

    def _process_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        processed_row = {
            "_id": row["_id"],
            self.cursor_field: row.get(self.cursor_field, 0),
            "content": {k: v for k, v in row.items() if k not in ["_id", self.cursor_field]}
        }
        return processed_row

    def get_json_schema(self) -> Dict[str, Any]:
        schema = super().get_json_schema()
        schema["properties"][self.cursor_field] = {"type": "number"}
        return schema
