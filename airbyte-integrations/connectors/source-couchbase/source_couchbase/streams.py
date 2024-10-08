from typing import Any, Iterable, List, Mapping, MutableMapping, Dict, Optional
from airbyte_cdk.models import SyncMode, AirbyteStateMessage, AirbyteStateType
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
        return "id"

    def get_json_schema(self) -> Dict[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "content": {"type": "object", "additionalProperties": True}
            }
        }

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = get_documents_query(self.bucket, self.scope, self.collection)
        yield from self._execute_query(query)

    def _execute_query(self, query: str) -> Iterable[Mapping[str, Any]]:
        for row in self.cluster.query(query):
            yield self._process_row(row)

    def _process_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        content = row.get(self.collection, {})
        return {
            "id": row["id"],
            "content": content if isinstance(content, dict) else {"value": content}
        }

class IncrementalCouchbaseStream(CouchbaseStream, IncrementalMixin):
    def __init__(self, cluster: Cluster, bucket: str, scope: str, collection: str, cursor_field: str, state: MutableMapping[str, Any] = None):
        super().__init__(cluster, bucket, scope, collection)
        self._cursor_field = cursor_field
        self._state = state or {}

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        self._state = value

    @property
    def cursor_field(self) -> str:
        return self._cursor_field

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        latest_benchmark = latest_record["content"].get(self.cursor_field)
        if latest_benchmark is not None:
            return {self.cursor_field: max(latest_benchmark, current_stream_state.get(self.cursor_field, latest_benchmark))}
        return current_stream_state

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = self._build_query(self.state)
        for record in self._process_query_results(query):
            yield record
            yield from self._yield_state()

    def _build_query(self, stream_state: Optional[Mapping[str, Any]] = None) -> str:
        cursor_value = stream_state.get(self.cursor_field) if stream_state else None
        return get_incremental_documents_query(self.bucket, self.scope, self.collection, self.cursor_field, cursor_value)

    def _process_query_results(self, query: str) -> Iterable[Mapping[str, Any]]:
        missing_cursor_field_records = []
        for record in self._execute_query(query):
            if self.cursor_field not in record["content"]:
                missing_cursor_field_records.append(record["id"])
            else:
                self.state = self.get_updated_state(self.state, record)
            yield record
        self._log_missing_cursor_field_records(missing_cursor_field_records)

    def _log_missing_cursor_field_records(self, missing_records: List[str]):
        if missing_records:
            logger.warning(f"Records missing the cursor field {self.cursor_field}: {', '.join(missing_records)}. These records will not update the state.")

    def _yield_state(self) -> Iterable[AirbyteStateMessage]:
        if self.state:
            yield AirbyteStateMessage(type=AirbyteStateType.STREAM, stream=self.name, data={self.cursor_field: self.state[self.cursor_field]})

    def _process_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        record = super()._process_row(row)
        if self.cursor_field not in record["content"]:
            record["content"][self.cursor_field] = None
        return record
