#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
import time
import uuid
from dataclasses import dataclass
from typing import Any, List, Mapping, MutableMapping, Iterable

from airbyte_cdk.models import AirbyteMessage, AirbyteStream

import weaviate

from .utils import generate_id, parse_id_schema, parse_vectors, stream_to_class_name


@dataclass
class BufferedObject:
    id: str
    properties: Mapping[str, Any]
    vector: List[Any]
    class_name: str


class WeaviatePartialBatchError(Exception):
    pass


class Client:
    def __init__(self, config: Mapping[str, Any], schema: Mapping[str, str]):
        self.batch_size = int(config.get("batch_size", 100))
        self.client = self.get_weaviate_client(config)
        self.config = config
        self.schema = schema
        self.vectors = parse_vectors(config.get("vectors"))
        self.id_schema = parse_id_schema(config.get("id_schema"))
        self.buffered_objects: MutableMapping[str, BufferedObject] = {}
        self.objects_with_error: MutableMapping[str, BufferedObject] = {}

    def batch_buffered_write(self, input_messages:Iterable[AirbyteMessage]):

        with self.client.batch() as batch:

            for message in input_messages:
                if message.type == Type.STATE:
                    # Emitting a state message indicates that all records which came before it have been written to the destination. So we flush
                    # the queue to ensure writes happen, then output the state message to indicate it's safe to checkpoint state
                    self.flush()
                    yield message
                elif message.type == Type.RECORD:
                    record = message.record

                    record, class_name, record_id, vector = self.process_message(record.stream, record.data)

                    batch.add_data_object(record, class_name, record_id, vector=vector)
                else:
                    # ignore other message types for now
                    continue

    def buffered_write_operation(self, stream_name: str, record: MutableMapping):
        
        record, class_name, record_id, vector = self.process_message(stream_name, record)

        self.client.batch.add_data_object(record, class_name, record_id, vector=vector)
        self.buffered_objects[record_id] = BufferedObject(record_id, record, vector, class_name)
        if self.client.batch.num_objects() >= self.batch_size:
            self.flush()

    # generic ETL massaging for a record to a Weaviate data types for client insertion
    def process_message(self, stream_name: str, record: MutableMapping):
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
        record_id = str(record_id)

        # TODO support nested objects instead of converting to json string when weaviate supports this
        for k, v in record.items():
            if self.schema[stream_name].get(k, "") == "jsonify":
                record[k] = json.dumps(v)
            # Handling of empty list that's not part of defined schema otherwise Weaviate throws invalid string property
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

        # Property names in Weaviate have to start with lowercase letter
        record = {k[0].lower() + k[1:]: v for k, v in record.items()}
        vector = None
        if stream_name in self.vectors:
            vector_column_name = self.vectors.get(stream_name)
            vector = record.get(vector_column_name)
            del record[vector_column_name]
        class_name = stream_to_class_name(stream_name)

        print(record_id, record)
        
        return (record, class_name, record_id, vector)


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
            print("Retrying buffered object", buffered_object.id, buffered_object.properties)
            self.client.batch.add_data_object(
                buffered_object.properties, buffered_object.class_name, buffered_object.id, buffered_object.vector
            )

        if len(self.objects_with_error) > 0 and retries > 0:
            logging.info("sleeping 2 seconds before retrying batch again")
            time.sleep(2)
            self.flush(retries - 1)

        self.buffered_objects.clear()

    def delete_stream_entries(self, stream:AirbyteStream):

        class_name = stream_to_class_name(stream.name)
        try:
            self.client.schema.delete_class(class_name=class_name)
            logging.info(f"Deleted class {class_name}")

            self.client.schema.create_class( self.map_airbyte_stream_to_weaviate_class(stream) )
            logging.info(f"Recreated class {class_name}")
        except weaviate.exceptions.UnexpectedStatusCodeException as e:
            if e.message.startswith("Get schema! Unexpected status code: 404"):
                logging.info(f"Class {class_name} did not exist.")
            else:
                raise e



    def get_current_weaviate_schema(self, class_name:str) -> dict:
        schema = None
        try:
            schema = self.client.schema.get(class_name=class_name)
        except weaviate.exceptions.UnexpectedStatusCodeException as e:
            if e.message.startswith("Get schema! Unexpected status code: 404"):
                logging.info(f"Class {class_name} did not exist.")
            else:
                raise e
        return schema

    def map_airbyte_stream_to_weaviate_class(self, stream:AirbyteStream) -> dict:
        weaviate_class = {}
        weaviate_class['class'] = stream_to_class_name(stream.name)
        weaviate_class['description'] = "This class was autogenerated by Airbyte"
        weaviate_class['properties'] = []

        for k, v in stream.json_schema.get("properties").items():

            data_type = v.get("type")
            if not isinstance(data_type, (list, tuple)):
                data_type = [data_type]
            else:
                data_type.remove('null')

            new_property = {}
            new_property['name'] = k
            new_property['dataType'] = data_type
            new_property['description'] = "This property was autogenerated by Airbyte"
            weaviate_class['properties'].append(new_property)

        # add class specific config options 
        weaviate_class["invertedIndexConfig"] = { "indexNullState": True }

        print("Generated class from stream:", weaviate_class)
        return weaviate_class

    def create_class_from_stream(self, stream:AirbyteStream):
        try:
            self.client.schema.create_class( self.map_airbyte_stream_to_weaviate_class(stream) )
        except weaviate.exceptions.UnexpectedStatusCodeException as e:
            if e.message.startswith("Create schema! Unexpected status code: 404"):
                logging.info(f"Class {class_name} was not created.")
            else:
                raise e

    @staticmethod
    def get_weaviate_client(config: Mapping[str, Any]) -> weaviate.Client:
        url, username, password, batch_size = config.get("url"), config.get("username"), config.get("password"), int(config.get("batch_size", 100))

        if username and not password:
            raise Exception("Password is required when username is set")
        if password and not username:
            raise Exception("Username is required when password is set")

        if username and password:
            credentials = weaviate.auth.AuthClientPassword(username, password)
            client = weaviate.Client(url=url, auth_client_secret=credentials)
        else: 
            client = weaviate.Client(url=url, timeout_config=(2, 2))

        client.batch.configure(batch_size=batch_size, dynamic=True)
        return client
