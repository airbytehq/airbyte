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
from airbyte_cdk.destinations.vector_db_based.indexer import Indexer
from airbyte_cdk.destinations.vector_db_based.utils import format_exception
from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog, Type, AirbyteLogMessage, Level
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode
from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams
from qdrant_client.conversions.common_types import PointsSelector

from destination_qdrant.config import QdrantIndexingConfigModel, DistanceMetricEnum



DISTANCE_METRIC_MAP = {
    DistanceMetricEnum.dot: Distance.DOT,
    DistanceMetricEnum.cos: Distance.COSINE,
    DistanceMetricEnum.euc: Distance.EUCLID
}

class QdrantIndexer(Indexer):
    config: QdrantIndexingConfigModel

    def __init__(self, config: QdrantIndexingConfigModel, embedding_dimensions: int):
        super().__init__(config)
        self.embedding_dimensions = embedding_dimensions

    def check(self) -> Optional[str]:
        try:
            self._create_client()
            if not self._client.get_collections():
                return "Qdrant client is not alive."
            try:
                self._client.get_collection(collection_name=self.config.collection)
            except ValueError:
                distance_metric = DISTANCE_METRIC_MAP[self.config.distance_metric]
                self._client.recreate_collection(
                    collection_name=self.config.collection,
                    vectors_config=VectorParams(size=self.embedding_dimensions, distance=distance_metric),
                )
        except Exception as e:
            return format_exception(e)
        finally:
            self._client.close()

    def pre_sync(self, catalog: ConfiguredAirbyteCatalog) -> None:
        self._create_client()
        streams_to_overwrite = [
            stream.stream.name for stream in catalog.streams if stream.destination_sync_mode == DestinationSyncMode.overwrite
        ]
        if streams_to_overwrite:
            self._delete_for_filter(
                models.FilterSelector(
                    filter=models.Filter(
                        should=[models.FieldCondition(key=METADATA_STREAM_FIELD, match=models.MatchValue(value=stream)) for stream in streams_to_overwrite]
                    )
                )
            )

    def index(self, document_chunks: List[Chunk], delete_ids: List[str]) -> None:
        if len(delete_ids) > 0:
            self._delete_for_filter(
                models.FilterSelector(
                    filter=models.Filter(
                        should=[models.FieldCondition(key=METADATA_RECORD_ID_FIELD, match=models.MatchValue(value=_id)) for _id in delete_ids]
                    )
                )
            )
        entities = []
        for i in range(len(document_chunks)):
            chunk = document_chunks[i]
            payload = chunk.metadata
            payload[self.config.text_field] = chunk.page_content
            entities.append(
                models.Record(
                    id=str(uuid.uuid4()),
                    payload=payload,
                    vector=chunk.embedding,
                )
            )
        self._client.upload_records(collection_name=self.config.collection, records=entities, parallel=10)

    def post_sync(self) -> List[AirbyteMessage]:
        try:
            self._client.close()
            return AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message="Qdrant Database Client has been closed successfully"))
        except Exception as e:
            return AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.ERROR, message=format_exception(e))) 

    def _create_client(self):
        auth_method = self.config.auth_method
        url = self.config.url
        prefer_grpc = self.config.prefer_grpc

        if auth_method.mode == "no_auth":
            self._client = QdrantClient(url=url, prefer_grpc=prefer_grpc)
        elif auth_method.mode == "api_key_auth":
            api_key = auth_method.api_key
            self._client = QdrantClient(url=url, prefer_grpc=prefer_grpc, api_key=api_key)

    def _delete_for_filter(self, selector: PointsSelector) -> None:
        self._client.delete(
            collection_name=self.config.collection, 
            points_selector=selector
            )
