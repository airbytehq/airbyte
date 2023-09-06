#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import itertools
import uuid
from typing import Optional

import pinecone
from airbyte_cdk.destinations.vector_db_based.document_processor import METADATA_RECORD_ID_FIELD, METADATA_STREAM_FIELD
from airbyte_cdk.destinations.vector_db_based.indexer import Indexer
from airbyte_cdk.destinations.vector_db_based.utils import format_exception
from airbyte_cdk.models.airbyte_protocol import ConfiguredAirbyteCatalog, DestinationSyncMode
from destination_pinecone.config import PineconeIndexingModel


def chunks(iterable, batch_size):
    """A helper function to break an iterable into chunks of size batch_size."""
    it = iter(iterable)
    chunk = tuple(itertools.islice(it, batch_size))
    while chunk:
        yield chunk
        chunk = tuple(itertools.islice(it, batch_size))


# large enough to speed up processing, small enough to not hit pinecone request limits
PINECONE_BATCH_SIZE = 40

MAX_METADATA_SIZE = 40_960 - 10_000


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
                self.delete_vectors(filter={METADATA_STREAM_FIELD: stream.stream.name})

    def post_sync(self):
        return []

    def delete_vectors(self, filter):
        if self._pod_type == "starter":
            # Starter pod types have a maximum of 100000 rows
            top_k = 10000
            self.delete_by_metadata(filter, top_k)
        else:
            self.pinecone_index.delete(filter=filter)

    def delete_by_metadata(self, filter, top_k):
        zero_vector = [0.0] * self.embedding_dimensions
        query_result = self.pinecone_index.query(vector=zero_vector, filter=filter, top_k=top_k)
        vector_ids = [doc.id for doc in query_result.matches]
        if len(vector_ids) > 0:
            self.pinecone_index.delete(ids=vector_ids)

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

    def index(self, document_chunks, delete_ids):
        if len(delete_ids) > 0:
            self.delete_vectors(filter={METADATA_RECORD_ID_FIELD: {"$in": delete_ids}})
        pinecone_docs = []
        for i in range(len(document_chunks)):
            chunk = document_chunks[i]
            metadata = self._truncate_metadata(chunk.metadata)
            metadata["text"] = chunk.page_content
            pinecone_docs.append((str(uuid.uuid4()), chunk.embedding, metadata))
        async_results = [
            self.pinecone_index.upsert(vectors=ids_vectors_chunk, async_req=True, show_progress=False)
            for ids_vectors_chunk in chunks(pinecone_docs, batch_size=PINECONE_BATCH_SIZE)
        ]
        # Wait for and retrieve responses (this raises in case of error)
        [async_result.result() for async_result in async_results]

    def check(self) -> Optional[str]:
        try:
            description = pinecone.describe_index(self.config.index)
            actual_dimension = int(description.dimension)
            if actual_dimension != self.embedding_dimensions:
                return f"Your embedding configuration will produce vectors with dimension {self.embedding_dimensions:d}, but your index is configured with dimension {actual_dimension:d}. Make sure embedding and indexing configurations match."
        except Exception as e:
            return format_exception(e)
        return None
