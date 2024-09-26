# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import List, Dict, Any

def get_buckets_query() -> str:
    """
    Returns the query for fetching bucket information.
    """
    return "SELECT name, bucketType, numReplicas, ramQuota, replicaNumber FROM system:buckets"

def get_scopes_query() -> str:
    """
    Returns the query for fetching scope information across all buckets.
    """
    return "SELECT b.name as bucket, s.name, s.uid FROM system:buckets b JOIN system:scopes s ON META(b).id = s.bucket_uid"

def get_collections_query() -> str:
    """
    Returns the query for fetching collection information across all buckets and scopes.
    """
    return """
    SELECT b.name as bucket, s.name as scope, c.name, c.uid
    FROM system:buckets b
    JOIN system:scopes s ON META(b).id = s.bucket_uid
    JOIN system:collections c ON s.uid = c.scope_uid
    """

def get_documents_query() -> str:
    """
    Returns the query template for fetching documents across all buckets, scopes, and collections.
    """
    return """
    SELECT b.name AS bucket, s.name AS scope, c.name AS collection, META(d).id AS id, d.* AS content, META(d).expiration, META(d).flags, META(d).cas
    FROM system:buckets b
    JOIN system:scopes s ON META(b).id = s.bucket_uid
    JOIN system:collections c ON s.uid = c.scope_uid
    JOIN `{0}`.`{1}`.`{2}` d
    """

def get_buckets_list_query() -> str:
    """
    Returns the query for fetching the list of buckets.
    """
    return "SELECT name FROM system:buckets"

def get_cluster_queries() -> List[Dict[str, Any]]:
    """
    Returns a list of all cluster queries to be executed.
    Each query is represented as a dictionary with 'name' and 'query' keys.
    """
    return [
        {
            "name": "buckets",
            "query": get_buckets_query()
        },
        {
            "name": "scopes",
            "query": get_scopes_query()
        },
        {
            "name": "collections",
            "query": get_collections_query()
        },
        {
            "name": "documents_template",
            "query": get_documents_query()
        },
        {
            "name": "buckets_list",
            "query": get_buckets_list_query()
        }
    ]

# Add more functions for different types of queries if necessary