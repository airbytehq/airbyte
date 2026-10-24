#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import logging
import os
import re
import uuid
from collections import defaultdict
from importlib.metadata import PackageNotFoundError, version
from typing import List, Optional, Tuple, Union
from urllib.parse import urlparse

import weaviate
from weaviate.classes.config import ConsistencyLevel
from weaviate.classes.init import AdditionalConfig, GrpcConfig, Proxies, Timeout
from weaviate.classes.query import Filter
from weaviate.classes.tenants import Tenant
from weaviate.config import ConnectionConfig

from airbyte_cdk.destinations.vector_db_based.document_processor import METADATA_RECORD_ID_FIELD
from airbyte_cdk.destinations.vector_db_based.indexer import Indexer
from airbyte_cdk.destinations.vector_db_based.utils import format_exception
from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog, DestinationSyncMode
from destination_weaviate.config import WeaviateIndexingConfigModel


class WeaviatePartialBatchError(Exception):
    pass


CLOUD_DEPLOYMENT_MODE = "cloud"
WEAVIATE_CLOUD_DOMAINS = (".weaviate.cloud", ".weaviate.network")
INTEGRATION_HEADER = "X-Weaviate-Client-Integration"


def _channel_option_value(value: str) -> Union[int, str]:
    try:
        return int(value)
    except ValueError:
        return value


def _integration_header_value() -> str:
    try:
        connector_version = version("airbyte-destination-weaviate")
    except PackageNotFoundError:
        connector_version = "unknown"
    return f"airbyte-destination-weaviate/{connector_version}"


