# Copyright (c) 2024 Couchbase, Inc., all rights reserved.

from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping

from couchbase.cluster import Cluster
from couchbase.exceptions import QueryIndexNotFoundException
from couchbase.options import QueryOptions

from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, FailureType, SyncMode, Type
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import CheckpointMixin
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

from .queries import get_documents_query


PAGE_SIZE = 1000


class CouchbaseStream(Stream):
    primary_key = "_id"

    def __init__(self, cluster: Cluster, bucket: str, scope: str, collection: str):
        self.cluster = cluster
        self.bucket = bucket
        self.scope = scope
        self.collection = collection
        self._name = f"{bucket}.{scope}.{collection}"

    @property
    def name(self) -> str:
        return self._name


class DocumentStream(CouchbaseStream, CheckpointMixin):
    cursor_field = "_ab_cdc_updated_at"

    def __init__(self, cluster: Cluster, bucket: str, scope: str, collection: str):
        super().__init__(cluster, bucket, scope, collection)
        self._state: MutableMapping[str, Any] = {}

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        self._state = value

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "_id": {"type": "string"},
                self.cursor_field: {"type": "integer"},
                self.collection: {"type": "object", "additionalProperties": True},
            },
        }

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: AirbyteRecordMessage) -> Mapping[str, Any]:
        latest_cursor_value = latest_record.data.get(self.cursor_field)
        current_cursor_value = current_stream_state.get(self.cursor_field)

        if latest_cursor_value is not None and (current_cursor_value is None or int(latest_cursor_value) > int(current_cursor_value)):
            return {self.cursor_field: int(latest_cursor_value)}
        return current_stream_state

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[AirbyteMessage]:
        cursor_value = stream_state.get(self.cursor_field, 0) if stream_state else 0

        query = get_documents_query(
            self.bucket, self.scope, self.collection, self.cursor_field, cursor_value if sync_mode == SyncMode.incremental else None
        )

        last_id = ""
        while True:
            rows_in_page = 0
            for row in self._query_page(query, last_id):
                rows_in_page += 1
                last_id = row["_id"]
                record = AirbyteRecordMessage(stream=self.name, data=row, emitted_at=int(datetime.now().timestamp()) * 1000)
                yield AirbyteMessage(type=Type.RECORD, record=record)
                if sync_mode == SyncMode.incremental:
                    self.state = self.get_updated_state(self.state, record)
            if rows_in_page < PAGE_SIZE:
                break

    def _query_page(self, query: str, last_id: str) -> Iterable[Mapping[str, Any]]:
        try:
            yield from self.cluster.query(query, QueryOptions(named_parameters={"last_id": last_id, "page_size": PAGE_SIZE}))
        except QueryIndexNotFoundException as e:
            raise AirbyteTracedException(
                message=(
                    f"No primary index is available on `{self.bucket}`.`{self.scope}`.`{self.collection}`. Create one with "
                    f"`CREATE PRIMARY INDEX ON `{self.bucket}`.`{self.scope}`.`{self.collection}`` (or grant the Airbyte user the "
                    "'Query Manage Index' role so the connector can create it) and wait for the index to come online."
                ),
                internal_message=str(e),
                failure_type=FailureType.config_error,
            ) from e
