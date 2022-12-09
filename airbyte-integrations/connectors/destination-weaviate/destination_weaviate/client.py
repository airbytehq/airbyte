#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import uuid
import logging
import json
from typing import Any, Mapping

import weaviate


class Client:
    def __init__(self, config: Mapping[str, Any], schema: Mapping[str, str]):
        self.client = self.get_weaviate_client(config)
        self.config = config
        self.batch_size = 100
        self.schema = schema

    def queue_write_operation(self, stream_name: str, record: Mapping):
        # TODO need to handle case where original DB ID is not a UUID
        id = ""
        if record.get("id"):
            id = record.get("id")
            if isinstance(id, int):
                id = uuid.UUID(int=id)
            del record["id"]
        else:
            id = uuid.uuid4()

        # TODO support nested objects instead of converting to json string when weaviate supports this
        for k, v in record.items():
            if self.schema[stream_name].get(k, "") == "jsonify":
                record[k] = json.dumps(v)
            # Handling of empty list that's not part of defined schema otherwise Weaviate throws invalid string property
            if isinstance(v, list) and len(v) == 0 and k not in self.schema[stream_name]:
                record[k] = ""

        self.client.batch.add_data_object(record, stream_name.title(), id)
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
