#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import uuid
import logging
import json
from typing import Any, Mapping

import weaviate
from .utils import generate_id, parse_id_schema, parse_vectors, stream_to_class_name


class Client:
    def __init__(self, config: Mapping[str, Any], schema: Mapping[str, str]):
        self.client = self.get_weaviate_client(config)
        self.config = config
        self.batch_size = int(config.get("batch_size", 100))
        self.schema = schema
        self.vectors = parse_vectors(config.get("vectors"))
        self.id_schema = parse_id_schema(config.get("id_schema"))

    def queue_write_operation(self, stream_name: str, record: Mapping):
        # TODO need to handle case where original DB ID is not a UUID
        if self.id_schema.get(stream_name, "") in record:
            id_field_name = self.id_schema.get(stream_name, "")
            record_id = generate_id(record.get(id_field_name))
            del record[id_field_name]
        else:
            if "id" in record:
                record_id = generate_id(record.get("id"))
                del record["id"]
            # Weaviate will throw an error if you try to store a field with name _id
            elif "_id" in record:
                record_id = generate_id(record.get("_id"))
                del record["_id"]
            else:
                record_id = uuid.uuid4()

        # TODO support nested objects instead of converting to json string when weaviate supports this
        for k, v in record.items():
            if self.schema[stream_name].get(k, "") == "jsonify":
                record[k] = json.dumps(v)
            # Handling of empty list that's not part of defined schema otherwise Weaviate throws invalid string property
            if isinstance(v, list) and len(v) == 0 and k not in self.schema[stream_name]:
                record[k] = ""

        # Property names in Weaviate have to start with lowercase letter
        record = {k[0].lower() + k[1:]: v for k, v in record.items()}
        vector = None
        if stream_name in self.vectors:
            vector_column_name = self.vectors.get(stream_name)
            vector = record.get(vector_column_name)
            del record[vector_column_name]
        class_name = stream_to_class_name(stream_name)
        self.client.batch.add_data_object(record, class_name, record_id, vector=vector)
        if self.client.batch.num_objects() >= self.batch_size:
            self.flush()

    def flush(self):
        # TODO add error handling instead of just logging
        results = self.client.batch.create_objects()
        for result in results:
            errors = result.get("result", {}).get("errors", [])
            if errors:
                logging.error(f"Object {result.get('id')} had errors: {errors}")

    def delete_stream_entries(self, stream_name: str):
        class_name = stream_to_class_name(stream_name)
        try:
            original_schema = self.client.schema.get(class_name=class_name)
            self.client.schema.delete_class(class_name=class_name)
            logging.info(f"Deleted class {class_name}")
            self.client.schema.create_class(original_schema)
            logging.info(f"Recreated class {class_name}")
        except weaviate.exceptions.UnexpectedStatusCodeException as e:
            if e.message.startswith("Get schema! Unexpected status code: 404"):
                logging.info(f"Class {class_name} did not exist.")
            else:
                raise e

    @staticmethod
    def get_weaviate_client(config: Mapping[str, Any]) -> weaviate.Client:
        url, username, password = config.get("url"), config.get("username"), config.get("password")

        if username and not password:
            raise Exception("Password is required when username is set")
        if password and not username:
            raise Exception("Username is required when password is set")

        if username and password:
            credentials = weaviate.auth.AuthClientPassword(username, password)
            return weaviate.Client(url=url, auth_client_secret=credentials)
        return weaviate.Client(url=url, timeout_config=(2, 2))
