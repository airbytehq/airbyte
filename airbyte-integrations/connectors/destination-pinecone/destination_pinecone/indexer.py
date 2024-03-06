#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import uuid
from typing import Optional

import pinecone
import urllib3
from airbyte_cdk.destinations.vector_db_based.document_processor import METADATA_RECORD_ID_FIELD, METADATA_STREAM_FIELD
from airbyte_cdk.destinations.vector_db_based.indexer import Indexer
from airbyte_cdk.destinations.vector_db_based.utils import create_chunks, create_stream_identifier, format_exception
from airbyte_cdk.models.airbyte_protocol import ConfiguredAirbyteCatalog, DestinationSyncMode
from destination_pinecone.config import PineconeIndexingModel

# large enough to speed up processing, small enough to not hit pinecone request limits
PINECONE_BATCH_SIZE = 40

# do not flood the server with too many connections in parallel
PARALLELISM_LIMIT = 4

MAX_METADATA_SIZE = 40_960 - 10_000

MAX_IDS_PER_DELETE = 1000


class PineconeIndexer(Indexer):
    config: PineconeIndexingModel

    def __init__(self, config: PineconeIndexingModel, embedding_dimensions: int):
        super().__init__(config)
        pinecone.init(api_key=config.pinecone_key, environment=config.pinecone_environment, threaded=True)

        self.pinecone_index = pinecone.GRPCIndex(config.index)
        self.embedding_dimensions = embedding_dimensions

    def pre_sync(self, catalog: ConfiguredAirbyteCatalog):
        index_description = pinecone.describe_index(self.config.index)
        self._pod_type = index_description.pod_type
        for stream in catalog.streams:
            if stream.destination_sync_mode == DestinationSyncMode.overwrite:
                self.delete_vectors(
                    filter={METADATA_STREAM_FIELD: create_stream_identifier(stream.stream)}, namespace=stream.stream.namespace
                )

    def post_sync(self):
        return []

    def delete_vectors(self, filter, namespace=None):
        if self._pod_type == "starter":
            # Starter pod types have a maximum of 100000 rows
            top_k = 10000
            self.delete_by_metadata(filter, top_k, namespace)
        else:
            self.pinecone_index.delete(filter=filter, namespace=namespace)

    def delete_by_metadata(self, filter, top_k, namespace=None):
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

    def index(self, document_chunks, namespace, stream):
        pinecone_docs = []
        for i in range(len(document_chunks)):
            chunk = document_chunks[i]
            metadata = self._truncate_metadata(chunk.metadata)
            if chunk.page_content is not None:
                metadata["text"] = chunk.page_content
            pinecone_docs.append((str(uuid.uuid4()), chunk.embedding, metadata))
        serial_batches = create_chunks(pinecone_docs, batch_size=PINECONE_BATCH_SIZE * PARALLELISM_LIMIT)
        for batch in serial_batches:
            async_results = [
                self.pinecone_index.upsert(vectors=ids_vectors_chunk, async_req=True, show_progress=False, namespace=namespace)
                for ids_vectors_chunk in create_chunks(batch, batch_size=PINECONE_BATCH_SIZE)
            ]
            # Wait for and retrieve responses (this raises in case of error)
            [async_result.result() for async_result in async_results]

    def delete(self, delete_ids, namespace, stream):
        if len(delete_ids) > 0:
            self.delete_vectors(filter={METADATA_RECORD_ID_FIELD: {"$in": delete_ids}}, namespace=namespace)

    def check(self) -> Optional[str]:
        try:
            indexes = pinecone.list_indexes()
            if self.config.index not in indexes:
                return f"Index {self.config.index} does not exist in environment {self.config.pinecone_environment}."

            description = pinecone.describe_index(self.config.index)
            actual_dimension = int(description.dimension)
            if actual_dimension != self.embedding_dimensions:
                return f"Your embedding configuration will produce vectors with dimension {self.embedding_dimensions:d}, but your index is configured with dimension {actual_dimension:d}. Make sure embedding and indexing configurations match."
        except Exception as e:
            if isinstance(e, urllib3.exceptions.MaxRetryError):
                if f"Failed to resolve 'controller.{self.config.pinecone_environment}.pinecone.io'" in str(e.reason):
                    return f"Failed to resolve environment, please check whether {self.config.pinecone_environment} is correct."

            if isinstance(e, pinecone.exceptions.UnauthorizedException):
                if e.body:
                    return e.body

            formatted_exception = format_exception(e)
            return formatted_exception
        return None
