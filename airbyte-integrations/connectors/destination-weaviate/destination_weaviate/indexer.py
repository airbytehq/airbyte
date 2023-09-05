#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from dataclasses import dataclass
import json
import time
import os
from typing import Any, List, Mapping, MutableMapping, Optional
import uuid
import logging


from airbyte_cdk.destinations.vector_db_based.document_processor import METADATA_RECORD_ID_FIELD, METADATA_STREAM_FIELD, Chunk
from airbyte_cdk.destinations.vector_db_based.embedder import Embedder
from airbyte_cdk.destinations.vector_db_based.indexer import Indexer
from airbyte_cdk.destinations.vector_db_based.utils import format_exception
from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode
from destination_weaviate.config import WeaviateIndexingConfigModel

import weaviate

class WeaviatePartialBatchError(Exception):
    pass


CLOUD_DEPLOYMENT_MODE = "cloud"

@dataclass
class BufferedObject:
    id: str
    properties: Mapping[str, Any]
    vector: Optional[List[Any]]
    class_name: str

class WeaviateIndexer(Indexer):
    config: WeaviateIndexingConfigModel

    def __init__(self, config: WeaviateIndexingConfigModel):
        super().__init__(config)
        self.buffered_objects: MutableMapping[str, BufferedObject] = {}
        self.objects_with_error: MutableMapping[str, BufferedObject] = {}

    def _create_client(self):
        if self.config.auth.mode == "username_password":
            credentials = weaviate.auth.AuthClientPassword(self.config.auth.username, self.config.auth.password)
            self.client = weaviate.Client(url=self.config.host, auth_client_secret=credentials)
        elif self.config.auth.mode == "token":
            credentials = weaviate.auth.AuthApiKey(self.config.auth.token)
            self.client = weaviate.Client(url=self.config.host, auth_client_secret=credentials)
        else:
            self.client = weaviate.Client(url=self.config.host)
        
        schema = self.client.schema.get(self.config.class_name)
        self.has_stream_metadata = any(prop.get("name") == METADATA_STREAM_FIELD  for prop in schema.get("properties", {}))
        self.has_record_id_metadata = any(prop.get("name") == METADATA_RECORD_ID_FIELD  for prop in schema.get("properties", {}))

    def check(self) -> Optional[str]:
        deployment_mode = os.environ.get("DEPLOYMENT_MODE", "")
        if deployment_mode.casefold() == CLOUD_DEPLOYMENT_MODE and not self._uses_https():
            return "Host must start with https://"
        try:
            self._create_client()

            # TODO validate collection is set up correctly. Embedding dimensions of -1 means that the cluster will take care of embedding

        except Exception as e:
            return format_exception(e)
        return None

    def _uses_https(self) -> bool:
        return self.config.host.startswith("https://")

    def pre_sync(self, catalog: ConfiguredAirbyteCatalog) -> None:
        self._create_client()
        for stream in catalog.streams:
            # if stream metadata is not set, this means the field is not created yet and we can skip deleting
            if stream.destination_sync_mode == DestinationSyncMode.overwrite and self.has_stream_metadata:
                self._delete_for_filter({"path": [METADATA_STREAM_FIELD], "operator": "Equal", "valueText": stream.stream.name})
    
    def _has_ab_metadata(self) -> bool:
        self.schema.get("properties")

    def _delete_for_filter(self, expr: dict) -> None:
        self.client.batch.delete_objects(class_name=self.config.class_name, where=expr)

    def index(self, document_chunks: List[Chunk], delete_ids: List[str]) -> None:
        # if record id metadata is not set, this means the field is not created yet and we can skip deleting
        if len(delete_ids) > 0 and self.has_record_id_metadata:
            self._delete_for_filter({
                "path": [METADATA_RECORD_ID_FIELD],
                "operator": "ContainsAny",
                "valueStringArray": delete_ids
            })
        for i in range(len(document_chunks)):
            chunk = document_chunks[i]
            weaviate_object = {**self._normalize(chunk.metadata), self.config.text_field: chunk.page_content}
            object_id = uuid.uuid4()
            self.client.batch.add_data_object(weaviate_object, self.config.class_name, object_id, vector=chunk.embedding)
            self.buffered_objects[object_id] = BufferedObject(object_id, weaviate_object, chunk.embedding, self.config.class_name)
        self.flush()
    
    def _normalize(self, metadata: dict) -> dict:
        result = {}

        for key, value in metadata.items():
            # Property names in Weaviate have to start with lowercase letter
            normalized_key = key[0].lower() + key[1:]
            if isinstance(value, list) and len(value) == 0:
                # Handling of empty list that's not part of defined schema otherwise Weaviate throws invalid string property
                continue
            if isinstance(value, (str, int, float, bool)) or (isinstance(value, list) and all(isinstance(item, str) for item in value)):
                result[normalized_key] = value
            else:
                # JSON encode all other types
                result[normalized_key] = json.dumps(value)

        return result


    def flush(self, retries: int = 3):
        if len(self.objects_with_error) > 0 and retries == 0:
            error_msg = f"Objects had errors and retries failed as well. Object IDs: {self.objects_with_error.keys()}"
            raise WeaviatePartialBatchError(error_msg)

        results = self.client.batch.create_objects()
        self.objects_with_error.clear()
        for result in results:
            errors = result.get("result", {}).get("errors", [])
            if errors:
                obj_id = result.get("id")
                self.objects_with_error[obj_id] = self.buffered_objects.get(obj_id)
                logging.info(f"Object {obj_id} had errors: {errors}. Going to retry.")

        for buffered_object in self.objects_with_error.values():
            self.client.batch.add_data_object(
                buffered_object.properties, buffered_object.class_name, buffered_object.id, buffered_object.vector
            )

        if len(self.objects_with_error) > 0 and retries > 0:
            logging.info("sleeping 2 seconds before retrying batch again")
            time.sleep(2)
            self.flush(retries - 1)

        self.buffered_objects.clear()
