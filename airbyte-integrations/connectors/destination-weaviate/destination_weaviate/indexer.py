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

import weaviate
from airbyte_cdk.destinations.vector_db_based.document_processor import METADATA_RECORD_ID_FIELD
from airbyte_cdk.destinations.vector_db_based.indexer import Indexer
from airbyte_cdk.destinations.vector_db_based.utils import create_chunks, format_exception
from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode
from destination_weaviate.config import WeaviateIndexingConfigModel


class WeaviatePartialBatchError(Exception):
    pass


CLOUD_DEPLOYMENT_MODE = "cloud"


class WeaviateIndexer(Indexer):
    config: WeaviateIndexingConfigModel

    def __init__(self, config: WeaviateIndexingConfigModel):
        super().__init__(config)

    def _create_client(self):
        headers = {
            self.config.additional_headers[i].header_key: self.config.additional_headers[i].value
            for i in range(len(self.config.additional_headers))
        }
        if self.config.auth.mode == "username_password":
            credentials = weaviate.auth.AuthClientPassword(self.config.auth.username, self.config.auth.password)
            self.client = weaviate.Client(url=self.config.host, auth_client_secret=credentials, additional_headers=headers)
        elif self.config.auth.mode == "token":
            credentials = weaviate.auth.AuthApiKey(self.config.auth.token)
            self.client = weaviate.Client(url=self.config.host, auth_client_secret=credentials, additional_headers=headers)
        else:
            self.client = weaviate.Client(url=self.config.host, additional_headers=headers)

        # disable dynamic batching because it's handled asynchroniously in the client
        self.client.batch.configure(
            batch_size=None, dynamic=False, weaviate_error_retries=weaviate.WeaviateErrorRetryConf(number_retries=5)
        )

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
        classes = {c["class"]: c for c in self.client.schema.get().get("classes", [])}
        self.has_record_id_metadata = defaultdict(lambda: False)
        for stream in catalog.streams:
            class_name = self.stream_to_class_name(stream.stream.name)
            schema = classes[class_name] if class_name in classes else None
            if stream.destination_sync_mode == DestinationSyncMode.overwrite and schema is not None:
                self.client.schema.delete_class(class_name=class_name)
                logging.info(f"Deleted class {class_name}")
                self.client.schema.create_class(schema)
                logging.info(f"Recreated class {class_name}")
            elif class_name not in classes:
                self.client.schema.create_class(
                    {
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
                )
                logging.info(f"Created class {class_name}")
            else:
                self.has_record_id_metadata[class_name] = schema is not None and any(
                    prop.get("name") == METADATA_RECORD_ID_FIELD for prop in schema.get("properties", {})
                )

    def delete(self, delete_ids, namespace, stream):
        if len(delete_ids) > 0:
            class_name = self.stream_to_class_name(stream)
            if self.has_record_id_metadata[class_name]:
                self.client.batch.delete_objects(
                    class_name=class_name,
                    where={"path": [METADATA_RECORD_ID_FIELD], "operator": "ContainsAny", "valueStringArray": delete_ids},
                )

    def index(self, document_chunks, namespace, stream):
        if len(document_chunks) == 0:
            return

        # As a single record can be split into lots of documents, break them into batches as configured to not overwhelm the cluster
        batches = create_chunks(document_chunks, batch_size=self.config.batch_size)
        for batch in batches:
            for i in range(len(batch)):
                chunk = batch[i]
                weaviate_object = {**self._normalize(chunk.metadata), self.config.text_field: chunk.page_content}
                object_id = str(uuid.uuid4())
                class_name = self.stream_to_class_name(chunk.record.stream)
                self.client.batch.add_data_object(weaviate_object, class_name, object_id, vector=chunk.embedding)
            self._flush()

    def stream_to_class_name(self, stream_name: str) -> str:
        pattern = "[^0-9A-Za-z_]+"
        stream_name = re.sub(pattern, "", stream_name)
        stream_name = stream_name.replace(" ", "")
        return stream_name[0].upper() + stream_name[1:]

    def _normalize(self, metadata: dict) -> dict:
        result = {}

        for key, value in metadata.items():
            # Property names in Weaviate have to start with lowercase letter
            normalized_key = key[0].lower() + key[1:]
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

    def _flush(self, retries: int = 3):
        results = self.client.batch.create_objects()
        all_errors = []

        for result in results:
            errors = result.get("result", {}).get("errors", [])
            if errors:
                all_errors.extend(errors)

        if len(all_errors) > 0:
            error_msg = "Errors while loading: " + ", ".join([str(error) for error in all_errors])
            raise WeaviatePartialBatchError(error_msg)
