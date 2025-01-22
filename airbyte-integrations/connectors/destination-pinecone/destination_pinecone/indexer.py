#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
import uuid
from typing import Optional

import urllib3
from pinecone import PineconeException
from pinecone.grpc import PineconeGRPC

from airbyte_cdk.destinations.vector_db_based.document_processor import METADATA_RECORD_ID_FIELD, METADATA_STREAM_FIELD
from airbyte_cdk.destinations.vector_db_based.indexer import Indexer
from airbyte_cdk.destinations.vector_db_based.utils import create_chunks, create_stream_identifier, format_exception
from airbyte_cdk.models import AirbyteConnectionStatus, Status
from airbyte_cdk.models.airbyte_protocol import ConfiguredAirbyteCatalog, DestinationSyncMode
from destination_pinecone.config import PineconeIndexingModel


# large enough to speed up processing, small enough to not hit pinecone request limits
PINECONE_BATCH_SIZE = 40

# do not flood the server with too many connections in parallel
PARALLELISM_LIMIT = 4

MAX_METADATA_SIZE = 40_960 - 10_000

MAX_IDS_PER_DELETE = 1000

AIRBYTE_TAG = "airbyte"
AIRBYTE_TEST_TAG = "airbyte_test"


class PineconeIndexer(Indexer):
    config: PineconeIndexingModel

    def __init__(self, config: PineconeIndexingModel, embedding_dimensions: int):
        super().__init__(config)
        try:
            self.pc = PineconeGRPC(api_key=config.pinecone_key, source_tag=self.get_source_tag, threaded=True)
        except PineconeException as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=str(e))

        self.pinecone_index = self.pc.Index(config.index)
        self.embedding_dimensions = embedding_dimensions

    def determine_spec_type(self, index_name):
        description = self.pc.describe_index(index_name)
        spec_keys = description.get("spec", {})
        if "pod" in spec_keys:
            return "pod"
        elif "serverless" in spec_keys:
            return "serverless"
        else:
            raise ValueError("Unknown index specification type.")

    def pre_sync(self, catalog: ConfiguredAirbyteCatalog):
        self._pod_type = self.determine_spec_type(self.config.index)

        for stream in catalog.streams:
            stream_identifier = create_stream_identifier(stream.stream)
            if stream.destination_sync_mode == DestinationSyncMode.overwrite:
                self.delete_vectors(
                    filter={METADATA_STREAM_FIELD: stream_identifier}, namespace=stream.stream.namespace, prefix=stream_identifier
                )

    def post_sync(self):
        return []

    def get_source_tag(self):
        is_test = "PYTEST_CURRENT_TEST" in os.environ or "RUN_IN_AIRBYTE_CI" in os.environ
        return AIRBYTE_TEST_TAG if is_test else AIRBYTE_TAG

    def delete_vectors(self, filter, namespace=None, prefix=None):
        if self._pod_type == "starter":
            # Starter pod types have a maximum of 100000 rows
            top_k = 10000
            self.delete_by_metadata(filter, top_k, namespace)
        elif self._pod_type == "serverless":
            if prefix == None:
                raise ValueError("Prefix is required for a serverless index.")
            self.delete_by_prefix(prefix=prefix, namespace=namespace)
        else:
            # Pod spec
            self.pinecone_index.delete(filter=filter, namespace=namespace)

    def delete_by_metadata(self, filter, top_k, namespace=None):
        """
        Applicable to Starter implementation only. Deletes all vectors that match the given metadata filter.
        """
        zero_vector = [0.0] * self.embedding_dimensions
        query_result = self.pinecone_index.query(vector=zero_vector, filter=filter, top_k=top_k, namespace=namespace)
        while len(query_result.matches) > 0:
            vector_ids = [doc.id for doc in query_result.matches]
            if len(vector_ids) > 0:
                # split into chunks of 1000 ids to avoid id limit
                batches = create_chunks(vector_ids, batch_size=MAX_IDS_PER_DELETE)
                for batch in batches:
                    self.pinecone_index.delete(ids=list(batch), namespace=namespace)
            query_result = self.pinecone_index.query(vector=zero_vector, filter=filter, top_k=top_k, namespace=namespace)

    def delete_by_prefix(self, prefix, namespace=None):
        """
        Applicable to Serverless implementation only. Deletes all vectors with the given prefix.
        """
        for ids in self.pinecone_index.list(prefix=prefix, namespace=namespace):
            self.pinecone_index.delete(ids=ids, namespace=namespace)

    def _truncate_metadata(self, metadata: dict) -> dict:
        """
        Normalize metadata to ensure it is within the size limit and doesn't contain complex objects.
        """
        result = {}
        current_size = 0

        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)) or (isinstance(value, list) and all(isinstance(item, str) for item in value)):
                # Calculate the size of the key and value
                item_size = len(str(key)) + len(str(value))

                # Check if adding the item exceeds the size limit
                if current_size + item_size <= MAX_METADATA_SIZE:
                    result[key] = value
                    current_size += item_size

        return result

    def index(self, document_chunks, namespace, streamName):
        pinecone_docs = []
        for i in range(len(document_chunks)):
            chunk = document_chunks[i]
            metadata = self._truncate_metadata(chunk.metadata)
            if chunk.page_content is not None:
                metadata["text"] = chunk.page_content
            prefix = streamName
            pinecone_docs.append((prefix + "#" + str(uuid.uuid4()), chunk.embedding, metadata))
        serial_batches = create_chunks(pinecone_docs, batch_size=PINECONE_BATCH_SIZE * PARALLELISM_LIMIT)
        for batch in serial_batches:
            async_results = []
            for ids_vectors_chunk in create_chunks(batch, batch_size=PINECONE_BATCH_SIZE):
                async_result = self.pinecone_index.upsert(
                    vectors=ids_vectors_chunk, async_req=True, show_progress=False, namespace=namespace
                )
                async_results.append(async_result)
            # Wait for and retrieve responses (this raises in case of error)
            [async_result.result() for async_result in async_results]

    def delete(self, delete_ids, namespace, stream):
        filter = {METADATA_RECORD_ID_FIELD: {"$in": delete_ids}}
        if len(delete_ids) > 0:
            if self._pod_type == "starter":
                # Starter pod types have a maximum of 100000 rows
                top_k = 10000
                self.delete_by_metadata(filter=filter, top_k=top_k, namespace=namespace)
            elif self._pod_type == "serverless":
                self.pinecone_index.delete(ids=delete_ids, namespace=namespace)
            else:
                # Pod spec
                self.pinecone_index.delete(filter=filter, namespace=namespace)

    def check(self) -> Optional[str]:
        try:
            list = self.pc.list_indexes()
            index_names = [index["name"] for index in list.indexes]
            if self.config.index not in index_names:
                return f"Index {self.config.index} does not exist in environment {self.config.pinecone_environment}."

            description = self.pc.describe_index(self.config.index)
            actual_dimension = int(description.dimension)
            if actual_dimension != self.embedding_dimensions:
                return f"Your embedding configuration will produce vectors with dimension {self.embedding_dimensions:d}, but your index is configured with dimension {actual_dimension:d}. Make sure embedding and indexing configurations match."
        except Exception as e:
            if isinstance(e, urllib3.exceptions.MaxRetryError):
                if f"Failed to resolve 'controller.{self.config.pinecone_environment}.pinecone.io'" in str(e.reason):
                    return f"Failed to resolve environment, please check whether {self.config.pinecone_environment} is correct."

            if isinstance(e, PineconeException):
                if e.body:
                    return e.body

            formatted_exception = format_exception(e)
            return formatted_exception
        return None
