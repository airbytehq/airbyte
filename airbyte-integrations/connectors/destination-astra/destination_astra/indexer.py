#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import uuid
from typing import Optional

import urllib3
from airbyte_cdk.destinations.vector_db_based.document_processor import METADATA_RECORD_ID_FIELD, METADATA_STREAM_FIELD
from airbyte_cdk.destinations.vector_db_based.indexer import Indexer
from airbyte_cdk.destinations.vector_db_based.utils import create_chunks, create_stream_identifier, format_exception
from airbyte_cdk.models.airbyte_protocol import ConfiguredAirbyteCatalog, DestinationSyncMode
from destination_astra.astra_client import AstraClient
from destination_astra.config import AstraIndexingModel

# do not flood the server with too many connections in parallel
PARALLELISM_LIMIT = 20

MAX_METADATA_SIZE = 40_960 - 10_000

MAX_IDS_PER_DELETE = 1000


class AstraIndexer(Indexer):
    config: AstraIndexingModel

    def __init__(self, config: AstraIndexingModel, embedding_dimensions: int):
        super().__init__(config)

        self.client = AstraClient(
            config.astra_db_endpoint, config.astra_db_app_token, config.astra_db_keyspace, embedding_dimensions, "cosine"
        )

        self.embedding_dimensions = embedding_dimensions

    def _create_collection(self):
        if self.client.find_collection(self.config.collection) is False:
            self.client.create_collection(self.config.collection)

    def pre_sync(self, catalog: ConfiguredAirbyteCatalog):
        self._create_collection()
        for stream in catalog.streams:
            if stream.destination_sync_mode == DestinationSyncMode.overwrite:
                self.client.delete_documents(
                    collection_name=self.config.collection, filter={METADATA_STREAM_FIELD: create_stream_identifier(stream.stream)}
                )

    def index(self, document_chunks, namespace, stream):
        docs = []
        for i in range(len(document_chunks)):
            chunk = document_chunks[i]
            metadata = chunk.metadata
            if chunk.page_content is not None:
                metadata["text"] = chunk.page_content
            doc = {
                "_id": str(uuid.uuid4()),
                "$vector": chunk.embedding,
                **metadata,
            }
            docs.append(doc)
        serial_batches = create_chunks(docs, batch_size=PARALLELISM_LIMIT)

        for batch in serial_batches:
            results = [chunk for chunk in batch]
            self.client.insert_documents(collection_name=self.config.collection, documents=results)

    def delete(self, delete_ids, namespace, stream):
        if len(delete_ids) > 0:
            self.client.delete_documents(collection_name=self.config.collection, filter={METADATA_RECORD_ID_FIELD: {"$in": delete_ids}})

    def check(self) -> Optional[str]:
        try:
            self._create_collection()
            collections = self.client.find_collections()
            collection = next(filter(lambda f: f["name"] == self.config.collection, collections), None)
            if collection is None:
                return f"{self.config.collection} collection does not exist."

            actual_dimension = collection["options"]["vector"]["dimension"]
            if actual_dimension != self.embedding_dimensions:
                return f"Your embedding configuration will produce vectors with dimension {self.embedding_dimensions:d}, but your collection is configured with dimension {actual_dimension:d}. Make sure embedding and indexing configurations match."
        except Exception as e:
            if isinstance(e, urllib3.exceptions.MaxRetryError):
                if "Failed to resolve 'apps.astra.datastax.com'" in str(e.reason):
                    return "Failed to resolve environment, please check whether the credential is correct."
            if isinstance(e, urllib3.exceptions.HTTPError):
                return str(e)

            formatted_exception = format_exception(e)
            return formatted_exception
        return None
