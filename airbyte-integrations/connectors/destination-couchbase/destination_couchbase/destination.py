# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging
from typing import Any, Iterable, Mapping
from uuid import uuid4

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, DestinationSyncMode, Status, Type
from couchbase.cluster import Cluster
from couchbase.auth import PasswordAuthenticator
from couchbase.options import ClusterOptions

logger = logging.getLogger("airbyte")

class DestinationCouchbase(Destination):
    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        """
        Reads the input stream of messages, config, and catalog to write data to Couchbase.
        """
        streams = {s.stream.name for s in configured_catalog.streams}
        logger.info(f"Starting write to Couchbase with {len(streams)} streams")

        cluster = self._get_cluster(config)
        bucket = cluster.bucket(config["bucket"])
        collection = bucket.default_collection()

        buffer = {}
        buffer_size = 1000  # Adjust as needed

        for configured_stream in configured_catalog.streams:
            if configured_stream.destination_sync_mode == DestinationSyncMode.overwrite:
                self._clear_collection(bucket, configured_stream.stream.name)
                logger.info(f"Stream {configured_stream.stream.name} is wiped.")

        for message in input_messages:
            if message.type == Type.STATE:
                self._flush_buffer(collection, buffer)
                yield message
            elif message.type == Type.RECORD:
                data = message.record.data
                stream = message.record.stream
                if stream not in streams:
                    logger.debug(f"Stream {stream} was not present in configured streams, skipping")
                    continue
                
                if stream not in buffer:
                    buffer[stream] = []
                
                buffer[stream].append(self._prepare_document(stream, data))

                if len(buffer[stream]) >= buffer_size:
                    self._flush_buffer(collection, {stream: buffer[stream]})
                    buffer[stream] = []

        # Flush any remaining messages
        self._flush_buffer(collection, buffer)

    @staticmethod
    def _get_cluster(config: Mapping[str, Any]) -> Cluster:
        auth = PasswordAuthenticator(config["username"], config["password"])
        return Cluster(config["connection_string"], ClusterOptions(auth))

    @staticmethod
    def _clear_collection(bucket, stream_name: str):
        query = f"DELETE FROM `{bucket.name}` WHERE META().id LIKE $1"
        bucket.cluster.query(query, f"{stream_name}::%")

    @staticmethod
    def _prepare_document(stream: str, data: Mapping[str, Any]) -> Mapping[str, Any]:
        return {
            "_id": f"{stream}::{str(uuid4())}",
            "_airbyte_ab_id": str(uuid4()),
            "_airbyte_emitted_at": data.get("_airbyte_emitted_at"),
            "_airbyte_data": data
        }

    @staticmethod
    def _flush_buffer(collection, buffer: Mapping[str, list]):
        for stream, documents in buffer.items():
            if documents:
                try:
                    collection.insert_multi(documents)
                except Exception as e:
                    logger.error(f"Error writing to Couchbase for stream {stream}: {str(e)}")
        buffer.clear()  # Clear the buffer after flushing

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            cluster = self._get_cluster(config)
            bucket = cluster.bucket(config["bucket"])
            bucket.ping()
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
