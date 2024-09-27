from typing import Any, Iterable, List, Mapping, MutableMapping, Optional
import json

from airbyte_cdk.sources.streams.core import Stream
from couchbase.cluster import Cluster

from .queries import (
    get_buckets_query,
    get_scopes_query,
    get_collections_query,
    get_documents_query,
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
        yield from result

class Scopes(CouchbaseStream):
    """
    Stream for Couchbase scopes across all buckets.
    """
    primary_key = ["bucket", "name"]
    name = "scopes"

    def read_records(self, sync_mode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        buckets_result = self.cluster.query(get_buckets_list_query())
        
        for bucket_row in buckets_result:
            bucket_name = bucket_row.get('name')
            if bucket_name:
                scopes_result = self.cluster.query(get_scopes_query(bucket_name))
                yield from (row for row in scopes_result if 'name' in row)

class Collections(CouchbaseStream):
    """
    Stream for Couchbase collections across all buckets and scopes.
    """
    primary_key = ["bucket", "scope", "name"]
    name = "collections"

    def read_records(self, sync_mode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        buckets_result = self.cluster.query(get_buckets_list_query())
        
        for bucket_row in buckets_result:
            bucket_name = bucket_row.get('name')
            if not bucket_name:
                continue

            scopes_result = self.cluster.query(get_scopes_query(bucket_name))
            
            for scope_row in scopes_result:
                scope_name = scope_row.get('name')
                if not scope_name:
                    continue

                collections_result = self.cluster.query(get_collections_query(bucket_name, scope_name))
                yield from (row for row in collections_result if 'name' in row)

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
        buckets_result = self.cluster.query(get_buckets_list_query())
        
        for bucket_row in buckets_result:
            bucket_name = bucket_row.get('name')
            if not bucket_name:
                continue

            scopes_result = self.cluster.query(get_scopes_query(bucket_name))
            
            for scope_row in scopes_result:
                scope_name = scope_row.get('name')
                if not scope_name:
                    continue

                collections_result = self.cluster.query(get_collections_query(bucket_name, scope_name))
                
                for collection_row in collections_result:
                    collection_name = collection_row.get('name')
                    if not collection_name:
                        continue

                    documents_result = self.cluster.query(get_documents_query(bucket_name, scope_name, collection_name))
                    for row in documents_result:
                        if 'id' in row:
                            yield self.format_document(row, bucket_name, scope_name, collection_name)

    @staticmethod
    def format_document(row, bucket_name, scope_name, collection_name):
        return {
            "id": row["id"],
            "bucket": bucket_name,
            "scope": scope_name,
            "collection": collection_name,
            "content": row,
            "metadata": {
                "expiration": row.get("expiration"),
                "flags": row.get("flags"),
                "cas": str(row.get("cas"))
            }
        }