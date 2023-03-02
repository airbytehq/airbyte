#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import hashlib
import re
import uuid
from typing import Any, Mapping

from airbyte_cdk.models import ConfiguredAirbyteCatalog


def parse_vectors(vectors_config: str) -> Mapping[str, str]:
    vectors = {}
    if not vectors_config:
        return vectors

    vectors_list = vectors_config.replace(" ", "").split(",")
    for vector in vectors_list:
        stream_name, vector_column_name = vector.split(".")
        vectors[stream_name] = vector_column_name
    return vectors


def parse_id_schema(id_schema_config: str) -> Mapping[str, str]:
    id_schema = {}
    if not id_schema_config:
        return id_schema

    id_schema_list = id_schema_config.replace(" ", "").split(",")
    for schema_id in id_schema_list:
        stream_name, id_field_name = schema_id.split(".")
        id_schema[stream_name] = id_field_name
    return id_schema


def hex_to_int(hex_str: str) -> int:
    try:
        return int(hex_str, 16)
    except ValueError:
        return 0


def is_uuid_string(uuid_string):
    uuid_pattern = "^[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12}$"
    return re.match(uuid_pattern, uuid_string)


def generate_id(record_id: Any) -> uuid.UUID:
    if isinstance(record_id, int):
        return uuid.UUID(int=record_id)

    if isinstance(record_id, str):
        if is_uuid_string(record_id):
            return uuid.UUID(record_id)
        id_int = hex_to_int(record_id)
        if id_int > 0:
            return uuid.UUID(int=id_int)
        hex_string = hashlib.md5(record_id.encode("UTF-8")).hexdigest()
        return uuid.UUID(hex=hex_string)


def get_schema_from_catalog(configured_catalog: ConfiguredAirbyteCatalog) -> Mapping[str, Mapping[str, str]]:
    schema = {}
    for stream in configured_catalog.streams:
        stream_schema = {}
        for k, v in stream.stream.json_schema.get("properties").items():
            stream_schema[k] = "default"
            if "array" in v.get("type", []) and (
                "object" in v.get("items", {}).get("type", []) or "array" in v.get("items", {}).get("type", []) or v.get("items", {}) == {}
            ):
                stream_schema[k] = "jsonify"
            if "object" in v.get("type", []):
                stream_schema[k] = "jsonify"
        schema[stream.stream.name] = stream_schema
    return schema


def stream_to_class_name(stream_name: str) -> str:
    pattern = "[^0-9A-Za-z_]+"
    stream_name = re.sub(pattern, "", stream_name)
    stream_name = stream_name.replace(" ", "")
    return stream_name[0].upper() + stream_name[1:]
