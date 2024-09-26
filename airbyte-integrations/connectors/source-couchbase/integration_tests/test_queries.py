import json
import pytest
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
from source_couchbase.queries import (
    get_buckets_query,
    get_scopes_query,
    get_collections_query,
    get_documents_query,
    get_cluster_queries,
)

def read_config():
    """
    Reads the configuration from secrets/config.json
    """
    with open('secrets/config.json', 'r') as config_file:
        return json.load(config_file)

@pytest.fixture(scope="module")
def couchbase_cluster():
    config = read_config()
    connection_string = config['connection_string']
    username = config['username']
    password = config['password']
    
    cluster = Cluster(connection_string, ClusterOptions(PasswordAuthenticator(username, password)))
    yield cluster
    cluster.close()

@pytest.fixture(scope="module")
def couchbase_config():
    config = read_config()
    return config

def test_demo_queries(couchbase_cluster, couchbase_config):
    bucket = couchbase_config['bucket']
    scope = couchbase_config['scope']
    collection = couchbase_config['collection']

    queries = get_cluster_queries(bucket, scope, collection)
    for query_info in queries:
        query_name = query_info['name']
        query = query_info['query']
        print(f"Executing query: {query_name}")
        try:
            result = couchbase_cluster.query(query)
            rows = list(result)
            assert len(rows) > 0, f"Query {query_name} returned no results"
            print(f"Query {query_name} returned {len(rows)} rows")
        except Exception as e:
            pytest.fail(f"Error executing query {query_name}: {e}")

    # Fetch and print all available keyspaces
    print("\nFetching all available keyspaces:")
    keyspaces_query = "SELECT * FROM system:keyspaces"
    try:
        result = couchbase_cluster.query(keyspaces_query)
        rows = list(result)
        assert len(rows) > 0, "Keyspaces query returned no results"
        print(f"Keyspaces query returned {len(rows)} rows")
    except Exception as e:
        pytest.fail(f"Error fetching keyspaces: {e}")

if __name__ == "__main__":
    pytest.main([__file__])