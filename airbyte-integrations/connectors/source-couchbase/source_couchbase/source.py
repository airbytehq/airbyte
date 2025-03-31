# Copyright (c) 2024 Couchbase, Inc., all rights reserved.

import logging
from datetime import timedelta
from typing import Any, List, Mapping, Tuple

from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .streams import DocumentStream


class SourceCouchbase(AbstractSource):
    def __init__(self):
        super().__init__()
        self.connection_string = None
        self.username = None
        self.password = None
        self.bucket_name = None

    @property
    def name(self) -> str:
        return "Couchbase"

    def _set_config_values(self, config: Mapping[str, Any]):
        self.connection_string = config["connection_string"]
        self.username = config["username"]
        self.password = config["password"]
        self.bucket_name = config["bucket"]

    def _get_cluster(self) -> Cluster:
        auth = PasswordAuthenticator(self.username, self.password)
        options = ClusterOptions(auth)
        options.apply_profile("wan_development")
        cluster = Cluster(self.connection_string, options)
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

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        self._set_config_values(config)
        try:
            cluster = self._get_cluster()
            bucket = cluster.bucket(self.bucket_name)
            bucket.ping()
            logger.info("Successfully connected to Couchbase cluster and bucket")
            return True, None
        except Exception as e:
            logger.error(f"Connection check failed: {str(e)}")
            return False, f"Connection check failed: {str(e)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        self._set_config_values(config)
        cluster = self._get_cluster()
        bucket = cluster.bucket(self.bucket_name)
        streams = []

        for scope in bucket.collections().get_all_scopes():
            for collection in scope.collections:
                self._ensure_primary_index(cluster, self.bucket_name, scope.name, collection.name)
                stream = DocumentStream(cluster, self.bucket_name, scope.name, collection.name)
                streams.append(stream)
                logging.info(f"Added stream for {scope.name}.{collection.name}")

        logging.info(f"Generated {len(streams)} streams")
        return streams
