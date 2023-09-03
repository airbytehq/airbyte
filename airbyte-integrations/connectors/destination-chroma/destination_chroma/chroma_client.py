#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import uuid
from typing import Any, Mapping, MutableMapping

import chromadb
from chromadb.config import Settings

from .utils import convert_to_valid_collection_name, parse_id_schema, parse_embedding_schema


class ChromaClient:
    def __init__(self, config: Mapping[str, Any], schema: Mapping[str, str]) -> None:
        self.config = config
        self.schema = schema
        self.id_map = parse_id_schema(config.get('id_schema'))
        self.embedding_map = parse_embedding_schema(config.get('embeddings_schema'))
        self.client = self.get_client()

    @staticmethod
    def get_client(self):

        auth_method = self.config['credentials']['auth_method']

        if auth_method == 'persistent_client':
            path = self.config['credentials']['path']
            client = chromadb.PersistentClient(path=path)
            return client

        elif auth_method == 'http_client':
            credentials = self.config.get('credentials')

            username = credentials.get('username')
            password = credentials.get('password')
            host = credentials.get('host')
            port = credentials.get('port')

            settings = Settings(chroma_client_auth_provider="chromadb.auth.basic.BasicAuthClientProvider", chroma_client_auth_credentials=f"{username}:{password}")

            client = chromadb.HttpClient(settings=settings, host=host, port=port)
            return client

        client = chromadb.Client()
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
        record_id = self.get_record_id(stream_name=stream_name, record=record)
        embedding = self.get_embedding(stream_name=stream_name, record=record)
        record = self.prepare_record(stream_name=stream_name, record=record)
        collection_name = convert_to_valid_collection_name(stream_name)

        collection = self.client.get_collection(name=collection_name)
        collection.add(
            embeddings=embedding,
            documents=[record], # TODO get specific records to add
            ids=[record_id],
            metadata=None # TODO add support for metadata
        )

    def get_record_id(self, stream_name: str, record: MutableMapping):
        if self.id_map.get(stream_name, "") in record:
            id_field_name = self.id_map.get(stream_name, "")
            record_id = record.get(id_field_name)
            del record[id_field_name]
        else:
            if "id" in record:
                record_id = record.get("id")
                del record["id"]
            # Weaviate will throw an error if you try to store a field with name _id
            elif "_id" in record:
                record_id = record.get("_id")
                del record["_id"]
            else:
                record_id = uuid.uuid4()
        record_id = str(record_id)
        return record_id

    def prepare_record(self, stream_name: str, record: MutableMapping):
   
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

        return record

    def get_embedding(self, stream_name: str, record: MutableMapping):
        if stream_name in self.embedding_map:
            embedding_column_name = self.embedding_map.get(stream_name)
            embedding = record.get(embedding_column_name)
            del record[embedding_column_name]
            return [embedding]
        return None