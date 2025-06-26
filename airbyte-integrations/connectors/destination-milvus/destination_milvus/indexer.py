#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import os
from multiprocessing import Process
from typing import Optional

from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, utility

from airbyte_cdk.destinations.vector_db_based.document_processor import METADATA_RECORD_ID_FIELD, METADATA_STREAM_FIELD
from airbyte_cdk.destinations.vector_db_based.indexer import Indexer
from airbyte_cdk.destinations.vector_db_based.utils import create_stream_identifier, format_exception
from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode
from destination_milvus.config import MilvusIndexingConfigModel


CLOUD_DEPLOYMENT_MODE = "cloud"


class MilvusIndexer(Indexer):
    config: MilvusIndexingConfigModel

    def __init__(self, config: MilvusIndexingConfigModel, embedder_dimensions: int):
        super().__init__(config)
        self.embedder_dimensions = embedder_dimensions

    def _connect(self):
        connections.connect(
            uri=self.config.host,
            db_name=self.config.db if self.config.db else "",
            user=self.config.auth.username if self.config.auth.mode == "username_password" else "",
            password=self.config.auth.password if self.config.auth.mode == "username_password" else "",
            token=self.config.auth.token if self.config.auth.mode == "token" else "",
        )

    def _connect_with_timeout(self):
        # Run connect in a separate process as it will hang if the token is invalid.
        proc = Process(target=self._connect)
        proc.start()
        proc.join(5)
        if proc.is_alive():
            # If the process is still alive after 5 seconds, terminate it and raise an exception
            proc.terminate()
            proc.join()
            raise Exception("Connection timed out, check your host and credentials")

    def _create_index(self, collection: Collection):
        """
        Create an index on the vector field when auto-creating the collection.

        This uses an IVF_FLAT index with 1024 clusters. This is a good default for most use cases. If more control is needed, the index can be created manually (this is also stated in the documentation)
        """
        collection.create_index(
            field_name=self.config.vector_field, index_params={"metric_type": "L2", "index_type": "IVF_FLAT", "params": {"nlist": 1024}}
        )

    def _create_client(self):
        self._connect_with_timeout()
        # If the process exited within 5 seconds, it's safe to connect on the main process to execute the command
        self._connect()

        if not utility.has_collection(self.config.collection):
            pk = FieldSchema(name="pk", dtype=DataType.INT64, is_primary=True, auto_id=True)
            vector = FieldSchema(name=self.config.vector_field, dtype=DataType.FLOAT_VECTOR, dim=self.embedder_dimensions)
            schema = CollectionSchema(fields=[pk, vector], enable_dynamic_field=True)
            collection = Collection(name=self.config.collection, schema=schema)
            self._create_index(collection)

        self._collection = Collection(self.config.collection)
        self._collection.load()
        self._primary_key = self._collection.primary_field.name

    def check(self) -> Optional[str]:
        deployment_mode = os.environ.get("DEPLOYMENT_MODE", "")
        if deployment_mode.casefold() == CLOUD_DEPLOYMENT_MODE and not self._uses_safe_config():
            return "Host must start with https:// and authentication must be enabled on cloud deployment."
        try:
            self._create_client()

            description = self._collection.describe()
            if not description["auto_id"]:
                return "Only collections with auto_id are supported"
            vector_field = next((field for field in description["fields"] if field["name"] == self.config.vector_field), None)
            if vector_field is None:
                return f"Vector field {self.config.vector_field} not found"
            if vector_field["type"] != DataType.FLOAT_VECTOR:
                return f"Vector field {self.config.vector_field} is not a vector"
            if vector_field["params"]["dim"] != self.embedder_dimensions:
                return f"Vector field {self.config.vector_field} is not a {self.embedder_dimensions}-dimensional vector"
        except Exception as e:
            return format_exception(e)
        return None

    def _uses_safe_config(self) -> bool:
        return self.config.host.startswith("https://") and not self.config.auth.mode == "no_auth"

    def pre_sync(self, catalog: ConfiguredAirbyteCatalog) -> None:
        self._create_client()
        for stream in catalog.streams:
            if stream.destination_sync_mode == DestinationSyncMode.overwrite:
                self._delete_for_filter(f'{METADATA_STREAM_FIELD} == "{create_stream_identifier(stream.stream)}"')

    def _delete_for_filter(self, expr: str) -> None:
        iterator = self._collection.query_iterator(expr=expr)
        page = iterator.next()
        while len(page) > 0:
            id_field = next(iter(page[0].keys()))
            ids = [next(iter(entity.values())) for entity in page]
            id_list_expr = ", ".join([str(id) for id in ids])
            self._collection.delete(expr=f"{id_field} in [{id_list_expr}]")
            page = iterator.next()

    def _normalize(self, metadata: dict) -> dict:
        result = {}

        for key, value in metadata.items():
            normalized_key = key
            # the primary key can't be set directly with auto_id, so we prefix it with an underscore
            if key == self._primary_key:
                normalized_key = f"_{key}"
            result[normalized_key] = value

        return result

    def index(self, document_chunks, namespace, stream):
        entities = []
        for i in range(len(document_chunks)):
            chunk = document_chunks[i]
            entity = {
                **self._normalize(chunk.metadata),
                self.config.vector_field: chunk.embedding,
                self.config.text_field: chunk.page_content,
            }
            if chunk.page_content is not None:
                entity[self.config.text_field] = chunk.page_content
            entities.append(entity)
        self._collection.insert(entities)

    def delete(self, delete_ids, namespace, stream):
        if len(delete_ids) > 0:
            id_list_expr = ", ".join([f'"{id}"' for id in delete_ids])
            id_expr = f"{METADATA_RECORD_ID_FIELD} in [{id_list_expr}]"
            self._delete_for_filter(id_expr)
