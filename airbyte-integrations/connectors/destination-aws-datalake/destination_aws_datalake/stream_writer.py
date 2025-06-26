#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
from datetime import date, datetime
from decimal import Decimal, getcontext
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd

from airbyte_cdk.models import ConfiguredAirbyteStream, DestinationSyncMode

from .aws import AwsHandler
from .config_reader import ConnectorConfig, PartitionOptions
from .constants import EMPTY_VALUES, GLUE_TYPE_MAPPING_DECIMAL, GLUE_TYPE_MAPPING_DOUBLE, PANDAS_TYPE_MAPPING


# By default we set glue decimal type to decimal(28,25)
# this setting matches that precision.
getcontext().prec = 25
logger = logging.getLogger("airbyte")


class DictEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)

        if isinstance(obj, (pd.Timestamp, datetime)):
            # all timestamps and datetimes are converted to UTC
            return obj.strftime("%Y-%m-%dT%H:%M:%SZ")

        if isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")

        return super(DictEncoder, self).default(obj)


class StreamWriter:
    def __init__(self, aws_handler: AwsHandler, config: ConnectorConfig, configured_stream: ConfiguredAirbyteStream) -> None:
        self._aws_handler: AwsHandler = aws_handler
        self._config: ConnectorConfig = config
        self._configured_stream: ConfiguredAirbyteStream = configured_stream
        self._schema: Dict[str, Any] = configured_stream.stream.json_schema["properties"]
        self._sync_mode: DestinationSyncMode = configured_stream.destination_sync_mode

        self._table_exists: bool = False
        self._table: str = configured_stream.stream.name
        self._database: str = self._configured_stream.stream.namespace or self._config.lakeformation_database_name

        self._messages = []
        self._partial_flush_count = 0

        logger.info(f"Creating StreamWriter for {self._database}:{self._table}")

    def _get_date_columns(self) -> List[str]:
        date_columns = []
        for key, val in self._schema.items():
            typ = val.get("type")
            typ = self._get_json_schema_type(typ)
            if isinstance(typ, str) and typ == "string":
                if val.get("format") in ["date-time", "date"]:
                    date_columns.append(key)

        return date_columns

    def _add_partition_column(self, col: str, df: pd.DataFrame) -> Dict[str, str]:
        partitioning = self._config.partitioning

        if partitioning == PartitionOptions.NONE:
            return {}

        partitions = partitioning.value.split("/")

        fields = {}
        for partition in partitions:
            date_col = f"{col}_{partition.lower()}"
            fields[date_col] = "bigint"

            # defaulting to 0 since both governed tables
            # and pyarrow don't play well with __HIVE_DEFAULT_PARTITION__
            # - pyarrow will fail to cast the column to any other type than string
            # - governed tables will fail when trying to query a table with partitions that have __HIVE_DEFAULT_PARTITION__
            # aside from the above, awswrangler will remove data from a table if the partition value is null
            # see: https://github.com/aws/aws-sdk-pandas/issues/921
            if partition == "YEAR":
                df[date_col] = df[col].dt.strftime("%Y").fillna("0").astype("Int64")

            elif partition == "MONTH":
                df[date_col] = df[col].dt.strftime("%m").fillna("0").astype("Int64")

            elif partition == "DAY":
                df[date_col] = df[col].dt.strftime("%d").fillna("0").astype("Int64")

            elif partition == "DATE":
                fields[date_col] = "date"
                df[date_col] = df[col].dt.strftime("%Y-%m-%d")

        return fields

    def _drop_additional_top_level_properties(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Helper that removes any unexpected top-level properties from the record.
        Since the json schema is used to build the table and cast types correctly,
        we need to remove any unexpected properties that can't be casted accurately.
        """
        schema_keys = self._schema.keys()
        records_keys = record.keys()
        difference = list(set(records_keys).difference(set(schema_keys)))

        for key in difference:
            del record[key]

        return record

    def _json_schema_cast_value(self, value, schema_entry) -> Any:
        typ = schema_entry.get("type")
        typ = self._get_json_schema_type(typ)
        props = schema_entry.get("properties")
        items = schema_entry.get("items")

        if typ == "string":
            format = schema_entry.get("format")
            if format == "date-time":
                return pd.to_datetime(value, errors="coerce", utc=True)

            return str(value) if value and value != "" else None

        elif typ == "integer":
            return pd.to_numeric(value, errors="coerce")

        elif typ == "number":
            if self._config.glue_catalog_float_as_decimal:
                return Decimal(str(value)) if value else Decimal("0")
            return pd.to_numeric(value, errors="coerce")

        elif typ == "boolean":
            return bool(value)

        elif typ == "null":
            return None

        elif typ == "object":
            if value in EMPTY_VALUES:
                return None

            if isinstance(value, dict) and props:
                for key, val in value.items():
                    if key in props:
                        value[key] = self._json_schema_cast_value(val, props[key])
                return value

        elif typ == "array" and items:
            if value in EMPTY_VALUES:
                return None

            if isinstance(value, list):
                return [self._json_schema_cast_value(item, items) for item in value]

        return value

    def _json_schema_cast(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Helper that fixes obvious type violations in a record's top level keys that may
        cause issues when casting data to pyarrow types. Such as:
        - Objects having empty strings or " " or "-" as value instead of null or {}
        - Arrays having empty strings or " " or "-" as value instead of null or []
        """
        for key, schema_type in self._schema.items():
            typ = self._schema[key].get("type")
            typ = self._get_json_schema_type(typ)
            record[key] = self._json_schema_cast_value(record.get(key), schema_type)

        return record

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

    def _get_json_schema_type(self, types: Union[List[str], str]) -> str:
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
        column_types = {}

        typ = "string"
        for col in df.columns:
            if col in self._schema:
                typ = self._schema[col].get("type", "string")
                airbyte_type = self._schema[col].get("airbyte_type")

                # special case where the json schema type contradicts the airbyte type
                if airbyte_type and typ == "number" and airbyte_type == "integer":
                    typ = "integer"

                typ = self._get_json_schema_type(typ)

            column_types[col] = PANDAS_TYPE_MAPPING.get(typ, "string")

        return column_types

    def _get_json_schema_types(self) -> Dict[str, str]:
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

    def _get_glue_dtypes_from_json_schema(self, schema: Dict[str, Any]) -> Tuple[Dict[str, str], List[str]]:
        """
        Helper that infers glue dtypes from a json schema.
        """
        type_mapper = GLUE_TYPE_MAPPING_DECIMAL if self._config.glue_catalog_float_as_decimal else GLUE_TYPE_MAPPING_DOUBLE

        column_types = {}
        json_columns = set()
        for col, definition in schema.items():
            result_typ = None
            col_typ = definition.get("type")
            airbyte_type = definition.get("airbyte_type")
            col_format = definition.get("format")

            col_typ = self._get_json_schema_type(col_typ)

            # special case where the json schema type contradicts the airbyte type
            if airbyte_type and col_typ == "number" and airbyte_type == "integer":
                col_typ = "integer"

            if col_typ == "string" and col_format == "date-time":
                result_typ = "timestamp"

            if col_typ == "string" and col_format == "date":
                result_typ = "date"

            if col_typ == "object":
                properties = definition.get("properties")
                allow_additional_properties = definition.get("additionalProperties", False)
                if properties and not allow_additional_properties and self._is_invalid_struct_or_array(properties):
                    object_props, _ = self._get_glue_dtypes_from_json_schema(properties)
                    result_typ = f"struct<{','.join([f'{k}:{v}' for k, v in object_props.items()])}>"
                else:
                    json_columns.add(col)
                    result_typ = "string"

            if col_typ == "array":
                items = definition.get("items", {})

                if isinstance(items, list):
                    items = items[0]

                raw_item_type = items.get("type")
                airbyte_raw_item_type = items.get("airbyte_type")

                # special case where the json schema type contradicts the airbyte type
                if airbyte_raw_item_type and raw_item_type == "number" and airbyte_raw_item_type == "integer":
                    raw_item_type = "integer"

                item_type = self._get_json_schema_type(raw_item_type)
                item_properties = items.get("properties")

                # if array has no "items", cast to string
                if not items:
                    json_columns.add(col)
                    result_typ = "string"

                # if array with objects
                elif isinstance(items, dict) and item_properties:
                    # Check if nested object has properties and no mixed type objects
                    if self._is_invalid_struct_or_array(item_properties):
                        item_dtypes, _ = self._get_glue_dtypes_from_json_schema(item_properties)
                        inner_struct = f"struct<{','.join([f'{k}:{v}' for k, v in item_dtypes.items()])}>"
                        result_typ = f"array<{inner_struct}>"
                    else:
                        json_columns.add(col)
                        result_typ = "string"

                elif item_type and self._json_schema_type_has_mixed_types(raw_item_type):
                    json_columns.add(col)
                    result_typ = "string"

                # array with single type
                elif item_type and not self._json_schema_type_has_mixed_types(raw_item_type):
                    result_typ = f"array<{type_mapper[item_type]}>"

            if result_typ is None:
                result_typ = type_mapper.get(col_typ, "string")

            column_types[col] = result_typ

        return column_types, json_columns

    @property
    def _cursor_fields(self) -> Optional[List[str]]:
        return self._configured_stream.cursor_field

    def append_message(self, message: Dict[str, Any]):
        clean_message = self._drop_additional_top_level_properties(message)
        clean_message = self._json_schema_cast(clean_message)
        self._messages.append(clean_message)

    def reset(self):
        logger.info(f"Deleting table {self._database}:{self._table}")
        success = self._aws_handler.delete_table(self._database, self._table)

        if not success:
            logger.warning(f"Failed to reset table {self._database}:{self._table}")

    def flush(self, partial: bool = False):
        logger.debug(f"Flushing {len(self._messages)} messages to table {self._database}:{self._table}")

        df = pd.DataFrame(self._messages)
        # best effort to convert pandas types
        df = df.astype(self._get_pandas_dtypes_from_json_schema(df), errors="ignore")

        if len(df) < 1:
            logger.info(f"No messages to write to {self._database}:{self._table}")
            return

        partition_fields = {}
        date_columns = self._get_date_columns()
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], format="mixed", utc=True)

                # Create date column for partitioning
                if self._cursor_fields and col in self._cursor_fields:
                    fields = self._add_partition_column(col, df)
                    partition_fields.update(fields)

        dtype, json_casts = self._get_glue_dtypes_from_json_schema(self._schema)
        dtype = {**dtype, **partition_fields}
        partition_fields = list(partition_fields.keys())

        # Make sure complex types that can't be converted
        # to a struct or array are converted to a json string
        # so they can be queried with json_extract
        for col in json_casts:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: json.dumps(x, cls=DictEncoder))

        if self._sync_mode == DestinationSyncMode.overwrite and self._partial_flush_count < 1:
            logger.debug(f"Overwriting {len(df)} records to {self._database}:{self._table}")
            self._aws_handler.write(
                df,
                self._database,
                self._table,
                dtype,
                partition_fields,
            )

        elif self._sync_mode == DestinationSyncMode.append or self._partial_flush_count > 0:
            logger.debug(f"Appending {len(df)} records to {self._database}:{self._table}")
            self._aws_handler.append(
                df,
                self._database,
                self._table,
                dtype,
                partition_fields,
            )

        else:
            self._messages = []
            raise Exception(f"Unsupported sync mode: {self._sync_mode}")

        if partial:
            self._partial_flush_count += 1

        del df
        self._messages.clear()
