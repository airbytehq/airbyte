import json
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

from airbyte_cdk.sources.streams import Stream
from couchbase.cluster import Cluster

from .queries import (
    get_buckets_query,
    get_scopes_query,
    get_collections_query,
    get_documents_query,
    get_buckets_list_query
)

class CouchbaseStream(Stream):
    """
    Base stream class for Couchbase. Handles connection and basic operations.
    """
    primary_key = None

    def __init__(self, cluster: Cluster):
        self.cluster = cluster
        
    def next_page_token(self, response: Any) -> Optional[Mapping[str, Any]]:
        """
        Couchbase REST API doesn't support pagination for most endpoints.
        """
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        No default query parameters.
        """
        return {}

    def parse_response(self, response: Any, **kwargs) -> Iterable[Mapping]:
        """
        Parse the response and yield records.
        """
        yield response

class Buckets(CouchbaseStream):
    """
    Stream for Couchbase buckets.
    """
    primary_key = "name"
    name = "buckets"

    def read_records(self, sync_mode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = get_buckets_query()
        result = self.cluster.query(query)
        for row in result:
            yield row

class Scopes(CouchbaseStream):
    """
    Stream for Couchbase scopes across all buckets.
    """
    primary_key = ["bucket", "name"]
    name = "scopes"

    def read_records(self, sync_mode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = get_scopes_query()
        result = self.cluster.query(query)
        for row in result:
            yield row

class Collections(CouchbaseStream):
    """
    Stream for Couchbase collections across all buckets and scopes.
    """
    primary_key = ["bucket", "scope", "name"]
    name = "collections"

    def read_records(self, sync_mode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = get_collections_query()
        result = self.cluster.query(query)
        for row in result:
            yield row

class Documents(CouchbaseStream):
    """
    Stream for Couchbase documents across all buckets, scopes, and collections.
    """
    primary_key = "id"
    name = "documents"

    @property
    def json_schema(self):
        schema_path = "source_couchbase/schemas/documents.json"
        with open(schema_path, "r") as f:
            return json.load(f)

    def read_records(self, sync_mode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        documents_query = get_documents_query()
        buckets_query = get_buckets_list_query()
        buckets_result = self.cluster.query(buckets_query)
        
        for bucket_row in buckets_result:
            bucket = self.cluster.bucket(bucket_row['name'])
            for scope in bucket.collections().get_all_scopes():
                for collection in scope.collections:
                    result = self.cluster.query(documents_query.format(bucket.name, scope.name, collection.name))
                    for row in result:
                        yield {
                            "id": row["id"],
                            "bucket": row["bucket"],
                            "scope": row["scope"],
                            "collection": row["collection"],
                            "content": row["content"],
                            "metadata": {
                                "expiration": row["expiration"],
                                "flags": row["flags"],
                                "cas": str(row["cas"])
                            }
                        }