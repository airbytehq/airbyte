# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging
from typing import Any, Iterable, Mapping
from uuid import uuid4

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, DestinationSyncMode, Status, Type
from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.exceptions import DocumentExistsException
from couchbase.options import ClusterOptions
from couchbase.result import MultiMutationResult

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
                self._clear_collection(cluster, config["bucket"], configured_stream.stream.name)
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
    def _clear_collection(cluster: Cluster, bucket_name: str, stream_name: str):
        query = f"DELETE FROM `{bucket_name}` WHERE META().id LIKE $1"
        cluster.query(query, f"{stream_name}::%")

    @staticmethod
    def _prepare_document(stream: str, data: Mapping[str, Any]) -> Mapping[str, Any]:
        # Ensure that _airbyte_emitted_at is always a valid value
        emitted_at = data.get("_airbyte_emitted_at") or int(uuid4().time)
        
        return {
            "id": f"{stream}::{str(uuid4())}",  # Changed from '_id' to 'id'
            "type": "airbyte_record",  # Added a type field
            "stream": stream,
            "emitted_at": emitted_at,
            "data": data  # Keep the original data intact
        }

    @staticmethod
    def _flush_buffer(collection, buffer: Mapping[str, list]):
        for stream, documents in buffer.items():
            if documents:
                batch = {doc["id"]: doc for doc in documents}
                try:
                    result: MultiMutationResult = collection.upsert_multi(batch)
                    
                    if not result.all_ok and result.exceptions:
                        duplicate_ids = []
                        other_errors = []
                        for doc_id, ex in result.exceptions.items():
                            if isinstance(ex, DocumentExistsException):
                                duplicate_ids.append(doc_id)
                            else:
                                other_errors.append({"id": doc_id, "exception": str(ex)})

                        if duplicate_ids:
                            logger.warning(f"Documents with IDs '{', '.join(duplicate_ids)}' already exist in the collection for stream {stream}")

                        if other_errors:
                            logger.error(f"Failed to load documents into Couchbase for stream {stream}. Errors:\n{other_errors}")

                    logger.info(f"Successfully loaded {len(batch)} documents for stream {stream}")

                except Exception as e:
                    logger.exception(f"Error occurred while loading documents for stream {stream}: {e}")
                    logger.error(f"Failed to load documents into Couchbase for stream {stream}. Error: {e}")

        buffer.clear()  # Clear the buffer after flushing

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            cluster = self._get_cluster(config)
            bucket = cluster.bucket(config["bucket"])
            bucket.ping()
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
