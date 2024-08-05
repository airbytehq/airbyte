import argparse
import json
from typing import Union, List

from airbyte_protocol.models import AirbyteCatalog, AirbyteStream
from pydbml import Database
from pydbml.classes import Column, Index, Reference, Table
from pydbml.renderer.dbml.default import DefaultDBMLRenderer


def _get_catalog(catalog_path: str) -> AirbyteCatalog:
    with open(catalog_path, "r") as file:
        try:
            return AirbyteCatalog.parse_obj(json.loads(file.read())["catalog"])
        except json.JSONDecodeError as error:
            raise ValueError(f"Could not read json file {catalog_path}: {error}. Please ensure that it is a valid JSON.")


def _get_relationships_by_stream(schema_relationships_path: str):
    with open(schema_relationships_path, "r") as file:
        return json.load(file)["streams"]


def _extract_type(property_type: Union[str, List[str]]) -> str:
    if isinstance(property_type, str):
        return property_type

    types = list(property_type)
    if "null" in types:
        # As we flag everything as nullable (except PK and cursor field), there is little value in keeping the information in order to show
        # this in DBML
        types.remove("null")
    if len(types) != 1:
        raise ValueError(f"Expected only one type apart from `null` but got {len(types)}: {property_type}")
    return types[0]


def _is_pk(stream: AirbyteStream, property_name: str) -> bool:
    return stream.source_defined_primary_key == [property_name]


def _has_composite_key(stream: AirbyteStream) -> bool:
    return len(stream.source_defined_primary_key) > 1


def _get_column(database: Database, table_name: str, column_name: str) -> Column:
    matching_tables = list(filter(lambda table: table.name == table_name, database.tables))
    if len(matching_tables) == 0:
        raise ValueError(f"Could not find table {table_name}")
    elif len(matching_tables) > 1:
        raise ValueError(f"Unexpected error: many tables found with name {table_name}")

    table: Table = matching_tables[0]
    matching_columns = list(filter(lambda column: column.name == column_name, table.columns))
    if len(matching_columns) == 0:
        raise ValueError(f"Could not find column {column_name} in table {table_name}. Columns are: {table.columns}")
    elif len(matching_columns) > 1:
        raise ValueError(f"Unexpected error: many columns found with name {column_name} for table {table_name}")

    return matching_columns[0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="dbml generator",
        description="From a discover output and a relationship file, generate a dbml file"
    )

    parser.add_argument("-d", "--discover-output")
    parser.add_argument("-r", "--schema-relationships")

    arguments = parser.parse_args()

    catalog = _get_catalog(arguments.discover_output)

    database = Database() # FIXME pass source name as a parameter
    for stream in catalog.streams:
        dbml_table = Table(stream.name)
        for property_name, property_information in stream.json_schema.get("properties").items():
            dbml_table.add_column(
                Column(
                    name=property_name,
                    type=_extract_type(property_information["type"]),
                    pk=_is_pk(stream, property_name),
                )
            )

        if stream.source_defined_primary_key and len(stream.source_defined_primary_key) > 1:
            if any(map(lambda key: len(key) != 1, stream.source_defined_primary_key)):
                raise ValueError(f"Does not support nested key as part of primary key `{stream.source_defined_primary_key}`")

            composite_key_columns = [column for key in stream.source_defined_primary_key for column in dbml_table.columns if column.name in key]
            if len(composite_key_columns) < len(stream.source_defined_primary_key):
                raise ValueError("Unexpected error: missing PK column from dbml table")

            dbml_table.add_index(
                Index(
                    subjects=composite_key_columns,
                    pk=True,
                )
            )
        database.add(dbml_table)

    for stream in _get_relationships_by_stream(arguments.schema_relationships):
        for column_name, relationship in stream["relations"].items():
            try:
                target_table_name, target_column_name = relationship.split(".")
            except ValueError as exception:
                raise ValueError("If 'too many values to unpack', relationship to nested fields is not supported") from exception

            database.add_reference(
                Reference(
                    type="<>",  # we don't have the information of which relationship type it is so we assume many-to-many for now
                    col1=_get_column(database, stream["name"], column_name),
                    col2=_get_column(database, target_table_name, target_column_name),
                )
            )

    # to publish this dbml file to dbdocs, use `DBDOCS_TOKEN=<token> dbdocs build source.dbml --project=<source>`
    with open("source.dbml", "w") as f:
        f.write(DefaultDBMLRenderer.render_db(database))
