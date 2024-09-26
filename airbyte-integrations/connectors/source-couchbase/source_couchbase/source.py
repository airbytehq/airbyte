import logging
from datetime import timedelta
from typing import Any, List, Mapping, Optional, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions

from .streams import Buckets, Collections, Documents, Scopes

class SourceCouchbase(AbstractSource):
    logger: logging.Logger = logging.getLogger("airbyte")

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        """
        Checks if the input configuration can be used to successfully connect to the Couchbase cluster.
        """
        try:
            cluster = self._get_cluster(config)
            cluster.ping()
            logger.info("Successfully connected to Couchbase cluster")
            return True, None
        except Exception as e:
            logger.error(f"Connection check failed: {str(e)}")
            return False, f"Connection check failed: {str(e)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Returns a list of discovered streams.
        """
        cluster = self._get_cluster(config)
        return [
            Buckets(cluster),
            Scopes(cluster),
            Collections(cluster),
            Documents(cluster)
        ]

    @staticmethod
    def _get_cluster(config: Mapping[str, Any]) -> Cluster:
        auth = PasswordAuthenticator(config['username'], config['password'])
        options = ClusterOptions(auth)
        options.apply_profile('wan_development')
        cluster = Cluster(config['connection_string'], options)
        cluster.wait_until_ready(timedelta(seconds=5))
        return cluster

    @staticmethod
    def _validate_config(config: Mapping[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validates the configuration.
        """
        required_fields = ["connection_string", "username", "password"]
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            return False, f"Missing required configuration fields: {', '.join(missing_fields)}"
        
        return True, None
