# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
from typing import List, Dict, Any
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator

# Data Containers
def get_datastores_query() -> str:
    return "SELECT * FROM system:datastores"

def get_namespaces_query() -> str:
    return "SELECT * FROM system:namespaces"

def get_buckets_query() -> str:
    return "SELECT * FROM system:buckets"

def get_scopes_query() -> str:
    return "SELECT * FROM system:scopes"

def get_keyspaces_query() -> str:
    return "SELECT * FROM system:keyspaces"

def get_indexes_query() -> str:
    return "SELECT * FROM system:indexes"

def get_dual_query() -> str:
    return "SELECT * FROM system:dual"

# Monitoring Catalogs
def get_vitals_query() -> str:
    return "SELECT * FROM system:vitals"

def get_active_requests_query() -> str:
    return "SELECT * FROM system:active_requests"

def get_prepareds_query() -> str:
    return "SELECT * FROM system:prepareds"

def get_completed_requests_query() -> str:
    return "SELECT * FROM system:completed_requests"

# Security Catalogs
def get_my_user_info_query() -> str:
    return "SELECT * FROM system:my_user_info"

def get_user_info_query() -> str:
    return "SELECT * FROM system:user_info"

def get_nodes_query() -> str:
    return "SELECT * FROM system:nodes"

def get_applicable_roles_query() -> str:
    return "SELECT * FROM system:applicable_roles"

# Other
def get_dictionary_query() -> str:
    return "SELECT * FROM system:dictionary"

def get_dictionary_cache_query() -> str:
    return "SELECT * FROM system:dictionary_cache"

def get_functions_query() -> str:
    return "SELECT * FROM system:functions"

def get_functions_cache_query() -> str:
    return "SELECT * FROM system:functions_cache"

def get_tasks_cache_query() -> str:
    return "SELECT * FROM system:tasks_cache"

def get_transactions_query() -> str:
    return "SELECT * FROM system:transactions"

def get_sequences_query() -> str:
    return "SELECT * FROM system:sequences"

def get_all_sequences_query() -> str:
    return "SELECT * FROM system:all-sequences"

def get_documents_query(bucket: str, scope: str, collection: str) -> str:
    return f"""
    SELECT * FROM `{bucket}`.`{scope}`.`{collection}`
    """

def get_cluster_queries(bucket: str, scope: str, collection: str) -> List[Dict[str, Any]]:
    """
    Returns a list of all cluster queries to be executed.
    Each query is represented as a dictionary with 'name' and 'query' keys.
    """
    return [
        {"name": "datastores", "query": get_datastores_query()},
        {"name": "namespaces", "query": get_namespaces_query()},
        {"name": "buckets", "query": get_buckets_query()},
        {"name": "scopes", "query": get_scopes_query()},
        {"name": "keyspaces", "query": get_keyspaces_query()},
        {"name": "indexes", "query": get_indexes_query()},
        {"name": "dual", "query": get_dual_query()},
        {"name": "vitals", "query": get_vitals_query()},
        {"name": "active_requests", "query": get_active_requests_query()},
        {"name": "prepareds", "query": get_prepareds_query()},
        {"name": "completed_requests", "query": get_completed_requests_query()},
        {"name": "my_user_info", "query": get_my_user_info_query()},
        {"name": "user_info", "query": get_user_info_query()},
        {"name": "nodes", "query": get_nodes_query()},
        {"name": "applicable_roles", "query": get_applicable_roles_query()},
        {"name": "dictionary", "query": get_dictionary_query()},
        {"name": "dictionary_cache", "query": get_dictionary_cache_query()},
        {"name": "functions", "query": get_functions_query()},
        {"name": "functions_cache", "query": get_functions_cache_query()},
        {"name": "tasks_cache", "query": get_tasks_cache_query()},
        {"name": "transactions", "query": get_transactions_query()},
        {"name": "sequences", "query": get_sequences_query()},
        {"name": "all_sequences", "query": get_all_sequences_query()},
        {"name": "documents", "query": get_documents_query(bucket, scope, collection)},
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
