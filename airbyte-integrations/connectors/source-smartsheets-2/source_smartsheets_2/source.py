#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import collections
import json
from datetime import datetime
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    Optional,
)

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    Status,
    SyncMode,
    Type,
)
from airbyte_cdk.sources import Source
from smartsheet.models.enums import ColumnType

from . import (
    api, 
    utils,
)

# This dictionary maps metadata fields to a tuple of the type of the field
# and a function that can yield the field value when given tne sheet,
# the row, and any extra arguments.
METADATA_MAPPING: dict[str, tuple[ColumnType, Callable[[Any], Optional[str]]]] = {
    "Folder ID": (
        ColumnType.TEXT_NUMBER,
        lambda sheet, row, kwargs: kwargs.get("folder_id"),
    ),
    "Sheet Path": (
        ColumnType.TEXT_NUMBER,
        lambda sheet, row, kwargs: kwargs.get("sheet_path"),
    ),
    "Sheet ID": (
        ColumnType.TEXT_NUMBER,
        lambda sheet, row, kwargs: str(sheet.id),
    ),
    "Sheet Name": (
        ColumnType.TEXT_NUMBER,
        lambda sheet, row, kwargs: sheet.name,
    ),
    "Sheet Created At": (
        ColumnType.DATETIME,
        lambda sheet, row, kwargs: sheet.created_at.isoformat(),
    ),
    "Sheet Modified At": (
        ColumnType.DATETIME,
        lambda sheet, row, kwargs: sheet.modified_at.isoformat(),
    ),
    "Sheet Permalink": (
        ColumnType.TEXT_NUMBER,
        lambda sheet, row, kwargs: sheet.permalink,
    ),
    "Sheet Version": (
        ColumnType.TEXT_NUMBER,
        lambda sheet, row, kwargs: str(sheet.version),
    ),
    "Row ID": (
        ColumnType.TEXT_NUMBER,
        lambda sheet, row, kwargs: str(row.id),
    ),
    "Row Created At": (
        ColumnType.DATETIME,
        lambda sheet, row, kwargs: row.created_at.isoformat(),
    ),
    "Row Created By": (
        ColumnType.TEXT_NUMBER,
        lambda sheet, row, kwargs: row.created_by.name,
    ),
    "Row Modified At": (
        ColumnType.DATETIME,
        lambda sheet, row, kwargs: row.modified_at.isoformat(),
    ),
    "Row Modified By": (
        ColumnType.TEXT_NUMBER,
        lambda sheet, row, kwargs: row.modified_by.name,
    ),
    "Row Permalink": (
        ColumnType.TEXT_NUMBER,
        lambda sheet, row, kwargs: row.permalink,
    ),
    "Row Number": (
        ColumnType.TEXT_NUMBER,
        lambda sheet, row, kwargs: str(row.row_number),
    ),
    "Row Version": (
        ColumnType.TEXT_NUMBER,
        lambda sheet, row, kwargs: str(row.version),
    ),
    "Row Parent ID": (
        ColumnType.TEXT_NUMBER,
        lambda sheet, row, kwargs: str(row.parent_id),
    ),
}


