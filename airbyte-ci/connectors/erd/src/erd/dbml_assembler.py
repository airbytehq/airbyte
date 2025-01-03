# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from pathlib import Path
from typing import List, Set, Union

import yaml
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import (
    ManifestReferenceResolver,
)
from airbyte_protocol.models import (  # type: ignore  # missing library stubs or py.typed marker
    AirbyteCatalog,
    AirbyteStream,
)
from pydbml import Database  # type: ignore  # missing library stubs or py.typed marker
from pydbml.classes import (  # type: ignore  # missing library stubs or py.typed marker
    Column,
    Index,
    Reference,
    Table,
)

from erd.relationships import Relationships


class Source:
    def __init__(self, source_folder: Path, source_technical_name: str) -> None:
        self._source_folder = source_folder
        self._source_technical_name = source_technical_name

    def is_dynamic(self, stream_name: str) -> bool:
        """
        This method is a very flaky heuristic to know if a stream is dynamic or not. A stream will be considered dynamic if:
        * The stream name is in the schemas folder
        * The stream is within the manifest and the schema definition is `InlineSchemaLoader`
        """
        manifest_static_streams = set()
        if self._has_manifest():
            with open(self._get_manifest_path()) as manifest_file:
                resolved_manifest = ManifestReferenceResolver().preprocess_manifest(
                    yaml.safe_load(manifest_file)
                )
            for stream in resolved_manifest["streams"]:
                if "schema_loader" not in stream:
                    # stream is assumed to have `DefaultSchemaLoader` which will show in the schemas folder so we can skip
                    continue
                if stream["schema_loader"]["type"] == "InlineSchemaLoader":
                    name = (
                        stream["name"]
                        if "name" in stream
                        else stream.get("$parameters").get("name", None)
                    )
                    if not name:
                        print(f"Could not retrieve name for this stream: {stream}")
                        continue
                    manifest_static_streams.add(
                        stream["name"]
                        if "name" in stream
                        else stream.get("$parameters").get("name", None)
                    )

        return (
            stream_name
            not in manifest_static_streams | self._get_streams_from_schemas_folder()
        )

    def _get_streams_from_schemas_folder(self) -> Set[str]:
        schemas_folder = (
            self._source_folder
            / self._source_technical_name.replace("-", "_")
            / "schemas"
        )
        return (
            {
                p.name.replace(".json", "")
                for p in schemas_folder.iterdir()
                if p.is_file()
            }
            if schemas_folder.exists()
            else set()
        )

    def _get_manifest_path(self) -> Path:
        return (
            self._source_folder
            / self._source_technical_name.replace("-", "_")
            / "manifest.yaml"
        )

    def _has_manifest(self) -> bool:
        return self._get_manifest_path().exists()


class DbmlAssembler:
    def assemble(
        self,
        source: Source,
        discovered_catalog: AirbyteCatalog,
        relationships: Relationships,
    ) -> Database:
        database = Database()
        for stream in discovered_catalog.streams:
            if source.is_dynamic(stream.name):
                print(f"Skipping stream {stream.name} as it is dynamic")
                continue

            database.add(self._create_table(stream))

        self._add_references(source, database, relationships)

        return database

    def _create_table(self, stream: AirbyteStream) -> Table:
        dbml_table = Table(stream.name)
        for property_name, property_information in stream.json_schema.get(
            "properties"
        ).items():
            try:
                dbml_table.add_column(
                    Column(
                        name=property_name,
                        type=self._extract_type(property_information["type"]),
                        pk=self._is_pk(stream, property_name),
                    )
                )
            except (KeyError, ValueError) as exception:
                print(f"Ignoring field {property_name}: {exception}")
                continue

        if (
            stream.source_defined_primary_key
            and len(stream.source_defined_primary_key) > 1
        ):
            if any(map(lambda key: len(key) != 1, stream.source_defined_primary_key)):
                raise ValueError(
                    f"Does not support nested key as part of primary key `{stream.source_defined_primary_key}`"
                )

            composite_key_columns = [
                column
                for key in stream.source_defined_primary_key
                for column in dbml_table.columns
                if column.name in key
            ]
            if len(composite_key_columns) < len(stream.source_defined_primary_key):
                raise ValueError("Unexpected error: missing PK column from dbml table")

            dbml_table.add_index(
                Index(
                    subjects=composite_key_columns,
                    pk=True,
                )
            )
        return dbml_table

    def _add_references(
        self, source: Source, database: Database, relationships: Relationships
    ) -> None:
        for stream in relationships["streams"]:
            for column_name, relationship in stream["relations"].items():
                if source.is_dynamic(stream["name"]):
                    print(
                        f"Skipping relationship as stream {stream['name']} from relationship is dynamic"
                    )
                    continue

                try:
                    target_table_name, target_column_name = relationship.split(
                        ".", 1
                    )  # we support the field names having dots but not stream name hence we split on the first dot only
                except ValueError as exception:
                    raise ValueError(
                        f"Could not handle relationship {relationship}"
                    ) from exception

                if source.is_dynamic(target_table_name):
                    print(
                        f"Skipping relationship as target stream {target_table_name} is dynamic"
                    )
                    continue

                try:
                    database.add_reference(
                        Reference(
                            type="<>",  # we don't have the information of which relationship type it is so we assume many-to-many for now
                            col1=self._get_column(
                                database, stream["name"], column_name
                            ),
                            col2=self._get_column(
                                database, target_table_name, target_column_name
                            ),
                        )
                    )
                except ValueError as exception:
                    print(f"Skipping relationship: {exception}")

    def _extract_type(self, property_type: Union[str, List[str]]) -> str:
        if isinstance(property_type, str):
            return property_type

        types = list(property_type)
        if "null" in types:
            # As we flag everything as nullable (except PK and cursor field), there is little value in keeping the information in order to
            # show this in DBML
            types.remove("null")
        if len(types) != 1:
            raise ValueError(
                f"Expected only one type apart from `null` but got {len(types)}: {property_type}"
            )
        return types[0]

    def _is_pk(self, stream: AirbyteStream, property_name: str) -> bool:
        return stream.source_defined_primary_key == [[property_name]]

    def _get_column(
        self, database: Database, table_name: str, column_name: str
    ) -> Column:
        matching_tables = list(
            filter(lambda dbml_table: dbml_table.name == table_name, database.tables)
        )
        if len(matching_tables) == 0:
            raise ValueError(f"Could not find table {table_name}")
        elif len(matching_tables) > 1:
            raise ValueError(
                f"Unexpected error: many tables found with name {table_name}"
            )

        table: Table = matching_tables[0]
        matching_columns = list(
            filter(lambda column: column.name == column_name, table.columns)
        )
        if len(matching_columns) == 0:
            raise ValueError(
                f"Could not find column {column_name} in table {table_name}. Columns are: {table.columns}"
            )
        elif len(matching_columns) > 1:
            raise ValueError(
                f"Unexpected error: many columns found with name {column_name} for table {table_name}"
            )

        return matching_columns[0]
