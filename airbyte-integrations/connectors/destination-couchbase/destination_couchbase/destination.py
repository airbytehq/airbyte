# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging
import re
from datetime import timedelta
from typing import Any, Iterable, Mapping
from uuid import uuid4

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, DestinationSyncMode, Status, Type
from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.exceptions import DocumentExistsException, CouchbaseException
from couchbase.options import ClusterOptions, UpsertOptions

logger = logging.getLogger("airbyte")

class DestinationCouchbase(Destination):
    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        """
        Reads the input stream of messages, config, and catalog to write data to Couchbase.
        """
        cluster = self._get_cluster(config)
        bucket_name = config["bucket"]
        scope_name = config.get("scope", "_default")

        streams = {s.stream.name: self._sanitize_collection_name(s.stream.name) for s in configured_catalog.streams}
        logger.info(f"Starting write to Couchbase with {len(streams)} streams")

        collections = {stream: self._setup_collection(cluster, bucket_name, scope_name, sanitized_name) 
                       for stream, sanitized_name in streams.items()}

        buffer = {}
        buffer_size = 1000  # Adjust as needed

        for message in input_messages:
            if message.type == Type.STATE:
                self._flush_buffer(collections, buffer)
                yield message
            elif message.type == Type.RECORD:
                data = message.record.data
                stream = message.record.stream
                if stream not in streams:
                    logger.warning(f"Encountered new stream {stream}. Adding to streams and creating collection.")
                    sanitized_name = self._sanitize_collection_name(stream)
                    streams[stream] = sanitized_name
                    collections[stream] = self._setup_collection(cluster, bucket_name, scope_name, sanitized_name)
                
                if stream not in buffer:
                    buffer[stream] = []
                
                buffer[stream].append(self._prepare_document(stream, data))

                if len(buffer[stream]) >= buffer_size:
                    self._flush_buffer(collections, {stream: buffer[stream]})
                    buffer[stream] = []

        # Flush any remaining messages
        self._flush_buffer(collections, buffer)

    @staticmethod
    def _get_cluster(config: Mapping[str, Any]) -> Cluster:
        auth = PasswordAuthenticator(config["username"], config["password"])
        cluster = Cluster(config["connection_string"], ClusterOptions(auth))
        cluster.wait_until_ready(timedelta(seconds=5))
        return cluster

    @staticmethod
    def _sanitize_collection_name(name: str) -> str:
        # Replace invalid characters with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # Ensure the name starts with a letter
        if not sanitized[0].isalpha():
            sanitized = 'c_' + sanitized
        return sanitized

    @classmethod
    def _setup_collection(cls, cluster, bucket_name, scope_name, collection_name):
        try:
            bucket = cluster.bucket(bucket_name)
            bucket_manager = bucket.collections()
            
            # Check if collection exists, create if it doesn't
            collections = bucket_manager.get_all_scopes()
            collection_exists = any(
                scope.name == scope_name and collection_name in [col.name for col in scope.collections]
                for scope in collections
            )
            if not collection_exists:
                logger.info(f"Collection '{collection_name}' does not exist. Creating it...")
                bucket_manager.create_collection(scope_name, collection_name)
                logger.info(f"Collection '{collection_name}' created successfully.")
            else:
                logger.info(f"Collection '{collection_name}' already exists. Skipping creation.")
            collection = bucket.scope(scope_name).collection(collection_name)
            # Ensure primary index exists
            try:
                cluster.query(f"CREATE PRIMARY INDEX IF NOT EXISTS ON `{bucket_name}`.`{scope_name}`.`{collection_name}`").execute()
                logger.info("Primary index present or created successfully.")
            except Exception as e:
                logger.warning(f"Error creating primary index: {str(e)}")
            # Clear all documents in the collection
            try:
                query = f"DELETE FROM `{bucket_name}`.`{scope_name}`.`{collection_name}`"
                cluster.query(query).execute()
                logger.info("All documents cleared from the collection.")
            except Exception as e:
                logger.warning(f"Error while clearing documents: {str(e)}. The collection might be empty.")
            return collection
        except Exception as e:
            raise RuntimeError(f"Error setting up collection: {str(e)}")

    @staticmethod
    def _prepare_document(stream: str, data: Mapping[str, Any]) -> Mapping[str, Any]:
        return {
            "id": f"{stream}::{str(uuid4())}",
            "type": "airbyte_record",
            "stream": stream,
            "data": data
        }

    @staticmethod
    def _flush_buffer(collections, buffer: Mapping[str, list]):
        for stream, documents in buffer.items():
            if documents:
                collection = collections[stream]
                batch = {doc["id"]: doc for doc in documents}
                try:
                    # Set a longer timeout for the entire batch operation
                    timeout = timedelta(seconds=len(batch) * 2.5)  # 2.5 seconds per document
                    options = UpsertOptions(timeout=timeout)
                    
                    result = collection.upsert_multi(batch, options)
                    if not result.all_ok:
                        for doc_id, ex in result.exceptions.items():
                            if isinstance(ex, DocumentExistsException):
                                logger.warning(f"Document with ID '{doc_id}' already exists in the collection for stream {stream}")
                            else:
                                logger.error(f"Failed to upsert document '{doc_id}' for stream {stream}. Error: {ex}")
                    logger.info(f"Successfully loaded {len(batch)} documents for stream {stream}")
                except CouchbaseException as e:
                    logger.error(f"Error occurred while loading documents for stream {stream}: {e}")
                    logger.error(f"Full exception details: {repr(e)}")

        buffer.clear()  # Clear the buffer after flushing

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            cluster = self._get_cluster(config)
            bucket_name = config["bucket"]
            scope_name = config.get("scope", "_default")
            
            # Create a temporary collection
            temp_collection_name = f"airbyte_check_{uuid4().hex[:8]}"
            try:
                self._setup_collection(cluster, bucket_name, scope_name, temp_collection_name)
                logger.info(f"Successfully created and set up temporary collection: {temp_collection_name}")
                
                # Delete the temporary collection
                bucket = cluster.bucket(bucket_name)
                bucket.collections().drop_collection(scope_name, temp_collection_name)
                logger.info(f"Successfully deleted temporary collection: {temp_collection_name}")
                
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
            except Exception as e:
                return AirbyteConnectionStatus(status=Status.FAILED, message=f"Failed to create/delete temporary collection: {str(e)}")
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
