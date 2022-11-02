#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
import pandas as pd

from typing import Dict, Any, Optional, List, Union
from destination_aws_datalake.config_reader import ConnectorConfig, PartitionOptions
from airbyte_cdk.models import DestinationSyncMode, ConfiguredAirbyteStream

from .aws import AwsHandler

logger = logging.getLogger("airbyte")


class StreamWriter:
    def __init__(self, aws_handler: AwsHandler, config: ConnectorConfig, configured_stream: ConfiguredAirbyteStream):
        self._aws_handler: AwsHandler = aws_handler
        self._config: ConnectorConfig = config
        self._configured_stream: ConfiguredAirbyteStream = configured_stream
        self._schema: Dict[str, Any] = configured_stream.stream.json_schema["properties"]
        self._sync_mode: DestinationSyncMode = configured_stream.destination_sync_mode

        self._table_exists: bool = False
        self._table: str = configured_stream.stream.name
        self._database: str = self._configured_stream.stream.namespace or self._config.lakeformation_database_name

        self._messages = []

        logger.info(f"Creating StreamWriter for {self._database}:{self._table}")

    def _get_path(self) -> str:
        bucket = f"s3://{self._config.bucket_name}"
        if self._config.bucket_prefix:
            bucket += f"/{self._config.bucket_prefix}"

        return f"{bucket}/{self._database}/{self._table}/"

    def _get_date_columns(self) -> list:
        date_columns = []
        for key, val in self._schema.items():
            typ = val.get("type")
            if (isinstance(typ, str) and typ == "string") or (isinstance(typ, list) and "string" in typ):
                if val.get("format") in ["date-time", "date"]:
                    date_columns.append(key)

        return date_columns

    def _add_partition_column(self, col: str, df: pd.DataFrame) -> list:
        partitioning = self._config.partitioning

        if partitioning == PartitionOptions.NONE:
            return []

        partitions = partitioning.value.split("/")

        fields = []
        for partition in partitions:
            date_col = f"{col}_{partition.lower()}"
            if partition == "YEAR":
                df[date_col] = df[col].dt.year

            elif partition == "MONTH":
                df[date_col] = df[col].dt.month

            elif partition == "DAY":
                df[date_col] = df[col].dt.day

            elif partition == "DATE":
                df[date_col] = df[col].dt.date

            fields.append(date_col)

        return fields

    def _get_non_null_json_schema_types(self, typ: Union[str, List[str]]) -> Union[str, List[str]]:
        if isinstance(typ, list):
            return list(filter(lambda x: x != "null", typ))

        return typ

    def _json_schema_type_has_mixed_types(self, typ: Union[str, List[str]]) -> bool:
        if isinstance(typ, list):
            typ = self._get_non_null_json_schema_types(typ)
            if len(typ) > 1:
                return True

        return False

    def _get_json_schema_type(self, types: Union[List[str], str] ) -> str:
        if isinstance(types, str):
            return types

        if not isinstance(types, list):
            return "string"

        types = self._get_non_null_json_schema_types(types)
        # when multiple types, cast to string
        if self._json_schema_type_has_mixed_types(types):
            return "string"

        return types[0]

    def _get_pandas_dtypes_from_json_schema(self, df: pd.DataFrame) -> Dict[str, str]:
        type_mapper = {
            "string": "string",
            "integer": "int64",
            "number": "float64",
            "boolean": "bool",
            "object": "object",
            "array": "object",
        }

        column_types = {}

        typ = "string"
        for col in df.columns:
            if col in self._schema:
                typ = self._schema[col].get("type", "string")
                typ = self._get_json_schema_type(typ)

            column_types[col] = type_mapper.get(typ, "string")

        return column_types

    def _get_json_schema_types(self):
        types = {}
        for key, val in self._schema.items():
            typ = val.get("type")
            types[key] = self._get_json_schema_type(typ)
        return types

    def _is_invalid_struct_or_array(self, schema: Dict[str, Any]) -> bool:
        """
        Helper that detects issues with nested objects/arrays in the json schema.
        When a complex data type is detected (schema with oneOf) or a nested object without properties
        the columns' dtype will be casted to string to avoid pyarrow conversion issues.
        """
        result = True
        def check_properties(schema):
            nonlocal result
            for val in schema.values():
                # Complex types can't be casted to an athena/glue type
                if val.get("oneOf"):
                    result = False
                    continue

                raw_typ = val.get("type")

                # If the type is a list, check for mixed types
                # complex objects with mixed types can't be reliably casted
                if isinstance(raw_typ, list) and self._json_schema_type_has_mixed_types(raw_typ):
                    result = False
                    continue

                typ = self._get_json_schema_type(raw_typ)

                # If object check nested properties
                if typ == "object":
                    properties = val.get("properties")
                    if not properties:
                        result = False
                    else:
                        check_properties(properties)

                # If array check nested properties
                if typ == "array":
                    items = val.get("items")

                    if not items:
                        result = False
                        continue

                    if isinstance(items, list):
                        items = items[0]

                    item_properties = items.get("properties")
                    if item_properties:
                        check_properties(item_properties)


        check_properties(schema)
        return result

    def _get_glue_dtypes_from_json_schema(self, schema: Dict[str, Any], nested: bool = False) -> Dict[str, str]:
        """
        Helper that infers glue dtypes from a json schema.
        """

        type_mapper = {
            "string": "string",
            "integer": "bigint",
            "number": "decimal(38, 18)" if self._config.glue_catalog_float_as_decimal else "double",
            "boolean": "boolean",
            "null": "string",
        }

        column_types = {}
        for (col, definition) in schema.items():

            result_typ = None
            col_typ = definition.get("type")
            col_format = definition.get("format")

            col_typ = self._get_json_schema_type(col_typ)

            if col_typ == "string" and col_format == "date-time":
                result_typ = "timestamp"

            if col_typ == "string" and col_format == "date":
                result_typ = "date"

            if col_typ == "object":
                properties = definition.get("properties")
                if properties and self._is_invalid_struct_or_array(properties):
                    object_props = self._get_glue_dtypes_from_json_schema(properties)
                    result_typ = f"struct<{','.join([f'{k}:{v}' for k, v in object_props.items()])}>"
                else:
                    result_typ = "string"

            if col_typ == "array":
                items = definition.get("items", {})
                if isinstance(items, list):
                    items = items[0]

                raw_item_type = items.get("type")
                item_type = self._get_json_schema_type(raw_item_type)
                item_properties = items.get("properties")

                if isinstance(items, dict) and item_properties:
                    # Check if nested object has properties and no mixed type objects
                    if self._is_invalid_struct_or_array(item_properties):
                        item_dtypes = self._get_glue_dtypes_from_json_schema(item_properties)
                        inner_struct = f"struct<{','.join([f'{k}:{v}' for k, v in item_dtypes.items()])}>"
                        result_typ = f"array<{inner_struct}>"
                    else:
                        result_typ = "string"

                elif item_type and self._json_schema_type_has_mixed_types(raw_item_type):
                    result_typ = "string"

                elif item_type and not self._json_schema_type_has_mixed_types(raw_item_type):
                    result_typ = f"array<{type_mapper[item_type]}>"

            if result_typ is None:
                result_typ = type_mapper.get(col_typ, "string")

            column_types[col] = result_typ

        return column_types


    @property
    def _cursor_fields(self) -> Optional[List[str]]:
        return self._configured_stream.cursor_field

    def append_message(self, message):
        self._messages.append(message)

    def reset(self):
        logger.info(f"Deleting table {self._database}:{self._table}")
        success = self._aws_handler.delete_table(self._database, self._table)

        if not success:
            raise Exception(f"Failed to reset table {self._database}:{self._table}")

    def flush(self, force_append=False):
        logger.debug(f"Flushing {len(self._messages)} messages to table {self._database}:{self._table}")

        df = pd.DataFrame(self._messages)
        # best effort to convert pandas types
        df = df.astype(self._get_pandas_dtypes_from_json_schema(df), errors="ignore")

        if len(df) < 1:
            logger.info(f"No messages to write to {self._database}:{self._table}")
            return

        partition_fields = []
        date_columns = self._get_date_columns()
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])

                # Create date column for partitioning
                if self._cursor_fields and col in self._cursor_fields:
                    fields = self._add_partition_column(col, df)
                    partition_fields.extend(fields)

        dtype = self._get_glue_dtypes_from_json_schema(self._schema)
        if self._sync_mode == DestinationSyncMode.overwrite and not force_append:
            logger.debug(f"Overwriting {len(df)} records to {self._database}:{self._table}")
            self._aws_handler.write(
                df,
                self._get_path(),
                self._database,
                self._table,
                dtype,
                partition_fields,
            )

        elif self._sync_mode == DestinationSyncMode.append or force_append:
            logger.debug(f"Appending {len(df)} records to {self._database}:{self._table}")
            self._aws_handler.append(
                df,
                self._get_path(),
                self._database,
                self._table,
                dtype,
                partition_fields,
            )

        else:
            self._messages = []
            raise Exception(f"Unsupported sync mode: {self._sync_mode}")

        del df
        self._messages.clear()
