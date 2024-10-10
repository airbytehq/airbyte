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
        state = self._validate_state(state or {})
        
        try:
            for configured_stream in catalog.streams:
                stream = next(stream for stream in self.streams(config) if stream.name == configured_stream.stream.name)
                stream_state = state.get(stream.name, {})
                
                try:
                    for record in self._read_records(stream, configured_stream, stream_state):
                        yield AirbyteMessage(
                            type=Type.RECORD,
                            record=AirbyteRecordMessage(
                                stream=stream.name,
                                data=record,
                                emitted_at=int(time.time() * 1000)
                            )
                        )
                except Exception as e:
                    logger.error(f"Error reading records from stream {stream.name}: {str(e)}")
                    raise
                
                if isinstance(stream, IncrementalCouchbaseStream):
                    stream_state = stream.state
                    if '_ab_cdc_updated_at' in stream_state:
                        yield AirbyteMessage(
                            type=Type.STATE,
                            state=AirbyteStateMessage(data={stream.name: {'_ab_cdc_updated_at': stream_state['_ab_cdc_updated_at']}})
                        )
        except Exception as e:
            logger.error(f"Unexpected error during sync: {str(e)}")
            raise

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
        try:
            cluster.query(query).execute()
        except Exception as e:
            logging.error(f"Failed to create primary index for {bucket}.{scope}.{collection}: {str(e)}")

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

    @staticmethod
    def _validate_state(state: Mapping[str, Any]) -> Mapping[str, Any]:
        if not isinstance(state, dict):
            raise ValueError(f"State must be a dictionary, got {type(state)}")
        for stream_name, stream_state in state.items():
            if not isinstance(stream_state, dict):
                raise ValueError(f"State for stream {stream_name} must be a dictionary, got {type(stream_state)}")
            if '_ab_cdc_updated_at' in stream_state and not isinstance(stream_state['_ab_cdc_updated_at'], (int, float)):
                raise ValueError(f"_ab_cdc_updated_at for stream {stream_name} must be a number, got {type(stream_state['_ab_cdc_updated_at'])}")
        return state

    @staticmethod
    def _read_records(stream, configured_stream, stream_state):
        for record in stream.read_records(sync_mode=configured_stream.sync_mode, cursor_field=configured_stream.cursor_field, stream_slice=None, stream_state=stream_state):
            yield record
