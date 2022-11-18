#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
import os
import re
from typing import Any, Dict, List, Set

import yaml
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode, SyncMode
from normalization.destination_type import DestinationType
from normalization.transform_catalog import dbt_macro
from normalization.transform_catalog.destination_name_transformer import DestinationNameTransformer
from normalization.transform_catalog.stream_processor import StreamProcessor
from normalization.transform_catalog.table_name_registry import TableNameRegistry


class CatalogProcessor:
    """
    Takes as input an AirbyteCatalog file (stored as Json Schema).
    Associated input raw data is expected to be stored in a staging area called "raw_schema".

    This processor reads the catalog file, extracts streams descriptions and transforms them to final tables in their
    targeted destination schema.

    This is relying on a StreamProcessor to handle the conversion of a stream to a table one at a time.
    """

    def __init__(self, output_directory: str, destination_type: DestinationType):
        """
        @param output_directory is the path to the directory where this processor should write the resulting SQL files (DBT models)
        @param destination_type is the destination type of warehouse
        """
        self.output_directory: str = output_directory
        self.destination_type: DestinationType = destination_type
        self.name_transformer: DestinationNameTransformer = DestinationNameTransformer(destination_type)
        self.models_to_source: Dict[str, str] = {}

    def process(self, catalog_file: str, json_column_name: str, default_schema: str):
        """
        This method first parse and build models to handle top-level streams.
        In a second loop will go over the substreams that were nested in a breadth-first traversal manner.

        @param catalog_file input AirbyteCatalog file in JSON Schema describing the structure of the raw data
        @param json_column_name is the column name containing the JSON Blob with the raw data
        @param default_schema is the final schema where to output the final transformed data to
        """
        tables_registry: TableNameRegistry = TableNameRegistry(self.destination_type)
        schema_to_source_tables: Dict[str, Set[str]] = {}
        catalog = read_json(catalog_file)
        # print(json.dumps(catalog, separators=(",", ":")))
        substreams = []
        stream_processors = self.build_stream_processor(
            catalog=catalog,
            json_column_name=json_column_name,
            default_schema=default_schema,
            name_transformer=self.name_transformer,
            destination_type=self.destination_type,
            tables_registry=tables_registry,
        )
        for stream_processor in stream_processors:
            stream_processor.collect_table_names()
        for conflict in tables_registry.resolve_names():
            print(
                f"WARN: Resolving conflict: {conflict.schema}.{conflict.table_name_conflict} "
                f"from '{'.'.join(conflict.json_path)}' into {conflict.table_name_resolved}"
            )
        for stream_processor in stream_processors:
            # MySQL table names need to be manually truncated, because it does not do it automatically
            truncate = self.destination_type == DestinationType.MYSQL or self.destination_type == DestinationType.TIDB
            raw_table_name = self.name_transformer.normalize_table_name(f"_airbyte_raw_{stream_processor.stream_name}", truncate=truncate)
            add_table_to_sources(schema_to_source_tables, stream_processor.schema, raw_table_name)

            nested_processors = stream_processor.process()
            self.models_to_source.update(stream_processor.models_to_source)

            if nested_processors and len(nested_processors) > 0:
                substreams += nested_processors
            for file in stream_processor.sql_outputs:
                output_sql_file(os.path.join(self.output_directory, file), stream_processor.sql_outputs[file])
        self.write_yaml_sources_file(schema_to_source_tables)
        self.process_substreams(substreams, tables_registry)

    @staticmethod
    def build_stream_processor(
        catalog: Dict,
        json_column_name: str,
        default_schema: str,
        name_transformer: DestinationNameTransformer,
        destination_type: DestinationType,
        tables_registry: TableNameRegistry,
    ) -> List[StreamProcessor]:
        result = []
        for configured_stream in get_field(catalog, "streams", "Invalid Catalog: 'streams' is not defined in Catalog"):
            stream_config = get_field(configured_stream, "stream", "Invalid Stream: 'stream' is not defined in Catalog streams")

            # The logic here matches the logic in JdbcBufferedConsumerFactory.java.
            # Any modifications need to be reflected there and vice versa.
            schema = default_schema
            if "namespace" in stream_config:
                schema = stream_config["namespace"]

            schema_name = name_transformer.normalize_schema_name(schema, truncate=False)
            if destination_type == DestinationType.ORACLE:
                quote_in_parenthesis = re.compile(r"quote\((.*)\)")
                raw_schema_name = name_transformer.normalize_schema_name(schema, truncate=False)
                if not quote_in_parenthesis.findall(json_column_name):
                    json_column_name = name_transformer.normalize_column_name(json_column_name, in_jinja=True)
            else:
                column_inside_single_quote = re.compile(r"\'(.*)\'")
                raw_schema_name = name_transformer.normalize_schema_name(f"_airbyte_{schema}", truncate=False)
                if not column_inside_single_quote.findall(json_column_name):
                    json_column_name = f"'{json_column_name}'"

            stream_name = get_field(stream_config, "name", f"Invalid Stream: 'name' is not defined in stream: {str(stream_config)}")
            # MySQL table names need to be manually truncated, because it does not do it automatically
            truncate = destination_type == DestinationType.MYSQL or destination_type == DestinationType.TIDB
            raw_table_name = name_transformer.normalize_table_name(f"_airbyte_raw_{stream_name}", truncate=truncate)

            source_sync_mode = get_source_sync_mode(configured_stream, stream_name)
            destination_sync_mode = get_destination_sync_mode(configured_stream, stream_name)
            cursor_field = []
            primary_key = []
            if source_sync_mode.value == SyncMode.incremental.value or destination_sync_mode.value in [
                # DestinationSyncMode.upsert_dedup.value,
                DestinationSyncMode.append_dedup.value,
            ]:
                cursor_field = get_field(configured_stream, "cursor_field", f"Undefined cursor field for stream {stream_name}")
            if destination_sync_mode.value in [
                # DestinationSyncMode.upsert_dedup.value,
                DestinationSyncMode.append_dedup.value
            ]:
                primary_key = get_field(configured_stream, "primary_key", f"Undefined primary key for stream {stream_name}")

            message = f"'json_schema'.'properties' are not defined for stream {stream_name}"
            properties = get_field(get_field(stream_config, "json_schema", message), "properties", message)

            from_table = dbt_macro.Source(schema_name, raw_table_name)

            stream_processor = StreamProcessor.create(
                stream_name=stream_name,
                destination_type=destination_type,
                raw_schema=raw_schema_name,
                default_schema=default_schema,
                schema=schema_name,
                source_sync_mode=source_sync_mode,
                destination_sync_mode=destination_sync_mode,
                cursor_field=cursor_field,
                primary_key=primary_key,
                json_column_name=json_column_name,
                properties=properties,
                tables_registry=tables_registry,
                from_table=from_table,
            )
            result.append(stream_processor)
        return result

    def process_substreams(self, substreams: List[StreamProcessor], tables_registry: TableNameRegistry):
        """
        Handle nested stream/substream/children
        """
        while substreams:
            children = substreams
            substreams = []
            for substream in children:
                substream.tables_registry = tables_registry
                nested_processors = substream.process()
                self.models_to_source.update(substream.models_to_source)
                if nested_processors:
                    substreams += nested_processors
                for file in substream.sql_outputs:
                    output_sql_file(os.path.join(self.output_directory, file), substream.sql_outputs[file])

    def write_yaml_sources_file(self, schema_to_source_tables: Dict[str, Set[str]]):
        """
        Generate the sources.yaml file as described in https://docs.getdbt.com/docs/building-a-dbt-project/using-sources/
        """
        schemas = []
        for entry in sorted(schema_to_source_tables.items(), key=lambda kv: kv[0]):
            schema = entry[0]
            quoted_schema = self.name_transformer.needs_quotes(schema)
            tables = []
            for source in sorted(schema_to_source_tables[schema]):
                if quoted_schema:
                    tables.append({"name": source, "quoting": {"identifier": True}})
                else:
                    tables.append({"name": source})
            schemas.append(
                {
                    "name": schema,
                    "quoting": {
                        "database": True,
                        "schema": quoted_schema,
                        "identifier": False,
                    },
                    "tables": tables,
                }
            )
        source_config = {"version": 2, "sources": schemas}
        source_path = os.path.join(self.output_directory, "sources.yml")
        output_dir = os.path.dirname(source_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        with open(source_path, "w") as fh:
            fh.write(yaml.dump(source_config, sort_keys=False))


# Static Functions


def read_json(input_path: str) -> Any:
    """
    Reads and load a json file
    @param input_path is the path to the file to read
    """
    with open(input_path, "r") as file:
        contents = file.read()
    return json.loads(contents)


def get_field(config: Dict, key: str, message: str):
    """
    Retrieve value of field in a Dict object. Throw an error if key is not found with message as reason.
    """
    if key in config:
        return config[key]
    else:
        raise KeyError(message)


def get_source_sync_mode(stream_config: Dict, stream_name: str) -> SyncMode:
    """
    Read the source sync_mode field from config or return a default value if not found
    """
    if "sync_mode" in stream_config:
        sync_mode = get_field(stream_config, "sync_mode", "")
    else:
        sync_mode = ""
    try:
        result = SyncMode(sync_mode)
    except ValueError as e:
        # Fallback to default source sync mode value
        result = SyncMode.full_refresh
        print(f"WARN: Source sync mode falling back to {result} for {stream_name}: {e}")
    return result


def get_destination_sync_mode(stream_config: Dict, stream_name: str) -> DestinationSyncMode:
    """
    Read the destination_sync_mode field from config or return a default value if not found
    """
    if "destination_sync_mode" in stream_config:
        dest_sync_mode = get_field(stream_config, "destination_sync_mode", "")
    else:
        dest_sync_mode = ""
    try:
        result = DestinationSyncMode(dest_sync_mode)
    except ValueError as e:
        # Fallback to default destination sync mode value
        result = DestinationSyncMode.append
        print(f"WARN: Destination sync mode falling back to {result} for {stream_name}: {e}")
    return result


def add_table_to_sources(schema_to_source_tables: Dict[str, Set[str]], schema_name: str, table_name: str):
    """
    Keeps track of source tables used in this catalog to build a source.yaml file for DBT
    """
    if schema_name not in schema_to_source_tables:
        schema_to_source_tables[schema_name] = set()
    if table_name not in schema_to_source_tables[schema_name]:
        schema_to_source_tables[schema_name].add(table_name)
    else:
        raise KeyError(f"Duplicate table {table_name} in {schema_name}")


def output_sql_file(file: str, sql: str):
    """
    @param file is the path to filename to be written
    @param sql is the dbt sql content to be written in the generated model file
    """
    output_dir = os.path.dirname(file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(file, "w") as f:
        for line in sql.splitlines():
            if line.strip():
                f.write(line + "\n")
        f.write("\n")
