#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
from io import IOBase
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple, Union

import pandas as pd
from airbyte_cdk.sources.file_based.config.file_based_stream_config import ExcelFormat, FileBasedStreamConfig
from airbyte_cdk.sources.file_based.exceptions import ConfigValidationError, FileBasedSourceError, RecordParseError
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader, FileReadMode
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.schema_helpers import SchemaType
from numpy import datetime64
from numpy import dtype as dtype_
from numpy import issubdtype
from orjson import orjson
from pydantic.v1 import BaseModel


class ExcelParser(FileTypeParser):
    ENCODING = None

    def check_config(self, config: FileBasedStreamConfig) -> Tuple[bool, Optional[str]]:
        """
        ExcelParser does not require config checks, implicit pydantic validation is enough.
        """
        return True, None

    async def infer_schema(
        self,
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
    ) -> SchemaType:
        """
        Infers the schema of the Excel file by examining its contents.

        Args:
            config (FileBasedStreamConfig): Configuration for the file-based stream.
            file (RemoteFile): The remote file to be read.
            stream_reader (AbstractFileBasedStreamReader): Reader to read the file.
            logger (logging.Logger): Logger for logging information and errors.

        Returns:
            SchemaType: Inferred schema of the Excel file.
        """

        # Validate the format of the config
        self.validate_format(config.format, logger)

        fields: Dict[str, str] = {}

        with stream_reader.open_file(file, self.file_read_mode, self.ENCODING, logger) as fp:
            df = self.open_and_parse_file(fp)
            for column, df_type in df.dtypes.items():
                # Choose the broadest data type if the column's data type differs in dataframes
                prev_frame_column_type = fields.get(column)
                fields[column] = self.dtype_to_json_type(prev_frame_column_type, df_type)

        schema = {
            field: ({"type": "string", "format": "date-time"} if fields[field] == "date-time" else {"type": fields[field]})
            for field in fields
        }
        return schema

    def parse_records(
        self,
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
        discovered_schema: Optional[Mapping[str, SchemaType]] = None,
    ) -> Iterable[Dict[str, Any]]:
        """
        Parses records from an Excel file based on the provided configuration.

        Args:
            config (FileBasedStreamConfig): Configuration for the file-based stream.
            file (RemoteFile): The remote file to be read.
            stream_reader (AbstractFileBasedStreamReader): Reader to read the file.
            logger (logging.Logger): Logger for logging information and errors.
            discovered_schema (Optional[Mapping[str, SchemaType]]): Discovered schema for validation.

        Yields:
            Iterable[Dict[str, Any]]: Parsed records from the Excel file.
        """

        # Validate the format of the config
        self.validate_format(config.format, logger)

        try:
            # Open and parse the file using the stream reader
            with stream_reader.open_file(file, self.file_read_mode, self.ENCODING, logger) as fp:
                df = self.open_and_parse_file(fp)
                # Yield records as dictionaries
                # DataFrame.to_dict() method returns datetime values in pandas.Timestamp values, which are not serializable by orjson
                # DataFrame.to_json() returns string with datetime values serialized to iso8601 with microseconds to align with pydantic behavior
                # see PR description: https://github.com/airbytehq/airbyte/pull/44444/
                yield from orjson.loads(df.to_json(orient="records", date_format="iso", date_unit="us"))

        except Exception as exc:
            # Raise a RecordParseError if any exception occurs during parsing
            raise RecordParseError(FileBasedSourceError.ERROR_PARSING_RECORD, filename=file.uri) from exc

    @property
    def file_read_mode(self) -> FileReadMode:
        """
        Returns the file read mode for the Excel file.

        Returns:
            FileReadMode: The file read mode (binary).
        """
        return FileReadMode.READ_BINARY

    @staticmethod
    def dtype_to_json_type(current_type: Optional[str], dtype: dtype_) -> str:
        """
        Convert Pandas DataFrame types to Airbyte Types.

        Args:
            current_type (Optional[str]): One of the previous types based on earlier dataframes.
            dtype: Pandas DataFrame type.

        Returns:
            str: Corresponding Airbyte Type.
        """
        number_types = ("int64", "float64")
        if current_type == "string":
            # Previous column values were of the string type, no need to look further.
            return current_type
        if dtype == object:
            return "string"
        if dtype in number_types and (not current_type or current_type == "number"):
            return "number"
        if dtype == "bool" and (not current_type or current_type == "boolean"):
            return "boolean"
        if issubdtype(dtype, datetime64):
            return "date-time"
        return "string"

    @staticmethod
    def validate_format(excel_format: BaseModel, logger: logging.Logger) -> None:
        """
        Validates if the given format is of type ExcelFormat.

        Args:
            excel_format (Any): The format to be validated.

        Raises:
            ConfigValidationError: If the format is not ExcelFormat.
        """
        if not isinstance(excel_format, ExcelFormat):
            logger.info(f"Expected ExcelFormat, got {excel_format}")
            raise ConfigValidationError(FileBasedSourceError.CONFIG_VALIDATION_ERROR)

    @staticmethod
    def open_and_parse_file(fp: Union[IOBase, str, Path]) -> pd.DataFrame:
        """
        Opens and parses the Excel file.

        Args:
            fp: File pointer to the Excel file.

        Returns:
            pd.DataFrame: Parsed data from the Excel file.
        """
        return pd.ExcelFile(fp, engine="calamine").parse()