class SourceSmartsheets_2(Source):
    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the integration
            e.g: if a provided Smartsheet API token can be used to connect to the Smartsheet API.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this source, content of this json is as specified in
        the properties of the spec.yaml file

        :return: AirbyteConnectionStatus indicating a Success or Failure
        """
        try:
            logger.info("getting a client")
            client = api.get_client(config)
            logger.info("accessing the root folder")
            client.Folders.get_folder(config["root-folder-id"])
            for sheet_id in config["schema-sheet-ids"]:
                logger.info("accessing schema sheet with id: '%d'", sheet_id)
                client.Sheets.get_sheet(sheet_id)
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {str(e)}")

    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        """
        Returns an AirbyteCatalog representing the available streams and fields in this integration.
        Given a config with stream name, valid credentials, schema sheet IDs, and metadata fields;
        returns an Airbyte catalog where there is a single stream with the given name, whose schema
        is the union of the columns of the sheets from the given schema sheet IDs and the metadata fields.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this source, content of this json is as specified in
        the properties of the spec.yaml file

        :return: AirbyteCatalog is an object describing a list of all available streams in this source.
            A stream is an AirbyteStream object that includes:
            - its stream name (or table name in the case of Postgres)
            - json_schema providing the specifications of expected schema for this stream (a list of columns described
            by their names and types)
        """
        logger.info("getting a client")
        client = api.get_client(config)

        # Retrieve columns from given sheet IDs
        columns = {}  # maps column name to column type
        for curr_sheet_id in config["schema-sheet-ids"]:
            logger.info("processing sheet id: '%d'", curr_sheet_id)
            curr_sheet = client.Sheets.get_sheet(curr_sheet_id)
            for column in curr_sheet.columns:
                if column.title in columns:
                    columns[column.title] = utils.reconcile_types(columns[column.title], column.type.value)
                else:
                    columns[column.title] = column.type.value

        # Process type safety option
        if config.get("enforce-safe-types"):
            columns = {k: ColumnType.TEXT_NUMBER for k in columns.keys()}

        # Add metadata fields
        metadata_fields: list[str] = config.get("metadata-fields", [])
        if metadata_fields:
            metadata_cols = {col: METADATA_MAPPING[col][0] for col in metadata_fields}
            columns.update(metadata_cols)

        # Convert types
        columns = {col: utils.convert_column_type(col_type) for (col, col_type) in columns.items()}

        # Normalize schema if needed
        if config.get("column-name-normalization"):
            columns = {utils.normalize_column_name(col, config.get("column-name-normalization")): val for (col, val) in columns.items()}

        # Return results
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": columns,
        }
        stream = AirbyteStream(
            name=config["stream-name"],
            json_schema=json_schema,
            supported_sync_modes=[SyncMode.full_refresh],
        )
        return AirbyteCatalog(streams=[stream])

    def read(
        self, logger: AirbyteLogger, config: json, catalog: ConfiguredAirbyteCatalog, state: Dict[str, any]
    ) -> Generator[AirbyteMessage, None, None]:
        """
        Returns a generator of the AirbyteMessages generated by reading the source with the given configuration,
        catalog, and state.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this source, content of this json is as specified in
            the properties of the spec.yaml file
        :param catalog: The input catalog is a ConfiguredAirbyteCatalog which is almost the same as AirbyteCatalog
            returned by discover(), but
        in addition, it's been configured in the UI! For each particular stream and field, there may have been provided
        with extra modifications such as: filtering streams and/or columns out, renaming some entities, etc
        :param state: When a Airbyte reads data from a source, it might need to keep a checkpoint cursor to resume
            replication in the future from that saved checkpoint.
            This is the object that is provided with state from previous runs and avoid replicating the entire set of
            data everytime.

        :return: A generator that produces a stream of AirbyteRecordMessage contained in AirbyteMessage object.
        """
        # Process arguments
        configured_stream = catalog.streams[0]
        stream_name = configured_stream.stream.name
        schema_properties = configured_stream.stream.json_schema["properties"]
        include_patterns: Iterable[str] = config.get("include-patterns", [])
        exclude_patterns: Iterable[str] = config.get("exclude-patterns", [])

        # Get a client
        client = api.get_client(config)

        # Depth-first traversal of the Smartsheet file system, starting from the given root folder
        folder_stack: Iterable[tuple[int, Optional[tuple[str]]]] = collections.deque()
        folder_stack.append((config["root-folder-id"], None))

        while folder_stack:
            curr_folder_id, prev_path = folder_stack.pop()
            logger.info("requesting folder: '%d'", curr_folder_id)
            curr_folder = client.Folders.get_folder(curr_folder_id)
            # Some logic to make paths prettier
            # 'curr_path' is a tuple of path segments that laters gets converted to a 'pathlib.PurePath'
            # 'curr_path_str' is the representation that is mainly for logging, can also be used in the metadata
            if prev_path is None:
                curr_path = ("/",)
                curr_path_str = "/"
            else:
                curr_path = prev_path + (curr_folder.name,)
                curr_path_str = curr_path[0] + "/".join(curr_path[1:])
            logger.info("processing folder: '%s'", curr_path_str)

            # Filter subfolders
            matched_folders, unmatched_folders = utils.filter_folders_by_exclusion(
                ((subfolder, curr_path) for subfolder in curr_folder.folders), exclude_patterns
            )
            for subfolder, pattern in matched_folders:
                logger.info("subfolder excluded: '%s' -- matched pattern: '%s'", f"{curr_path_str}/{subfolder.name}", pattern)
            # Reverse iteration to extend the stack in lexical order
            for subfolder in reversed(unmatched_folders):
                folder_stack.append((subfolder.id, curr_path))

            # Filter sheets
            matched_sheets = utils.filter_sheets_by_inclusion(((sheet, curr_path) for sheet in curr_folder.sheets), include_patterns)
            sheet_ids: list[int] = [sheet.id for (sheet, _) in matched_sheets]
            for sheet, pattern in matched_sheets:
                logger.info("sheet included: '%s' -- matched pattern: '%s'", f"{curr_path_str}/{sheet.name}", pattern)

            # Process sheets
            for sheet_id in sheet_ids:
                sheet = client.Sheets.get_sheet(sheet_id)
                logger.info("processing sheet: '%s'", f"{curr_path_str}/{sheet.name}")
                columns: list[tuple[int, str]] = []
                # Get whatever columns from the schema are available
                for col_idx, column in enumerate(sheet.columns):
                    col_name = column.title if not config.get("column-name-normalization") else utils.normalize_column_name(column.title, config.get("column-name-normalization"))
                    if col_name in schema_properties:
                        columns.append((col_idx, col_name))

                # Process rows with the available columns and the metadata
                for row in sheet.rows:
                    metadata: dict[str, Any] = {
                        field: METADATA_MAPPING[field][1](
                            sheet,
                            row,
                            {
                                "folder_id": curr_folder_id,
                                "sheet_path": curr_path_str,
                            },
                        )
                        for field in config.get("metadata-fields", [])
                    }
                    if config.get("column-name-normalization"):
                        metadata = {utils.normalize_column_name(key, config.get("column-name-normalization")): val for (key, val) in metadata.items()}
                    data: dict[str, Any] = {}
                    for col_idx, col_name in columns:
                        data[col_name] = row.cells[col_idx].value
                    # Sometimes we get rows that are actually empty, skip those
                    if all(val is None for val in data.values()):
                        continue
                    data.update(metadata)
                    yield AirbyteMessage(
                        type=Type.RECORD,
                        record=AirbyteRecordMessage(stream=stream_name, data=data, emitted_at=int(datetime.now().timestamp()) * 1000),
                    )
