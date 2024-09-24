#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
import requests
from datetime import timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions, ClusterTimeoutOptions, QueryOptions

class CouchbaseStream(Stream):
    """
    Base stream class for Couchbase. Handles connection and basic operations.
    """
    primary_key = None

    def __init__(self, cluster: Cluster, bucket_name: str, scope_name: str = "_default"):
        self.cluster = cluster
        self.bucket = self.cluster.bucket(bucket_name)
        self.scope = self.bucket.scope(scope_name)
        
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Couchbase REST API doesn't support pagination for most endpoints.
        """
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        No default query parameters.
        """
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Parse the response and yield records.
        """
        yield response.json()

    def read_records(self, sync_mode, cursor_field = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        raise NotImplementedError("Subclasses should implement this method")

class Buckets(CouchbaseStream):
    """
    Stream for Couchbase buckets.
    """
    primary_key = "name"

    def read_records(self, sync_mode, cursor_field = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = "SELECT name, bucketType, numReplicas FROM system:buckets"
        result = self.cluster.query(query)
        for row in result:
            yield row

class Documents(CouchbaseStream):
    """
    Stream for Couchbase documents within a bucket and scope.
    """
    primary_key = "id"

    def __init__(self, cluster: Cluster, bucket_name: str, scope_name: str, collection_name: str):
        super().__init__(cluster, bucket_name, scope_name)
        self.collection = self.scope.collection(collection_name)

    def read_records(self, sync_mode, cursor_field = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        query = f"SELECT META().id, * FROM `{self.bucket.name}`.`{self.scope.name}`.`{self.collection.name}`"
        result = self.cluster.query(query)
        for row in result:
            yield row

class SourceCouchbase(AbstractSource):

    logger: logging.Logger = logging.getLogger("airbyte")

    def check_connection(self, logger: logging.Logger
                         , config) -> Tuple[bool, any]:
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
        streams = [Buckets(cluster, config['bucket_name'])]
        
        try:
            bucket = cluster.bucket(config['bucket_name'])
            for scope in bucket.collections().get_all_scopes():
                for collection in scope.collections:
                    streams.append(
                        Documents(
                            cluster,
                            config['bucket_name'],
                            scope.name,
                            collection.name
                        )
                    )
            self.logger.info(f"Discovered {len(streams)} streams")
        except Exception as e:
            self.logger.error(f"Error discovering streams: {str(e)}")
        
        return streams

    @staticmethod
    def _get_cluster(config: Mapping[str, Any]) -> Cluster:
        auth = PasswordAuthenticator(config['username'], config['password'])
        options = ClusterOptions(auth)
        options.apply_profile('wan_development')
        cluster = Cluster(f"{config['connection_string']}", options)
        cluster.wait_until_ready(timedelta(seconds=5))
        return cluster

    @staticmethod
    def validate_config(config: Mapping[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validates the configuration.
        """
        required_fields = ["connection_string", "username", "password", "bucket_name"]
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            return False, f"Missing required configuration fields: {', '.join(missing_fields)}"
        
        return True, None
