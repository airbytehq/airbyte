import logging
from datetime import timedelta
from typing import Any, List, Mapping, Optional, Tuple, Iterable
import time

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.models import (
    ConnectorSpecification,
    FailureType,
    AirbyteMessage,
    Type,
    ConfiguredAirbyteCatalog,
    AirbyteStateMessage,
    AirbyteRecordMessage,
)
from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

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
                        state=config.get('state', {})
                    ))
                else:
                    streams.append(CouchbaseStream(cluster, config['bucket'], scope.name, collection.name))
        
        if not streams:
            raise AirbyteTracedException(
                internal_message="No streams available",
                message="No streams could be generated from the provided configuration. Please check your permissions and the names of buckets, scopes, and collections.",
                failure_type=FailureType.config_error
            )
        
        return streams

    def read(self, logger: logging.Logger, config: Mapping[str, Any], catalog: ConfiguredAirbyteCatalog, state: Mapping[str, Any] = None) -> Iterable[AirbyteMessage]:
        state = state or {}
        for configured_stream in catalog.streams:
            stream = next(stream for stream in self.streams(config) if stream.name == configured_stream.stream.name)
            stream_state = state.get(stream.name, {})
            for record in stream.read_records(sync_mode=configured_stream.sync_mode, cursor_field=configured_stream.cursor_field, stream_slice=None, stream_state=stream_state):
                yield AirbyteMessage(
                    type=Type.RECORD,
                    record=AirbyteRecordMessage(
                        stream=stream.name,
                        data=record,
                        emitted_at=int(time.time() * 1000)
                    )
                )
            
            if isinstance(stream, IncrementalCouchbaseStream):
                stream_state = stream.state
                yield AirbyteMessage(
                    type=Type.STATE,
                    state=AirbyteStateMessage(data={stream.name: stream_state})
                )

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
        
        return True, None