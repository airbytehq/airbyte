#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
import re
from datetime import date, datetime
from decimal import Decimal, getcontext
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
import pyarrow as pa

from airbyte_cdk.models import ConfiguredAirbyteStream, DestinationSyncMode, FailureType
from airbyte_cdk.utils import AirbyteTracedException

from .aws import AwsHandler
from .config_reader import ConnectorConfig, PartitionOptions
from .constants import EMPTY_VALUES, GLUE_TYPE_MAPPING_DECIMAL, GLUE_TYPE_MAPPING_DOUBLE, PANDAS_TYPE_MAPPING


_PYARROW_COLUMN_RE = re.compile(r"Conversion failed for column ([^\s]+) with type")
_PYARROW_TYPE_HINT_RES: Tuple[re.Pattern, ...] = (
    re.compile(r"object of type <class '([^']+)'> cannot be converted to (\w+)"),
    re.compile(r"with type (\w+): tried to convert to (\w+)"),
)
_TARGET_TO_JSON_SCHEMA: Dict[str, Tuple[str, ...]] = {
    "int": ("integer", "number"),
    "int64": ("integer", "number"),
    "int32": ("integer", "number"),
    "double": ("number",),
    "float": ("number",),
    "float64": ("number",),
    "float32": ("number",),
    "string": ("string",),
    "str": ("string",),
    "bool": ("boolean",),
    "boolean": ("boolean",),
}


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

        try:
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
        except (pa.ArrowInvalid, pa.ArrowTypeError) as ex:
            raise self._build_type_mismatch_exception(df, ex) from ex

        if partial:
            self._partial_flush_count += 1

        del df

    def _build_type_mismatch_exception(self, df: pd.DataFrame, ex: Exception) -> AirbyteTracedException:
        """
        Build an `AirbyteTracedException` describing a pyarrow type-conversion failure.

        The underlying pyarrow error only names the top-level column (for example
        `Conversion failed for column properties with type object`). For nested
        struct/array columns that makes it hard to tell which specific subfield
        actually violated the declared schema. This helper parses the column name
        and (when present) the observed-Python-type / target-pyarrow-type pair
        out of the error, walks the offending column's values against the stream's
        JSON schema, and returns the first dotted field path whose value type does
        not match the declared type along with the observed Python type and the
        declared JSON Schema type.

        The walk is filtered to only return mismatches that match the
        `(observed, target)` types in the pyarrow message when those can be
        parsed, so that for example a `str -> int` failure does not get
        misattributed to an unrelated `Timestamp -> string` mismatch in the
        same struct. Falls back to the first mismatch if no filtered match is
        found.
        """
        err_msg = str(ex)
        column_match = _PYARROW_COLUMN_RE.search(err_msg)
        column = column_match.group(1) if column_match else None
        observed_filter, declared_filter = self._parse_pyarrow_type_hint(err_msg)

        bad_path: Optional[str] = None
        observed_type: Optional[str] = None
        declared_type: Optional[str] = None
        if column and column in df.columns and column in self._schema:
            values = df[column].tolist()
            schema_entry = self._schema[column]
            if observed_filter is not None or declared_filter is not None:
                bad_path, observed_type, declared_type = self._find_first_type_mismatch(
                    values,
                    schema_entry,
                    prefix=column,
                    observed_filter=observed_filter,
                    declared_filter=declared_filter,
                )
            if bad_path is None:
                bad_path, observed_type, declared_type = self._find_first_type_mismatch(values, schema_entry, prefix=column)

        if bad_path is not None:
            message = (
                f'Stream "{self._table}" field "{bad_path}" has values of type '
                f"{observed_type} that do not match declared type {declared_type}."
            )
        elif column is not None:
            message = f'Stream "{self._table}" column "{column}" has values that do not match the declared schema type.'
        else:
            message = f'Stream "{self._table}" produced values that cannot be converted to the declared schema types.'

        internal_message = (
            f"[stream={self._table} column={column} field={bad_path} "
            f"observed_type={observed_type} declared_type={declared_type}] "
            f"pyarrow conversion failed: {ex!r}"
        )
        return AirbyteTracedException(
            message=message,
            internal_message=internal_message,
            failure_type=FailureType.config_error,
        )

    @staticmethod
    def _parse_pyarrow_type_hint(err_msg: str) -> Tuple[Optional[str], Optional[Tuple[str, ...]]]:
        """
        Parse the observed Python type and the target conversion type out of a
        pyarrow error message. Returns `(observed_python_type_name, allowed_json_schema_types)`,
        where `allowed_json_schema_types` is a tuple of JSON Schema type names
        that the target pyarrow type could correspond to (for example `int`
        maps to `("integer", "number")`). Returns `(None, None)` if neither
        side can be parsed.
        """
        for pattern in _PYARROW_TYPE_HINT_RES:
            match = pattern.search(err_msg)
            if not match:
                continue
            observed = match.group(1)
            target = match.group(2)
            allowed = _TARGET_TO_JSON_SCHEMA.get(target)
            return observed, allowed
        return None, None

    def _find_first_type_mismatch(
        self,
        values: List[Any],
        schema_entry: Dict[str, Any],
        prefix: str,
        observed_filter: Optional[str] = None,
        declared_filter: Optional[Tuple[str, ...]] = None,
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Walk each value in `values` against `schema_entry` and return the first
        `(dotted_path, observed_python_type, declared_json_schema_type)` where
        the observed Python type does not match the declared JSON Schema type.
        When `observed_filter` and/or `declared_filter` are provided, only
        mismatches matching those types are returned. Returns `(None, None, None)`
        if no matching mismatch is found.
        """
        for value in values:
            path, observed, declared = self._walk_value(
                value,
                schema_entry,
                prefix,
                observed_filter=observed_filter,
                declared_filter=declared_filter,
            )
            if path is not None:
                return path, observed, declared
        return None, None, None

    def _walk_value(
        self,
        value: Any,
        schema_entry: Dict[str, Any],
        prefix: str,
        observed_filter: Optional[str] = None,
        declared_filter: Optional[Tuple[str, ...]] = None,
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        if value is None or value in EMPTY_VALUES:
            return None, None, None

        declared = self._get_json_schema_type(schema_entry.get("type"))

        if declared == "object" and isinstance(value, dict):
            props = schema_entry.get("properties") or {}
            for key, sub_value in value.items():
                sub_schema = props.get(key)
                if sub_schema is None:
                    continue
                path, observed, sub_declared = self._walk_value(
                    sub_value,
                    sub_schema,
                    f"{prefix}.{key}",
                    observed_filter=observed_filter,
                    declared_filter=declared_filter,
                )
                if path is not None:
                    return path, observed, sub_declared
            return None, None, None

        if declared == "array" and isinstance(value, list):
            items_schema = schema_entry.get("items") or {}
            for idx, item in enumerate(value):
                path, observed, sub_declared = self._walk_value(
                    item,
                    items_schema,
                    f"{prefix}[{idx}]",
                    observed_filter=observed_filter,
                    declared_filter=declared_filter,
                )
                if path is not None:
                    return path, observed, sub_declared
            return None, None, None

        observed_type = type(value).__name__
        mismatch: Optional[Tuple[str, str, str]] = None
        if declared in ("integer", "number"):
            # `bool` is a subclass of `int` in Python, but does not round-trip as a number here.
            if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
                mismatch = (prefix, observed_type, declared)
        elif declared == "boolean" and not isinstance(value, bool):
            mismatch = (prefix, observed_type, declared)
        elif declared == "string" and not isinstance(value, str):
            mismatch = (prefix, observed_type, declared)

        if mismatch is None:
            return None, None, None
        if observed_filter is not None and mismatch[1] != observed_filter:
            return None, None, None
        if declared_filter is not None and mismatch[2] not in declared_filter:
            return None, None, None
        return mismatch
        self._messages.clear()
