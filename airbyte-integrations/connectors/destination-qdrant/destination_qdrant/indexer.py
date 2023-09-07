#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#



import uuid
from typing import List, Optional

from airbyte_cdk.destinations.vector_db_based.document_processor import (
    METADATA_RECORD_ID_FIELD,
    METADATA_STREAM_FIELD,
    Chunk
)
from airbyte_cdk.destinations.vector_db_based.embedder import Embedder
from airbyte_cdk.destinations.vector_db_based.indexer import Indexer
from airbyte_cdk.destinations.vector_db_based.utils import format_exception
from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode

from qdrant_client import QdrantClient, models
from qdrant_client.conversions.common_types import PointsSelector

from destination_qdrant.config import QdrantIndexingConfigModel



class QdrantIndexer(Indexer):
    config: QdrantIndexingConfigModel

    def __init__(self, config: QdrantIndexingConfigModel, embedder: Embedder):
        super().__init__(config, embedder)

    def _create_client(self):
        self._client = QdrantClient(self.config.host, prefer_grpc=self.config.prefer_grpc, api_key=self.config.token)

        self._collection = self._client.get_collection(self.config.collection)

    def check(self) -> Optional[str]:
        try:
            self._create_client()
            # TODO - do some checks
        except Exception as e:
            return format_exception(e)
        return None

    def pre_sync(self, catalog: ConfiguredAirbyteCatalog) -> None:
        self._create_client()
        for stream in catalog.streams:
            if stream.destination_sync_mode == DestinationSyncMode.overwrite:
                self._delete_for_filter(
                    models.FilterSelector(
                        filter=models.Filter(
                            must=[models.FieldCondition(key=METADATA_STREAM_FIELD, match=models.MatchValue(value=stream.stream.name))]
                        )
                    )
                )

    def _delete_for_filter(self, selector: PointsSelector) -> None:
        self._client.delete(collection_name=self.config.collection, points_selector=selector)

    def index(self, document_chunks: List[Chunk], delete_ids: List[str]) -> None:
        if len(delete_ids) > 0:
            self._delete_for_filter(
                models.FilterSelector(
                    filter=models.Filter(
                        should=[models.FieldCondition(key=METADATA_RECORD_ID_FIELD, match=models.MatchValue(value=id)) for id in delete_ids]
                    )
                )
            )
        embedding_vectors = self.embedder.embed_texts([chunk.page_content for chunk in document_chunks])
        entities = []
        for i in range(len(document_chunks)):
            chunk = document_chunks[i]
            metadata = chunk.metadata
            metadata["text"] = chunk.page_content
            entities.append(
                models.Record(
                    id=str(uuid.uuid4()),
                    payload={**chunk.metadata, self.config.text_field: chunk.page_content},
                    vector=embedding_vectors[i],
                )
            )
        self._client.upload_records(collection_name=self.config.collection, records=entities)

