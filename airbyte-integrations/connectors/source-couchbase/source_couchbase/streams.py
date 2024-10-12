# Copyright (c) 2024 Couchbase, Inc., all rights reserved.

from abc import ABC
from logging import getLogger
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import IncrementalMixin
from couchbase.cluster import Cluster

from .queries import get_documents_query, get_incremental_documents_query

logger = getLogger(__name__)

class CouchbaseStream(Stream, ABC):
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
                "_ab_cdc_updated_at": {"type": "integer"},
                self.collection: {
                    "type": "object",
                    "additionalProperties": True
                }
            }
        }

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = get_documents_query(self.bucket, self.scope, self.collection)
        for row in self.cluster.query(query):
            yield row

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
        latest_benchmark = latest_record.get(self.cursor_field)
        if latest_benchmark is not None:
            current_stream_state = current_stream_state or {}
            max_value = max(latest_benchmark, current_stream_state.get(self.cursor_field, latest_benchmark))
            return {self.cursor_field: max_value}
        return current_stream_state

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        cursor_value = stream_state.get(self.cursor_field) if stream_state else None
        query = get_incremental_documents_query(self.bucket, self.scope, self.collection, cursor_value)
        
        for row in self.cluster.query(query):
            yield row
