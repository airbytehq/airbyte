#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, Mapping, MutableMapping

import chromadb
from chromadb.config import Settings

from .utils import convert_to_valid_collection_name


class ChromaClient:
    def __init__(self, config: Mapping[str, Any], schema: Mapping[str, str]) -> None:
        self.username = config.get('username')
        self.password = config.get('password')
        self.host = config.get('host')
        self.port = config.get('port')
        self.client = self.get_client()
        self.schema = schema

    @staticmethod
    def get_client(self):

        settings = Settings(chroma_client_auth_provider="chromadb.auth.basic.BasicAuthClientProvider",chroma_client_auth_credentials=f"{self.username}:{self.password}")

        client = chromadb.HttpClient(settings=settings, host=self.host, port=self.port)

        return client
    
    def delete_collection_data(self, stream_name: str):
        collection_name = convert_to_valid_collection_name(stream_name)
        try:
            self.client.delete_collection(name=collection_name)
            self.client.create_collection(name=collection_name)
        except ValueError as e:
            raise e
        
    def flush(self):
        pass

    def write_data(self, stream_name: str, record: MutableMapping):
        for k, v in record.items():
            if self.schema[stream_name].get(k, "") == "jsonify":
                record[k] = json.dumps(v)
            # Handling of empty list that's not part of defined schema
            if isinstance(v, list) and len(v) == 0 and k not in self.schema[stream_name]:
                record[k] = ""

        missing_properties = set(self.schema[stream_name].keys()).difference(record.keys()).discard("id")
        for prop in missing_properties or []:
            record[prop] = None

        additional_props = set(record.keys()).difference(self.schema[stream_name].keys())
        for prop in additional_props or []:
            if isinstance(record[prop], dict):
                record[prop] = json.dumps(record[prop])
            if isinstance(record[prop], list) and len(record[prop]) > 0 and isinstance(record[prop][0], dict):
                record[prop] = json.dumps(record[prop])

        collection_name = convert_to_valid_collection_name(stream_name)
        collection = self.client.get_collection(name=collection_name)
        collection.add(
            documents=[record],
            ids=[record.primary_key],
            metadata=None
        )
