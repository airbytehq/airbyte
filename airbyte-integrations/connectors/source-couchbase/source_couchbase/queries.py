# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
from typing import List, Dict, Any
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator


def get_buckets_query() -> str:
    """
    Returns the query for fetching the list of buckets.
    """
    return "SELECT * FROM system:buckets"
    

def get_scopes_query(bucket: str) -> str:
    """
    Returns the query for fetching scope information for a specific bucket.
    """
    return f"SELECT * FROM `{bucket}`._scopes"


def get_collections_query(bucket: str, scope: str) -> str:
    """
    Returns the query for fetching collection information for a specific bucket and scope.
    """
    return f"SELECT * FROM `{bucket}`.`{scope}`._collections"


def get_documents_query(bucket: str, scope: str, collection: str) -> str:
    """
    Returns the query template for fetching documents for a specific bucket, scope, and collection.
    """
    return f"""
    SELECT META(d).id AS `id`, d.*, META(d).expiration, META(d).flags, META(d).cas
    FROM `{bucket}`.`{scope}`.`{collection}` d
    """


def get_buckets_list_query() -> str:
    """
    Returns the query for fetching the list of buckets.
    """
    return "SELECT * FROM system:buckets"


def get_cluster_queries(bucket: str, scope: str, collection: str) -> List[Dict[str, Any]]:
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
            "query": get_scopes_query(bucket)
        },
        {
            "name": "collections",
            "query": get_collections_query(bucket, scope)
        },
        {
            "name": "documents",
            "query": get_documents_query(bucket, scope, collection)
        },
    ]

def demo_queries(cluster: Cluster, bucket: str, scope: str, collection: str):
    queries = get_cluster_queries(bucket, scope, collection)
    for query_info in queries:
        query_name = query_info['name']
        query = query_info['query']
        print(f"Executing query: {query_name}")
        try:
            result = cluster.query(query)
            for row in result:
                print(row)
        except Exception as e:
            print(f"Error executing query {query_name}: {e}")

    # Fetch and print all available keyspaces
    print("\nFetching all available keyspaces:")
    keyspaces_query = "SELECT * FROM system:keyspaces"
    try:
        result = cluster.query(keyspaces_query)
        for row in result:
            print(row)
    except Exception as e:
        print(f"Error fetching keyspaces: {e}")

def read_config():
    """
    Reads the configuration from secrets/config.json
    """
    with open('secrets/config.json', 'r') as config_file:
        return json.load(config_file)

if __name__ == "__main__":
    # Read configuration from secrets/config.json
    config = read_config()
    
    # Use configuration values
    connection_string = config['connection_string']
    username = config['username']
    password = config['password']
    bucket = config['bucket']
    scope = config['scope']
    collection = config['collection']

    try:
        cluster = Cluster(connection_string, ClusterOptions(PasswordAuthenticator(username, password)))
        demo_queries(cluster, bucket, scope, collection)
    except Exception as e:
        print(f"Error connecting to Couchbase cluster: {e}")
