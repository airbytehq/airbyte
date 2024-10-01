#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import uuid
from typing import List, Optional

from airbyte_cdk.destinations.vector_db_based.document_processor import METADATA_RECORD_ID_FIELD, METADATA_STREAM_FIELD
from airbyte_cdk.destinations.vector_db_based.indexer import Indexer
from airbyte_cdk.destinations.vector_db_based.utils import create_stream_identifier, format_exception
from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, ConfiguredAirbyteCatalog, Level, Type
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode
from destination_qdrant.config import QdrantIndexingConfigModel
from qdrant_client import QdrantClient, models
from qdrant_client.conversions.common_types import PointsSelector
from qdrant_client.models import Distance, PayloadSchemaType, VectorParams

DISTANCE_METRIC_MAP = {
    "dot": Distance.DOT,
    "cos": Distance.COSINE,
    "euc": Distance.EUCLID,
}


class QdrantIndexer(Indexer):
    config: QdrantIndexingConfigModel

    def __init__(self, config: QdrantIndexingConfigModel, embedding_dimensions: int):
        super().__init__(config)
        self.embedding_dimensions = embedding_dimensions

    def check(self) -> Optional[str]:
        auth_method_mode = self.config.auth_method.mode
        if auth_method_mode == "api_key_auth" and not self.config.url.startswith("https://"):
            return "Host must start with https://"

        try:
            self._create_client()

            if not self._client:
                return "Qdrant client is not alive."

            available_collections = [collection.name for collection in self._client.get_collections().collections]
            distance_metric = DISTANCE_METRIC_MAP[self.config.distance_metric]

            if self.config.collection in available_collections:
                collection_info = self._client.get_collection(collection_name=self.config.collection)
                assert (
                    collection_info.config.params.vectors.size == self.embedding_dimensions
                ), "The collection's vector's size must match the embedding dimensions"
                assert (
                    collection_info.config.params.vectors.distance == distance_metric
                ), "The colection's vector's distance metric must match the selected distance metric option"
            else:
                self._client.recreate_collection(
                    collection_name=self.config.collection,
                    vectors_config=VectorParams(size=self.embedding_dimensions, distance=distance_metric),
                )

        except Exception as e:
            return format_exception(e)
        finally:
            if self._client:
                self._client.close()

    def pre_sync(self, catalog: ConfiguredAirbyteCatalog) -> None:
        self._create_client()
        streams_to_overwrite = [
            create_stream_identifier(stream.stream)
            for stream in catalog.streams
            if stream.destination_sync_mode == DestinationSyncMode.overwrite
        ]
        if streams_to_overwrite:
            self._delete_for_filter(
                models.FilterSelector(
                    filter=models.Filter(
                        should=[
                            models.FieldCondition(key=METADATA_STREAM_FIELD, match=models.MatchValue(value=stream))
                            for stream in streams_to_overwrite
                        ]
                    )
                )
            )
        for field in [METADATA_RECORD_ID_FIELD, METADATA_STREAM_FIELD]:
            self._client.create_payload_index(
                collection_name=self.config.collection, field_name=field, field_schema=PayloadSchemaType.KEYWORD
            )

    def delete(self, delete_ids, namespace, stream):
        if len(delete_ids) > 0:
            self._delete_for_filter(
                models.FilterSelector(
                    filter=models.Filter(
                        should=[
                            models.FieldCondition(key=METADATA_RECORD_ID_FIELD, match=models.MatchValue(value=_id)) for _id in delete_ids
                        ]
                    )
                )
            )

    def index(self, document_chunks, namespace, stream):
        entities = []
        for i in range(len(document_chunks)):
            chunk = document_chunks[i]
            payload = chunk.metadata
            if chunk.page_content is not None:
                payload[self.config.text_field] = chunk.page_content
            entities.append(
                models.Record(
                    id=str(uuid.uuid4()),
                    payload=payload,
                    vector=chunk.embedding,
                )
            )
        self._client.upload_records(collection_name=self.config.collection, records=entities)

    def post_sync(self) -> List[AirbyteMessage]:
        try:
            self._client.close()
            return [
                AirbyteMessage(
                    type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message="Qdrant Database Client has been closed successfully")
                )
            ]
        except Exception as e:
            return [AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.ERROR, message=format_exception(e)))]

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
        self._client.delete(collection_name=self.config.collection, points_selector=selector)
