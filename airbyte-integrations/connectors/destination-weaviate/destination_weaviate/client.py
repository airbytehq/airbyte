#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import uuid
import logging
import json
from typing import Any, Mapping, List

import weaviate


def parse_vectors(vectors_config: str) -> Mapping[str, str]:
    vectors = {}
    if not vectors_config:
        return vectors

    vectors_list = vectors_config.replace(" ", "").split(",")
    for vector in vectors_list:
        stream_name, vector_column_name = vector.split(".")
        vectors[stream_name] = vector_column_name
    return vectors


def hex_to_int(hex_str: str) -> int:
    try:
        return int(hex_str, 16)
    except ValueError:
        return 0



def generate_id(record_id: Any) -> uuid.UUID:
    if isinstance(record_id, int):
        return uuid.UUID(int=record_id)
    if isinstance(record_id, str):
        id_int = hex_to_int(record_id)
        if hex_to_int(record_id) > 0:
            return uuid.UUID(int=id_int)


class Client:
    def __init__(self, config: Mapping[str, Any], schema: Mapping[str, str]):
        self.client = self.get_weaviate_client(config)
        self.config = config
        self.batch_size = int(config.get("batch_size", 100))
        self.schema = schema
        self.vectors = parse_vectors(config.get("vectors"))


    def queue_write_operation(self, stream_name: str, record: Mapping):
        # TODO need to handle case where original DB ID is not a UUID
        record_id = ""
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
        self.client.batch.add_data_object(record, stream_name.title(), record_id, vector=vector)
        if self.client.batch.num_objects() >= self.batch_size:
            self.flush()

    def flush(self):
        # TODO add error handling instead of just logging
        results = self.client.batch.create_objects()
        for result in results:
            errors = result.get("result", {}).get("errors", [])
            if errors:
                logging.error(f"Object {result.get('id')} had errors: {errors}")

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