class WeaviateIndexer(Indexer):
    config: WeaviateIndexingConfigModel
    client: weaviate.WeaviateClient

    def __init__(self, config: WeaviateIndexingConfigModel):
        super().__init__(config)

    def _http_url(self):
        host = self.config.host.strip()
        # The Weaviate Cloud console shows the REST endpoint without a scheme
        url = urlparse(host if "://" in host else f"https://{host}")
        if url.scheme not in ("http", "https") or not url.hostname:
            raise ValueError(f"Public Endpoint must be a hostname or a URL starting with http:// or https://, got {self.config.host!r}")
        return url

    def _grpc_endpoint(self, http_host: str, http_secure: bool) -> Tuple[str, int, bool]:
        connection = self.config.connection
        grpc_secure = http_secure if connection.grpc_secure == "auto" else connection.grpc_secure == "enabled"
        if connection.grpc_host.strip():
            grpc = urlparse(f"//{connection.grpc_host.strip().split('://')[-1]}")
            return grpc.hostname or http_host, grpc.port or (443 if grpc_secure else 50051), grpc_secure
        # Same derivation as weaviate.connect_to_weaviate_cloud
        if http_host.endswith(".weaviate.network"):
            ident, domain = http_host.split(".", 1)
            return f"{ident}.grpc.{domain}", 443, grpc_secure
        if http_host.endswith(WEAVIATE_CLOUD_DOMAINS):
            return f"grpc-{http_host}", 443, grpc_secure
        return http_host, 50051, grpc_secure

    def _credentials(self):
        auth = self.config.auth
        if auth.mode == "token":
            return weaviate.auth.AuthApiKey(auth.token)
        if auth.mode == "username_password":
            return weaviate.auth.AuthClientPassword(auth.username, auth.password, scope=auth.scope.strip() or None)
        if auth.mode == "client_credentials":
            return weaviate.auth.AuthClientCredentials(auth.client_secret, scope=auth.scope.strip() or None)
        if auth.mode == "bearer_token":
            return weaviate.auth.AuthBearerToken(
                auth.access_token, expires_in=auth.expires_in, refresh_token=auth.refresh_token.strip() or None
            )
        return None

    def _additional_config(self) -> AdditionalConfig:
        connection = self.config.connection
        proxies = None
        if connection.http_proxy or connection.https_proxy or connection.grpc_proxy:
            proxies = Proxies(http=connection.http_proxy or None, https=connection.https_proxy or None, grpc=connection.grpc_proxy or None)
        grpc_config = None
        if connection.grpc_channel_options:
            grpc_config = GrpcConfig(
                channel_options=[(option.name, _channel_option_value(option.value)) for option in connection.grpc_channel_options]
            )
        return AdditionalConfig(
            connection=ConnectionConfig(
                session_pool_connections=connection.session_pool_connections,
                session_pool_maxsize=connection.session_pool_maxsize,
                session_pool_max_retries=connection.session_pool_max_retries,
                session_pool_timeout=connection.session_pool_timeout,
            ),
            timeout=Timeout(init=connection.timeout_init, query=connection.timeout_query, insert=connection.timeout_insert),
            proxies=proxies,
            trust_env=connection.trust_env,
            grpc_config=grpc_config,
        )

    def _create_client(self):
        headers = {header.header_key: header.value for header in self.config.additional_headers}
        headers[INTEGRATION_HEADER] = _integration_header_value()

        url = self._http_url()
        http_secure = url.scheme == "https"
        grpc_host, grpc_port, grpc_secure = self._grpc_endpoint(url.hostname, http_secure)
        self.client = weaviate.connect_to_custom(
            http_host=url.hostname,
            http_port=url.port or (443 if http_secure else 80),
            http_secure=http_secure,
            grpc_host=grpc_host,
            grpc_port=grpc_port,
            grpc_secure=grpc_secure,
            headers=headers,
            additional_config=self._additional_config(),
            auth_credentials=self._credentials(),
            skip_init_checks=self.config.connection.skip_init_checks,
        )

    def _close_client(self):
        if hasattr(self, "client"):
            self.client.close()
            del self.client

    def _add_tenant_to_class_if_missing(self, class_name: str):
        tenants = self.client.collections.use(class_name).tenants
        if self.config.tenant_id not in tenants.get():
            tenants.create([Tenant(name=self.config.tenant_id)])
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
        finally:
            self._close_client()
        return None

    def _uses_safe_config(self) -> bool:
        try:
            https = self._http_url().scheme == "https"
        except ValueError:
            return False
        return https and not self.config.auth.mode == "no_auth"

    def pre_sync(self, catalog: ConfiguredAirbyteCatalog) -> None:
        self._create_client()
        classes = self.client.collections.list_all(simple=False)
        self.has_record_id_metadata = defaultdict(lambda: False)
        use_tenant = bool(self.config.tenant_id.strip())

        for stream in catalog.streams:
            class_name = self._stream_to_class_name(stream.stream.name)
            schema = classes.get(class_name)
            if stream.destination_sync_mode == DestinationSyncMode.overwrite and schema is not None:
                self.client.collections.delete(class_name)
                logging.info(f"Deleted class {class_name}")
                self.client.collections.create_from_config(schema)
                logging.info(f"Recreated class {class_name}")
            elif schema is None:
                config = {
                    "class": class_name,
                    "vectorizer": self.config.default_vectorizer,
                    "properties": [
                        {
                            # Record ID is used for bookkeeping, not for searching
                            "name": METADATA_RECORD_ID_FIELD,
                            "dataType": ["text"],
                            "description": "Record ID, used for bookkeeping.",
                            "indexFilterable": True,
                            "indexSearchable": False,
                            "tokenization": "field",
                        }
                    ],
                }
                if use_tenant:
                    config["multiTenancyConfig"] = {"enabled": True}

                self.client.collections.create_from_dict(config)
                logging.info(f"Created class {class_name}")
            else:
                self.has_record_id_metadata[class_name] = any(prop.name == METADATA_RECORD_ID_FIELD for prop in schema.properties)

            # Only touch the classes this sync writes to, and only when they are multi-tenant
            if use_tenant and (schema is None or schema.multi_tenancy_config.enabled):
                self._add_tenant_to_class_if_missing(class_name)

    def post_sync(self) -> List[AirbyteMessage]:
        self._close_client()
        return []

    def _consistency_level(self) -> Optional[ConsistencyLevel]:
        if self.config.consistency_level == "default":
            return None
        return ConsistencyLevel(self.config.consistency_level)

    def _collection(self, class_name: str):
        collection = self.client.collections.use(class_name)
        if self.config.tenant_id.strip():
            collection = collection.with_tenant(self.config.tenant_id)
        consistency_level = self._consistency_level()
        if consistency_level is not None:
            collection = collection.with_consistency_level(consistency_level)
        return collection

    def delete(self, delete_ids, namespace, stream):
        if len(delete_ids) > 0:
            class_name = self._stream_to_class_name(stream)
            if self.has_record_id_metadata[class_name]:
                self._collection(class_name).data.delete_many(where=Filter.by_property(METADATA_RECORD_ID_FIELD).contains_any(delete_ids))

    def index(self, document_chunks, namespace, stream):
        if len(document_chunks) == 0:
            return

        tenant = self.config.tenant_id if self.config.tenant_id.strip() else None
        # As a single record can be split into lots of documents, send them in batches as configured to not overwhelm the cluster
        with self.client.batch.fixed_size(
            batch_size=self.config.batch_size,
            concurrent_requests=self.config.concurrent_requests,
            consistency_level=self._consistency_level(),
        ) as weaviate_batch:
            for chunk in document_chunks:
                weaviate_object = {**self._normalize(chunk.metadata)}
                if chunk.page_content is not None:
                    weaviate_object[self.config.text_field] = chunk.page_content
                weaviate_batch.add_object(
                    collection=self._stream_to_class_name(chunk.record.stream),
                    properties=weaviate_object,
                    uuid=str(uuid.uuid4()),
                    vector=chunk.embedding,
                    tenant=tenant,
                )
        self._raise_on_failed_objects()

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

    def _raise_on_failed_objects(self):
        failed_objects = self.client.batch.failed_objects
        if len(failed_objects) > 0:
            error_msg = "Errors while loading: " + ", ".join([failed.message for failed in failed_objects])
            raise WeaviatePartialBatchError(error_msg)
