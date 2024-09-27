from typing import Any, Iterable, List, Mapping, MutableMapping, Optional
import json

from airbyte_cdk.sources.streams.core import Stream
from couchbase.cluster import Cluster

from .queries import (
    get_datastores_query,
    get_namespaces_query,
    get_buckets_query,
    get_scopes_query,
    get_keyspaces_query,
    get_indexes_query,
    get_dual_query,
    get_vitals_query,
    get_active_requests_query,
    get_prepareds_query,
    get_completed_requests_query,
    get_my_user_info_query,
    get_user_info_query,
    get_nodes_query,
    get_applicable_roles_query,
    get_dictionary_query,
    get_dictionary_cache_query,
    get_functions_query,
    get_functions_cache_query,
    get_tasks_cache_query,
    get_transactions_query,
    get_sequences_query,
    get_all_sequences_query,
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

    @property
    def json_schema(self):
        return {}

class Datastores(CouchbaseStream):
    name = "datastores"
    primary_key = "id"

    def read_records(self, sync_mode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = get_datastores_query()
        result = self.cluster.query(query)
        yield from result

    @property
    def json_schema(self):
        schema_path = "source_couchbase/schemas/datastores.json"
        with open(schema_path, "r") as f:
            return json.load(f)

class Namespaces(CouchbaseStream):
    name = "namespaces"
    primary_key = "id"

    def read_records(self, sync_mode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = get_namespaces_query()
        result = self.cluster.query(query)
        yield from result

    @property
    def json_schema(self):
        schema_path = "source_couchbase/schemas/namespaces.json"
        with open(schema_path, "r") as f:
            return json.load(f)

class Buckets(CouchbaseStream):
    name = "buckets"
    primary_key = "name"

    def read_records(self, sync_mode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = get_buckets_query()
        result = self.cluster.query(query)
        yield from result

    @property
    def json_schema(self):
        schema_path = "source_couchbase/schemas/buckets.json"
        with open(schema_path, "r") as f:
            return json.load(f)

class Scopes(CouchbaseStream):
    name = "scopes"
    primary_key = ["bucket", "name"]

    def read_records(self, sync_mode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = get_scopes_query()
        result = self.cluster.query(query)
        yield from result

    @property
    def json_schema(self):
        schema_path = "source_couchbase/schemas/scopes.json"
        with open(schema_path, "r") as f:
            return json.load(f)

class Keyspaces(CouchbaseStream):
    name = "keyspaces"
    primary_key = "id"

    def read_records(self, sync_mode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = get_keyspaces_query()
        result = self.cluster.query(query)
        yield from result

    @property
    def json_schema(self):
        schema_path = "source_couchbase/schemas/keyspaces.json"
        with open(schema_path, "r") as f:
            return json.load(f)

class Indexes(CouchbaseStream):
    name = "indexes"
    primary_key = "id"

    def read_records(self, sync_mode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = get_indexes_query()
        result = self.cluster.query(query)
        yield from result

    @property
    def json_schema(self):
        schema_path = "source_couchbase/schemas/indexes.json"
        with open(schema_path, "r") as f:
            return json.load(f)

class Dual(CouchbaseStream):
    name = "dual"

    def read_records(self, sync_mode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = get_dual_query()
        result = self.cluster.query(query)
        yield from result

    @property
    def json_schema(self):
        schema_path = "source_couchbase/schemas/dual.json"
        with open(schema_path, "r") as f:
            return json.load(f)

class Vitals(CouchbaseStream):
    name = "vitals"

    def read_records(self, sync_mode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = get_vitals_query()
        result = self.cluster.query(query)
        yield from result

    @property
    def json_schema(self):
        schema_path = "source_couchbase/schemas/vitals.json"
        with open(schema_path, "r") as f:
            return json.load(f)

class ActiveRequests(CouchbaseStream):
    name = "active_requests"
    primary_key = "requestId"

    def read_records(self, sync_mode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = get_active_requests_query()
        result = self.cluster.query(query)
        yield from result

    @property
    def json_schema(self):
        schema_path = "source_couchbase/schemas/active_requests.json"
        with open(schema_path, "r") as f:
            return json.load(f)

class Prepareds(CouchbaseStream):
    name = "prepareds"
    primary_key = "name"

    def read_records(self, sync_mode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = get_prepareds_query()
        result = self.cluster.query(query)
        yield from result

    @property
    def json_schema(self):
        schema_path = "source_couchbase/schemas/prepareds.json"
        with open(schema_path, "r") as f:
            return json.load(f)

class CompletedRequests(CouchbaseStream):
    name = "completed_requests"
    primary_key = "requestId"

    def read_records(self, sync_mode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = get_completed_requests_query()
        result = self.cluster.query(query)
        yield from result

    @property
    def json_schema(self):
        schema_path = "source_couchbase/schemas/completed_requests.json"
        with open(schema_path, "r") as f:
            return json.load(f)

class MyUserInfo(CouchbaseStream):
    name = "my_user_info"
    primary_key = "id"

    def read_records(self, sync_mode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = get_my_user_info_query()
        result = self.cluster.query(query)
        yield from result

    @property
    def json_schema(self):
        schema_path = "source_couchbase/schemas/my_user_info.json"
        with open(schema_path, "r") as f:
            return json.load(f)

class UserInfo(CouchbaseStream):
    name = "user_info"
    primary_key = "id"

    def read_records(self, sync_mode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = get_user_info_query()
        result = self.cluster.query(query)
        yield from result

    @property
    def json_schema(self):
        schema_path = "source_couchbase/schemas/user_info.json"
        with open(schema_path, "r") as f:
            return json.load(f)

class Nodes(CouchbaseStream):
    name = "nodes"
    primary_key = "name"

    def read_records(self, sync_mode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = get_nodes_query()
        result = self.cluster.query(query)
        yield from result

    @property
    def json_schema(self):
        schema_path = "source_couchbase/schemas/nodes.json"
        with open(schema_path, "r") as f:
            return json.load(f)

class ApplicableRoles(CouchbaseStream):
    name = "applicable_roles"
    primary_key = "role"

    def read_records(self, sync_mode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = get_applicable_roles_query()
        result = self.cluster.query(query)
        yield from result

    @property
    def json_schema(self):
        schema_path = "source_couchbase/schemas/applicable_roles.json"
        with open(schema_path, "r") as f:
            return json.load(f)

class Dictionary(CouchbaseStream):
    name = "dictionary"
    primary_key = ["bucket", "keyspace"]

    def read_records(self, sync_mode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = get_dictionary_query()
        result = self.cluster.query(query)
        yield from result

    @property
    def json_schema(self):
        schema_path = "source_couchbase/schemas/dictionary.json"
        with open(schema_path, "r") as f:
            return json.load(f)

class DictionaryCache(CouchbaseStream):
    name = "dictionary_cache"
    primary_key = ["bucket", "keyspace"]

    def read_records(self, sync_mode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = get_dictionary_cache_query()
        result = self.cluster.query(query)
        yield from result

    @property
    def json_schema(self):
        schema_path = "source_couchbase/schemas/dictionary_cache.json"
        with open(schema_path, "r") as f:
            return json.load(f)

class Functions(CouchbaseStream):
    name = "functions"

    def read_records(self, sync_mode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = get_functions_query()
        result = self.cluster.query(query)
        yield from result

    @property
    def json_schema(self):
        schema_path = "source_couchbase/schemas/functions.json"
        with open(schema_path, "r") as f:
            return json.load(f)

class FunctionsCache(CouchbaseStream):
    name = "functions_cache"

    def read_records(self, sync_mode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = get_functions_cache_query()
        result = self.cluster.query(query)
        yield from result

    @property
    def json_schema(self):
        schema_path = "source_couchbase/schemas/functions_cache.json"
        with open(schema_path, "r") as f:
            return json.load(f)

class TasksCache(CouchbaseStream):
    name = "tasks_cache"
    primary_key = "id"

    def read_records(self, sync_mode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = get_tasks_cache_query()
        result = self.cluster.query(query)
        yield from result

    @property
    def json_schema(self):
        schema_path = "source_couchbase/schemas/tasks_cache.json"
        with open(schema_path, "r") as f:
            return json.load(f)

class Transactions(CouchbaseStream):
    name = "transactions"

    def read_records(self, sync_mode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = get_transactions_query()
        result = self.cluster.query(query)
        yield from result

    @property
    def json_schema(self):
        schema_path = "source_couchbase/schemas/transactions.json"
        with open(schema_path, "r") as f:
            return json.load(f)

class Sequences(CouchbaseStream):
    name = "sequences"

    def read_records(self, sync_mode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = get_sequences_query()
        result = self.cluster.query(query)
        yield from result

    @property
    def json_schema(self):
        schema_path = "source_couchbase/schemas/sequences.json"
        with open(schema_path, "r") as f:
            return json.load(f)

class AllSequences(CouchbaseStream):
    name = "all_sequences"

    def read_records(self, sync_mode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = get_all_sequences_query()
        result = self.cluster.query(query)
        yield from result

    @property
    def json_schema(self):
        schema_path = "source_couchbase/schemas/all_sequences.json"
        with open(schema_path, "r") as f:
            return json.load(f)

class Documents(CouchbaseStream):
    name = "documents"
    primary_key = "id"

    def read_records(self, sync_mode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        buckets_result = self.cluster.query(get_buckets_query())
        
        for bucket_row in buckets_result:
            bucket_name = bucket_row.get('buckets', {}).get('name')
            if not bucket_name:
                continue

            scopes_result = self.cluster.query(get_scopes_query())
            
            for scope_row in scopes_result:
                scope_name = scope_row.get('scopes', {}).get('name')
                if not scope_name:
                    continue

                collections_result = self.cluster.query(get_keyspaces_query())
                
                for collection_row in collections_result:
                    collection_name = collection_row.get('keyspaces', {}).get('name')
                    if not collection_name:
                        continue

                    documents_result = self.cluster.query(get_documents_query(bucket_name, scope_name, collection_name))
                    for row in documents_result:
                        yield self.format_document(row, bucket_name, scope_name, collection_name)

    @staticmethod
    def format_document(row, bucket_name, scope_name, collection_name):
        return {
            "id": row.get("id", ""),
            "bucket": bucket_name,
            "scope": scope_name,
            "collection": collection_name,
            "content": row,
        }