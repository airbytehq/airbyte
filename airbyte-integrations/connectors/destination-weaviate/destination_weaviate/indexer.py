#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import logging
import os
import re
import uuid
from collections import defaultdict
from typing import Optional
from urllib.parse import urlparse

import weaviate
import weaviate.classes.config as wvc_config
import weaviate.classes.query as wvc_query
import weaviate.classes.tenants as wvc_tenants

from airbyte_cdk.destinations.vector_db_based.document_processor import METADATA_RECORD_ID_FIELD
from airbyte_cdk.destinations.vector_db_based.indexer import Indexer
from airbyte_cdk.destinations.vector_db_based.utils import create_chunks, format_exception
from airbyte_cdk.models import ConfiguredAirbyteCatalog, DestinationSyncMode
from destination_weaviate.config import WeaviateIndexingConfigModel


class WeaviatePartialBatchError(Exception):
    pass


CLOUD_DEPLOYMENT_MODE = "cloud"



class WeaviateIndexer(Indexer):
    config: WeaviateIndexingConfigModel

    def __init__(self, config: WeaviateIndexingConfigModel):
        super().__init__(config)
        self.client: Optional[weaviate.WeaviateClient] = None

    def _create_client(self):
        headers = {
            header.header_key: header.value
            for header in self.config.additional_headers
        }

        auth_credentials = None
        if self.config.auth.mode == "username_password":
            auth_credentials = weaviate.auth.AuthClientPassword(
                username=self.config.auth.username,
                password=self.config.auth.password,
            )
        elif self.config.auth.mode == "token":
            auth_credentials = weaviate.auth.AuthApiKey(api_key=self.config.auth.token)

        parsed = urlparse(self.config.host)
        is_secure = parsed.scheme == "https"

        if is_secure:
            # Weaviate Cloud and HTTPS deployments where HTTP and gRPC share port 443
            self.client = weaviate.connect_to_weaviate_cloud(
                cluster_url=self.config.host,
                auth_credentials=auth_credentials,
                headers=headers,
            )
        else:
            # Local, Docker, k8s — HTTP on parsed port, gRPC on configured or default 50051
            hostname = parsed.hostname
            http_port = parsed.port or 80
            grpc_port = self.config.grpc_port or 50051
            self.client = weaviate.connect_to_custom(
                http_host=hostname,
                http_port=http_port,
                http_secure=False,
                grpc_host=hostname,
                grpc_port=grpc_port,
                grpc_secure=False,
                auth_credentials=auth_credentials,
                headers=headers,
            )

    def _add_tenant_to_class_if_missing(self, class_name: str):
        assert self.client is not None
        collection = self.client.collections.get(class_name)
        existing_tenants = collection.tenants.get()
        if self.config.tenant_id not in existing_tenants:
            collection.tenants.create([wvc_tenants.Tenant(name=self.config.tenant_id)])
            logging.info(f"Added tenant {self.config.tenant_id} to class {class_name}")
        else:
            logging.info(f"Tenant {self.config.tenant_id} already exists in class {class_name}")

    def check(self) -> Optional[str]:
        deployment_mode = os.environ.get("DEPLOYMENT_MODE", "")
        if deployment_mode.casefold() == CLOUD_DEPLOYMENT_MODE and not self._uses_safe_config():
            return "Host must start with https:// and authentication must be enabled on cloud deployment."
        try:
            self._create_client()
        except Exception as e:
            return format_exception(e)
        return None

    def _uses_safe_config(self) -> bool:
        return self.config.host.startswith("https://") and not self.config.auth.mode == "no_auth"

    def pre_sync(self, catalog: ConfiguredAirbyteCatalog) -> None:
        self._create_client()
        assert self.client is not None
        all_collections = self.client.collections.list_all(simple=False)
        existing_names = set(all_collections.keys())
        self.has_record_id_metadata = defaultdict(lambda: False)

        if self.config.tenant_id.strip():
            for name in existing_names:
                self._add_tenant_to_class_if_missing(name)

        for stream in catalog.streams:
            class_name = self._stream_to_class_name(stream.stream.name)
            if stream.destination_sync_mode == DestinationSyncMode.overwrite and class_name in existing_names:
                config_dict = self.client.collections.export_config(class_name).to_dict()
                self.client.collections.delete(class_name)
                logging.info(f"Deleted class {class_name}")
                self.client.collections.create_from_dict(config_dict)
                logging.info(f"Recreated class {class_name}")
            elif class_name not in existing_names:
                vector_config = (
                    wvc_config.Configure.Vectors.self_provided()
                    if self.config.default_vectorizer == "none"
                    else wvc_config.Configure.Vectors.custom(module_name=self.config.default_vectorizer)
                )
                mt_config = wvc_config.Configure.multi_tenancy(enabled=True) if self.config.tenant_id.strip() else None

                self.client.collections.create(
                    name=class_name,
                    vector_config=vector_config,
                    properties=[
                        wvc_config.Property(
                            name=METADATA_RECORD_ID_FIELD,
                            data_type=wvc_config.DataType.TEXT,
                            description="Record ID, used for bookkeeping.",
                            index_filterable=True,
                            index_searchable=False,
                            tokenization=wvc_config.Tokenization.FIELD,
                        )
                    ],
                    multi_tenancy_config=mt_config,
                )
                logging.info(f"Created class {class_name}")

                if self.config.tenant_id.strip():
                    self._add_tenant_to_class_if_missing(class_name)
            else:
                config = all_collections[class_name]
                self.has_record_id_metadata[class_name] = config is not None and any(
                    prop.name == METADATA_RECORD_ID_FIELD for prop in (config.properties or [])
                )

    def delete(self, delete_ids, namespace, stream):
        if len(delete_ids) > 0:
            class_name = self._stream_to_class_name(stream)
            if self.has_record_id_metadata[class_name]:
                collection = self.client.collections.get(class_name)
                where_filter = wvc_query.Filter.by_property(METADATA_RECORD_ID_FIELD).contains_any(delete_ids)
                if self.config.tenant_id.strip():
                    collection.with_tenant(self.config.tenant_id).data.delete_many(where=where_filter)
                else:
                    collection.data.delete_many(where=where_filter)

    def index(self, document_chunks, namespace, stream):
        if len(document_chunks) == 0:
            return

        # As a single record can be split into lots of documents, break them into batches as configured to not overwhelm the cluster
        batches = create_chunks(document_chunks, batch_size=self.config.batch_size)
        for batch_docs in batches:
            with self.client.batch.fixed_size(batch_size=len(batch_docs)) as batch:
                for chunk in batch_docs:
                    weaviate_object = {**self._normalize(chunk.metadata)}
                    if chunk.page_content is not None:
                        weaviate_object[self.config.text_field] = chunk.page_content
                    object_id = str(uuid.uuid4())
                    class_name = self._stream_to_class_name(chunk.record.stream)
                    batch.add_object(
                        properties=weaviate_object,
                        collection=class_name,
                        uuid=object_id,
                        vector=chunk.embedding,
                        tenant=self.config.tenant_id if self.config.tenant_id.strip() else None,
                    )

            failed = self.client.batch.failed_objects
            if failed:
                error_msg = "Errors while loading: " + ", ".join([str(e) for e in failed])
                raise WeaviatePartialBatchError(error_msg)

    def _stream_to_class_name(self, stream_name: str) -> str:
        pattern = "[^0-9A-Za-z_]+"
        stream_name = re.sub(pattern, "", stream_name)
        stream_name = stream_name.replace(" ", "")
        return stream_name[0].upper() + stream_name[1:]

    def _normalize_property_name(self, field_name: str) -> str:
        # Remove invalid characters and replace spaces with underscores
        normalized = re.sub(r"[^0-9A-Za-z_]", "", field_name.replace(" ", "_"))

        # Ensure the name starts with a letter or underscore
        if not re.match(r"^[_A-Za-z]", normalized):
            normalized = "_" + normalized

        return normalized[0].lower() + normalized[1:]

    def _normalize(self, metadata: dict) -> dict:
        result = {}

        for key, value in metadata.items():
            # Property names in Weaviate have to start with lowercase letter
            normalized_key = self._normalize_property_name(key)
            # "id" and "additional" are reserved properties in Weaviate, prefix to disambiguate
            if key == "id" or key == "_id" or key == "_additional":
                normalized_key = f"raw_{key}"
            if isinstance(value, list) and len(value) == 0:
                # Handling of empty list that's not part of defined schema otherwise Weaviate throws invalid string property
                continue
            if isinstance(value, (str, int, float, bool)) or (isinstance(value, list) and all(isinstance(item, str) for item in value)):
                result[normalized_key] = value
            else:
                # JSON encode all other types
                result[normalized_key] = json.dumps(value)

        return result
