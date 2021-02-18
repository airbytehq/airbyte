"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import os
from typing import Dict, Set

import yaml
from normalization.destination_type import DestinationType
from normalization.transform_catalog.destination_name_transformer import DestinationNameTransformer
from normalization.transform_catalog.stream_processor import StreamProcessor


class CatalogProcessor:
    """
    Takes as input an AirbyteCatalog file (stored as Json Schema).
    Associated input raw data is expected to be stored in a staging area called "raw_schema".

    This processor reads the catalog file, extracts streams descriptions and transforms them to final tables in their
    targeted destination schema.

    This is relying on a StreamProcessor to handle the conversion of a stream to a table one at a time.
    """

    def __init__(self, output_directory: str, integration_type: DestinationType):
        """
        @param output_directory is the path to the directory where this processor should write the resulting SQL files (DBT models)
        @param integration_type is the destination type of warehouse
        """
        self.output_directory: str = output_directory
        self.integration_type: DestinationType = integration_type
        self.name_transformer: DestinationNameTransformer = DestinationNameTransformer(integration_type)

    def process(self, catalog_file: str, json_column_name: str, target_schema: str):
        """
        This method first build the top-level streams and in a second loop will go over the substreams that
        were nested. (breadth-first traversal)

        @param catalog_file input AirbyteCatalog file in JSON Schema describing the structure of the raw data
        @param json_column_name is the column name containing the JSON Blob with the raw data
        @param target_schema is the final schema where to output the final transformed data to
        """
        # Registry of all tables in all schemas
        tables_registry: Set[str] = set()
        # Registry of source tables in each schemas
        source_tables: Dict[str, Set[str]] = {}

        catalog = read_json(catalog_file)
        print(json.dumps(catalog, separators=(",", ":")))
        substreams = {}
        for configured_stream in get_field(catalog, "streams", "Invalid Catalog: 'streams' is not defined in Catalog"):
            stream_config = get_field(configured_stream, "stream", "Invalid Stream: 'stream' is not defined in Catalog streams")
            schema_name = self.name_transformer.normalize_schema_name(target_schema)
            raw_schema_name = self.name_transformer.normalize_schema_name(f"_airbyte_{target_schema}")
            stream_name = get_field(stream_config, "name", f"Invalid Stream: 'name' is not defined in stream: {str(stream_config)}")
            raw_table_name = self.name_transformer.normalize_table_name(f"_airbyte_raw_{stream_name}")

            message = f"'json_schema'.'properties' are not defined for stream {stream_name}"
            properties = get_field(get_field(stream_config, "json_schema", message), "properties", message)

            from_table = "source('{}', '{}')".format(schema_name, raw_table_name)

            # Check properties
            if not properties:
                raise EOFError("Invalid Catalog: Unexpected empty properties in catalog")

            add_table_to_sources(source_tables, schema_name, raw_table_name)

            stream_processor = StreamProcessor().init(
                stream_name=stream_name,
                output_directory=self.output_directory,
                integration_type=self.integration_type,
                raw_schema=raw_schema_name,
                schema=schema_name,
                json_column_name=f"'{json_column_name}'",
                properties=properties,
                tables_registry=tables_registry,
            )
            nested_processors = stream_processor.process(from_table)
            add_table_to_registry(tables_registry, stream_processor)
            if nested_processors and len(nested_processors) > 0:
                substreams.update(nested_processors)
        self.write_yaml_sources_file(source_tables)
        self.process_substreams(substreams, tables_registry)

    def process_substreams(self, substreams: Dict, tables_registry: Set[str]):
        """
        Handle nested stream/substream/children
        """
        while substreams:
            children = substreams.copy()
            substreams = {}
            for child in children:
                for substream in children[child]:
                    substream.tables_registry = tables_registry
                    nested_processors = substream.process(child)
                    add_table_to_registry(tables_registry, substream)
                    if nested_processors:
                        substreams.update(nested_processors)

    def write_yaml_sources_file(self, source_tables: Dict[str, Set[str]]):
        """
        Generate the sources.yaml file as described in https://docs.getdbt.com/docs/building-a-dbt-project/using-sources/
        """
        schemas = []
        for schema in source_tables:
            quoted_schema = self.name_transformer.needs_quotes(schema)
            tables = []
            for source in source_tables[schema]:
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
        with open(source_path, "w") as fh:
            fh.write(yaml.dump(source_config))


# Static Functions


def read_json(input_path: str) -> dict:
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


def add_table_to_sources(source_tables: Dict[str, Set[str]], schema_name: str, table_name: str):
    """
    Keeps track of source tables used in this catalog to build a source.yaml file for DBT
    """
    if schema_name not in source_tables:
        source_tables[schema_name] = set()
    if table_name not in source_tables[schema_name]:
        source_tables[schema_name].add(table_name)
    else:
        raise KeyError(f"Duplicate table {table_name} in {schema_name}")


def add_table_to_registry(tables_registry: Set[str], processor: StreamProcessor):
    """
    Keeps track of all table names created by this catalog, regardless of their destination schema

    @param tables_registry where all table names are recorded
    @param processor the processor that created tables as part of its process
    """
    for table_name in processor.local_registry:
        if table_name not in tables_registry:
            tables_registry.add(table_name)
        else:
            raise KeyError(f"Duplicate table {table_name}")
