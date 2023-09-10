#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import uuid
from typing import List

import chromadb
from chromadb.config import Settings

from airbyte_cdk.destinations.vector_db_based.document_processor import METADATA_RECORD_ID_FIELD, METADATA_STREAM_FIELD, Chunk
from airbyte_cdk.destinations.vector_db_based.indexer import Indexer
from airbyte_cdk.destinations.vector_db_based.utils import format_exception
from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode

from destination_chroma.config import ChromaIndexingConfigModel
from destination_chroma.utils import validate_collection_name



class ChromaIndexer(Indexer):
    def __init__(self, config: ChromaIndexingConfigModel):
        super().__init__(config)
        self.collection_name = validate_collection_name(config.collection_name)

    def check(self):
        client = self._get_client()
        try:
            heartbeat = client.heartbeat()
            if not heartbeat:
                return "Chroma client server is not alive"
            collection = client.get_or_create_collection(name=self.collection_name) 
            count = collection.count()
            if count!=0 and not count:
                return f"unable to get or create collection with name {self.collection_name}"
            return
        except Exception as e:
            return format_exception(e)
        finally:
            del client

    def index(self, document_chunks: List[Chunk], delete_ids: List[str]) -> None:
        if len(delete_ids) > 0:
            self._delete_by_filter(field_name=METADATA_RECORD_ID_FIELD, field_values=delete_ids)
        entities = []
        for i in range(len(document_chunks)):
            chunk = document_chunks[i]
            entities.append({'id': str(uuid.uuid4()),
                             'embedding': chunk.embedding, 
                             'metadata': chunk.metadata,
                             'document': chunk.page_content})
        self._write_data(entities)

    def pre_sync(self, catalog: ConfiguredAirbyteCatalog) -> None:
        self.client = self._get_client()
        streams_to_overwrite = [stream.stream.name 
                                for stream in catalog.streams 
                                if stream.destination_sync_mode == DestinationSyncMode.overwrite]
        if streams_to_overwrite:
            self._delete_by_filter(field_name=METADATA_STREAM_FIELD, field_values=streams_to_overwrite)

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
    
    def _delete_by_filter(self, field_name, field_values):
        collection = self.client.get_collection(name=self.collection_name)
        try:
            where_filter = {
                field_name: {
                    "$in": field_values
                }
            }
            collection.delete(where=where_filter)
        except ValueError as e:
            raise e

    def _write_data(self, entities):
        ids = [entity['id'] for entity in entities]
        embeddings = [entity['embedding'] for entity in entities]
        if not any(embeddings):
            embeddings=None
        metadata = [entity['metadata'] for entity in entities]
        documents = [entity['document'] for entity in entities]

        collection = self.client.get_collection(name=self.collection_name)
        collection.add(
            ids=ids,
            embeddings=embeddings,
            metadata=metadata,
            documents=documents
        )
