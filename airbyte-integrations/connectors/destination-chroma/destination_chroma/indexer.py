#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import List

import chromadb
from chromadb.config import Settings
from airbyte_cdk.destinations.vector_db_based.document_processor import METADATA_RECORD_ID_FIELD, METADATA_STREAM_FIELD, Chunk
from airbyte_cdk.destinations.vector_db_based.embedder import Embedder
from airbyte_cdk.destinations.vector_db_based.indexer import Indexer
from airbyte_cdk.destinations.vector_db_based.utils import format_exception
from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode

from destination_chroma.config import ChromaIndexingConfigModel
from .utils import convert_to_valid_collection_name


class ChromaIndexer(Indexer):
    def __init__(self, config: ChromaIndexingConfigModel, embedder: Embedder):
        super().__init__(config, embedder)
        self.client = self._get_client()

    def check(self):
        try:
            client = self.client
            client.heartbeat()
            return
        except Exception as e:
            return format_exception(e)

    def index(self, document_chunks: List[Chunk], delete_ids: List[str]) -> None:
        if len(delete_ids) > 0:
            self._delete_records(METADATA_RECORD_ID_FIELD, delete_ids)
        embedding_vectors = self.embedder.embed_texts([chunk.page_content for chunk in document_chunks])
        entities = []
        # TODO separate text, metadata and vectors ----- also get the stream name before writing
        for i in range(len(document_chunks)):
            chunk = document_chunks[i]
            entities.append({**chunk.metadata, self.config.vector_field: embedding_vectors[i], self.config.text_field: chunk.page_content})
        self._write_data(entities)

    def pre_sync(self, catalog: ConfiguredAirbyteCatalog) -> None:
        self._get_client()
        streams_to_overwrite = [stream 
                                for stream in catalog.streams 
                                if stream.destination_sync_mode == DestinationSyncMode.overwrite]
        # TODO delete for each stream
        self._delete_records(METADATA_STREAM_FIELD, streams_to_overwrite)

    @staticmethod
    def _get_client(self):

        auth_method = self.config.auth_method
        if auth_method.mode == 'persistent_client':
            path = auth_method.path
            client = chromadb.PersistentClient(path=path)
            return client

        elif auth_method.mode == 'http_client':
            host = auth_method.host
            port = auth_method.port
            username = auth_method.username
            password = auth_method.password

            settings = Settings(chroma_client_auth_provider="chromadb.auth.basic.BasicAuthClientProvider", 
                                chroma_client_auth_credentials=f"{username}:{password}")

            client = chromadb.HttpClient(settings=settings, host=host, port=port)
            return client
        return
    
    def _delete_records(self, field_name, field_values):
        where_dict_list = [{field_name:value} for value in field_values]
        collection_name: str
        collection = self.client.get_collection(collection_name)
        try:
            for where_dict in where_dict_list:
                collection.delete(where=where_dict)
        except ValueError as e:
            raise e

    def _write_data(self, entities):
        record_id = self.get_record_id(record=record)
        embedding = self.get_embedding(record=record)
        record = self.prepare_record(record=record)
        collection_name = convert_to_valid_collection_name()

        collection = self.client.get_collection(name=collection_name)
        collection.add(
            embeddings=embedding,
            documents=[record], # TODO get specific records to add
            ids=[record_id],
            metadata=None # TODO add support for metadata
        )
