#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import hashlib
import re
from dataclasses import dataclass
from typing import Any, List, Mapping, Optional

from airbyte_cdk.destinations.vector_db_based.config import ProcessingConfigModel
from airbyte_cdk.models.airbyte_protocol import ConfiguredAirbyteStream, DestinationSyncMode
from destination_opengauss_datavec.type_mapping import (
    AIRBYTE_TYPE_TO_SQL_TYPE,
    DEFAULT_SQL_TYPE,
    JSON_FORMAT_TO_SQL_TYPE,
    JSON_TYPE_TO_SQL_TYPE,
)


MAX_IDENTIFIER_LENGTH = 62

BASE_COLUMNS = {
    "document_id",
    "chunk_id",
    "content",
    "embedding",
    "_airbyte_extracted_at",
    "_airbyte_meta",
}


@dataclass(frozen=True)
class MetadataColumn:
    """Metadata field mapping from CDK metadata key to destination column."""

    metadata_key: str
    column_name: str
    sql_type: str


@dataclass(frozen=True)
class StreamDestination:
    """Resolved write target for one Airbyte stream."""

    schema_name: str
    table_name: str
    write_table_name: str
    mode: DestinationSyncMode
    metadata_columns: List[MetadataColumn]


class SchemaBuilder:
    def __init__(self, processing_config: ProcessingConfigModel, default_schema: str):
        self.processing_config = processing_config
        self.default_schema = normalize_identifier(default_schema)

    def create_stream_destination(self, configured_stream: ConfiguredAirbyteStream) -> StreamDestination:
        """Resolve final/write table names and metadata columns for one stream."""
        schema_name = normalize_identifier(configured_stream.stream.namespace or self.default_schema)
        table_name = normalize_identifier(configured_stream.stream.name)
        write_table_name = table_name
        if configured_stream.destination_sync_mode == DestinationSyncMode.overwrite:
            write_table_name = normalize_identifier(f"_airbyte_tmp_{table_name}")

        return StreamDestination(
            schema_name=schema_name,
            table_name=table_name,
            write_table_name=write_table_name,
            mode=configured_stream.destination_sync_mode,
            metadata_columns=self.create_metadata_columns(configured_stream),
        )

    def create_metadata_columns(self, configured_stream: ConfiguredAirbyteStream) -> List[MetadataColumn]:
        """Resolve configured metadata fields into destination columns."""
        schema = configured_stream.stream.json_schema or {}
        used_column_names = set(BASE_COLUMNS)
        columns = []

        for metadata_key in self.configured_metadata_fields(configured_stream):
            field_schema = schema_for_path(schema, metadata_key)
            if field_schema is None:
                continue

            destination_key = self.mapped_metadata_key(metadata_key)
            column_name = metadata_column_name(destination_key, used_column_names)
            used_column_names.add(column_name)
            columns.append(
                MetadataColumn(
                    metadata_key=destination_key,
                    column_name=column_name,
                    sql_type=schema_to_sql_type(field_schema),
                )
            )

        return columns

    def configured_metadata_fields(self, configured_stream: ConfiguredAirbyteStream) -> List[str]:
        """Use explicit metadata_fields or fall back to top-level stream fields."""
        if self.processing_config.metadata_fields:
            return list(self.processing_config.metadata_fields)

        properties = (configured_stream.stream.json_schema or {}).get("properties") or {}
        return list(properties.keys())

    def mapped_metadata_key(self, metadata_key: str) -> str:
        """Apply processing field_name_mappings to metadata field names."""
        for mapping in self.processing_config.field_name_mappings or []:
            if mapping.from_field == metadata_key:
                return mapping.to_field
        return metadata_key


def metadata_column_name(metadata_key: str, used_column_names: set) -> str:
    """Normalize a metadata field path into a non-conflicting SQL column name."""
    column_name = normalize_identifier(metadata_key.replace(".", "_"))
    while column_name in used_column_names:
        column_name = normalize_identifier(f"_{column_name}")
    return column_name


def schema_for_path(schema: Mapping[str, Any], field_path: str) -> Optional[Mapping[str, Any]]:
    """Find the JSON schema node for a dotted metadata field path."""
    current_schema: Optional[Mapping[str, Any]] = schema
    for part in field_path.split("."):
        if current_schema is None or part == "*":
            return None
        properties = current_schema.get("properties")
        if not isinstance(properties, Mapping) or part not in properties:
            return None
        current_schema = properties[part]
    return current_schema


def schema_to_sql_type(field_schema: Mapping[str, Any]) -> str:
    """Map schema to SQL type using airbyte_type, format, type, then jsonb fallback."""
    airbyte_type = field_schema.get("airbyte_type")
    json_type = field_schema.get("type")
    if isinstance(json_type, list):
        non_null_types = [item for item in json_type if item != "null"]
        json_type = non_null_types[0] if len(non_null_types) == 1 else None

    return (
        AIRBYTE_TYPE_TO_SQL_TYPE.get(str(airbyte_type))
        or JSON_FORMAT_TO_SQL_TYPE.get(str(field_schema.get("format")))
        or JSON_TYPE_TO_SQL_TYPE.get(str(json_type))
        or DEFAULT_SQL_TYPE
    )


def normalize_identifier(name: str) -> str:
    """Normalize arbitrary stream/field names into safe SQL identifiers."""
    normalized = re.sub(r"[^a-zA-Z0-9_]+", "_", name)
    normalized = re.sub(r"_+", "_", normalized)
    if not normalized:
        normalized = "airbyte_stream"
    if re.match(r"^[0-9]", normalized):
        normalized = f"_{normalized}"
    if len(normalized.encode("utf-8")) > MAX_IDENTIFIER_LENGTH:
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:8]
        prefix_length = MAX_IDENTIFIER_LENGTH - len(digest) - 1
        normalized = f"{normalized[:prefix_length]}_{digest}"
    return normalized
