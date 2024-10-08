import logging
from datetime import timedelta
from typing import Any, List, Mapping, Optional, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.models import ConnectorSpecification
from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.exceptions import QueryIndexNotFoundException  # Ensure this import is present

from .streams import CouchbaseStream, IncrementalCouchbaseStream

class SourceCouchbase(AbstractSource):
    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            cluster = self._get_cluster(config)
            bucket = cluster.bucket(config['bucket'])
            bucket.ping()
            logger.info("Successfully connected to Couchbase cluster and bucket")
            return True, None
        except Exception as e:
            logger.error(f"Connection check failed: {str(e)}")
            return False, f"Connection check failed: {str(e)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        cluster = self._get_cluster(config)
        bucket = cluster.bucket(config['bucket'])
        
        streams = []
        
        for scope in bucket.collections().get_all_scopes():
            for collection in scope.collections:
                self._ensure_primary_index(cluster, config['bucket'], scope.name, collection.name)
                if config.get('use_incremental', False):
                    streams.append(IncrementalCouchbaseStream(
                        cluster,
                        config['bucket'],
                        scope.name,
                        collection.name,
                        cursor_field=config.get('cursor_field', 'updated_at'),
                        state=config.get('state', {})  # Pass the initial state here
                    ))
                else:
                    streams.append(CouchbaseStream(cluster, config['bucket'], scope.name, collection.name))
        
        return streams

    @staticmethod
    def _get_cluster(config: Mapping[str, Any]) -> Cluster:
        auth = PasswordAuthenticator(config['username'], config['password'])
        options = ClusterOptions(auth)
        options.apply_profile('wan_development')
        cluster = Cluster(config['connection_string'], options)
        cluster.wait_until_ready(timedelta(seconds=5))
        return cluster

    @staticmethod
    def _ensure_primary_index(cluster: Cluster, bucket: str, scope: str, collection: str):
        index_name = f"{bucket}_{scope}_{collection}_primary_index"
        query = f"CREATE PRIMARY INDEX IF NOT EXISTS `{index_name}` ON `{bucket}`.`{scope}`.`{collection}`"
        logging.debug(f"Executing query to ensure primary index: {query}")
        try:
            cluster.query(query).execute()
            logging.debug(f"Successfully ensured primary index for {bucket}.{scope}.{collection}")
        except Exception as e:
            logging.warning(f"Failed to create primary index for {bucket}.{scope}.{collection}: {str(e)}")

    @property
    def name(self) -> str:
        return "Couchbase"

    @staticmethod
    def _validate_config(config: Mapping[str, Any]) -> Tuple[bool, Optional[str]]:
        required_fields = ["connection_string", "username", "password", "bucket"]
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            return False, f"Missing required configuration fields: {', '.join(missing_fields)}"
        
        if config.get('use_incremental', False) and 'cursor_field' not in config:
            return False, "Cursor field must be specified when using incremental sync"
        
        return True, None