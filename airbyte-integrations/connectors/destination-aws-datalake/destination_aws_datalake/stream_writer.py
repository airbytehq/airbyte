#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
import re
from datetime import date, datetime
from decimal import Decimal, getcontext
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import pandas as pd
import pyarrow as pa

from airbyte_cdk.models import ConfiguredAirbyteStream, DestinationSyncMode, FailureType
from airbyte_cdk.utils import AirbyteTracedException

from .aws import AwsHandler
from .config_reader import ConnectorConfig, PartitionOptions
from .constants import EMPTY_VALUES, GLUE_TYPE_MAPPING_DECIMAL, GLUE_TYPE_MAPPING_DOUBLE, PANDAS_TYPE_MAPPING


_PYARROW_COLUMN_RE = re.compile(r"Conversion failed for column ([^\s]+) with type")


def _split_struct_fields(inner: str) -> List[Tuple[str, str]]:
    """
    Split the inner body of a Glue `struct<...>` into `(field_name, field_type)`
    pairs, respecting nested `<...>` so that `struct<a:struct<b:int>,c:string>`
    parses as `[("a", "struct<b:int>"), ("c", "string")]`. Each field is
    expected to be of the form `<name>:<type>`.
    """
    fields: List[Tuple[str, str]] = []
    depth = 0
    start = 0
    for i, ch in enumerate(inner):
        if ch == "<":
            depth += 1
        elif ch == ">":
            depth -= 1
        elif ch == "," and depth == 0:
            chunk = inner[start:i].strip()
            if ":" in chunk:
                name, typ = chunk.split(":", 1)
                fields.append((name.strip(), typ.strip()))
            start = i + 1
    chunk = inner[start:].strip()
    if chunk and ":" in chunk:
        name, typ = chunk.split(":", 1)
        fields.append((name.strip(), typ.strip()))
    return fields


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
_TARGET_TO_PYTHON_TYPES: Dict[str, Tuple[str, ...]] = {
    "int": ("int", "Decimal"),
    "int64": ("int", "Decimal"),
    "int32": ("int", "Decimal"),
    "double": ("float", "Decimal"),
    "float": ("float", "Decimal"),
    "float64": ("float", "Decimal"),
    "float32": ("float", "Decimal"),
    "string": ("str",),
    "str": ("str",),
    "bool": ("bool",),
    "boolean": ("bool",),
}
_TARGET_TO_PA_TYPE: Dict[str, pa.DataType] = {
    "int": pa.int64(),
    "int64": pa.int64(),
    "int32": pa.int32(),
    "double": pa.float64(),
    "float": pa.float64(),
    "float64": pa.float64(),
    "float32": pa.float32(),
    "string": pa.string(),
    "str": pa.string(),
    "bool": pa.bool_(),
    "boolean": pa.bool_(),
}
# Glue scalar types that map to each pyarrow target type. Used to decide
# whether a sub-field declared in the awswrangler dtype dict is plausibly
# the one pyarrow expected as the target.
_TARGET_TO_GLUE_TYPES: Dict[str, Tuple[str, ...]] = {
    "int": ("bigint", "int", "smallint", "tinyint", "long"),
    "int64": ("bigint", "int", "smallint", "tinyint", "long"),
    "int32": ("bigint", "int", "smallint", "tinyint", "long"),
    "double": ("double", "float", "decimal"),
    "float": ("double", "float", "decimal"),
    "float64": ("double", "float", "decimal"),
    "float32": ("double", "float", "decimal"),
    "string": ("string", "varchar", "char"),
    "str": ("string", "varchar", "char"),
    "bool": ("boolean",),
    "boolean": ("boolean",),
}
# Cap how many records the mixed-type discoverer walks to avoid pathological cost on large batches.
_MIXED_TYPE_RECORD_CAP = 5000
_MAX_MIXED_TYPE_CANDIDATES = 8
# Cap how many records the brute-force pyarrow probe replays per candidate sub-path.
_PROBE_RECORD_CAP = 1000
# Cap how many `(key, type-or-error)` entries are surfaced from the per-subkey
# probe in the internal log message. The probe still walks every distinct
# top-level key — this only bounds the diagnostic sample we attach to the
# `AirbyteTracedException`.
_MAX_SUBKEY_INFERENCE_SAMPLE = 12


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
        self._last_flush_dtype: Dict[str, str] = {}

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
        # Stash the dtype dict so `_build_type_mismatch_exception` can surface
        # it (and parse out per-sub-field expected types) when pyarrow fails.
        self._last_flush_dtype = dtype

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
        actually violated the declared schema.

        The destination's `_json_schema_cast_value` already coerces declared
        `number`/`integer` fields via `pd.to_numeric(..., errors="coerce")`, so by
        the time pyarrow fails the original offending value has often been
        replaced with `NaN`. That means walking the post-cast dataframe against
        the JSON schema cannot recover the field that actually crashed pyarrow:
        the crash is typically on a sub-field that was never in the declared
        schema (so the cast skipped it), but for which different records have
        different Python types (for example one record has a numeric value and
        another has a string), causing pyarrow's struct-inference to fail.

        This helper therefore looks for sub-paths under the offending column
        whose values have more than one distinct Python type across the batch,
        and prefers ones whose observed type set matches the
        `(observed, target)` pair parsed from pyarrow's error message. It falls
        back to the JSON-schema walker only when no mixed-type sub-path is
        found.
        """
        err_msg = str(ex)
        column_match = _PYARROW_COLUMN_RE.search(err_msg)
        column = column_match.group(1) if column_match else None
        observed_filter, declared_filter = self._parse_pyarrow_type_hint(err_msg)
        target_python_types = self._parse_pyarrow_target_python_types(err_msg)

        bad_path: Optional[str] = None
        observed_type: Optional[str] = None
        declared_type: Optional[str] = None
        mixed_candidates: List[Tuple[str, Set[str]]] = []
        observed_type_map: Dict[str, Set[str]] = {}
        probe_path: Optional[str] = None
        probe_error: Optional[str] = None
        subkey_probe_path: Optional[str] = None
        subkey_probe_error: Optional[str] = None
        subkey_inference_sample: List[Tuple[str, str]] = []
        target_pa_type = self._parse_pyarrow_target_pa_type(err_msg)
        target_glue_types = self._parse_pyarrow_target_glue_types(err_msg)
        column_glue_type = self._last_flush_dtype.get(column) if column else None
        # `glue_oracle_available` indicates the heuristic probe can use the
        # awswrangler `dtype` dict — the schema awswrangler hands to pyarrow
        # — to restrict candidates to sub-paths declared as the target Glue
        # type. In practice the Glue dtype dict for a struct column does not
        # always cover every sub-key the dataframe contains (HubSpot, for
        # example, ships dynamic property keys), and pyarrow's *own*
        # per-subkey type inference is what actually produced the target
        # type in the original error. The per-subkey replay below
        # (`_probe_struct_subkey_culprit`) is therefore the most
        # authoritative oracle: it asks pyarrow exactly the question
        # pyarrow asks itself, and the first subkey whose replay reproduces
        # the same error signature is the field pyarrow choked on.
        glue_oracle_available = bool(
            column_glue_type
            and target_glue_types
            and self._collect_glue_paths_matching_target(column_glue_type, column or "", target_glue_types)
        )
        if column and column in df.columns:
            values = df[column].tolist()
            observed_type_map = self._collect_observed_type_map(values, prefix=column)
            if target_pa_type is not None:
                subkey_culprit, subkey_err, subkey_inference_sample = self._probe_struct_subkey_culprit(
                    values=values,
                    target_pa_type=target_pa_type,
                )
                if subkey_culprit is not None:
                    subkey_probe_path = f"{column}.{subkey_culprit}"
                    subkey_probe_error = subkey_err
            if target_pa_type is not None and observed_filter is not None:
                probe_path, probe_error = self._probe_pyarrow_culprit(
                    values=values,
                    column_prefix=column,
                    target_pa_type=target_pa_type,
                    observed_type_map=observed_type_map,
                    observed_filter=observed_filter,
                    target_glue_types=target_glue_types,
                )
            mixed_candidates = self._rank_type_mismatch_candidates(
                observed_type_map,
                observed_filter=observed_filter,
                target_python_types=target_python_types,
                schema_entry=self._schema.get(column),
                column_prefix=column,
            )
            # The per-subkey replay is the most authoritative source:
            # pyarrow itself raised when handed exactly that subkey's values,
            # so the match is by construction the field that crashed the
            # full conversion. It outranks the Glue-oracle probe and all
            # heuristic walkers below.
            if subkey_probe_path is not None:
                bad_path = subkey_probe_path
                observed_type = observed_filter or "?"
                schema_entry_for_column = self._schema.get(column)
                declared_for_bad_path = (
                    self._lookup_declared_schema_type(schema_entry_for_column, bad_path, column)
                    if schema_entry_for_column is not None
                    else None
                )
                if declared_for_bad_path is not None:
                    declared_type = declared_for_bad_path
                elif declared_filter:
                    declared_type = "/".join(declared_filter)
                else:
                    declared_type = "?"
            elif glue_oracle_available and probe_path is not None:
                bad_path = probe_path
                observed_type = observed_filter
                schema_entry_for_column = self._schema.get(column)
                declared_for_bad_path = (
                    self._lookup_declared_schema_type(schema_entry_for_column, bad_path, column)
                    if schema_entry_for_column is not None
                    else None
                )
                if declared_for_bad_path is not None:
                    declared_type = declared_for_bad_path
                elif declared_filter:
                    declared_type = "/".join(declared_filter)
                else:
                    declared_type = "?"
            elif mixed_candidates:
                bad_path, observed_types_set = mixed_candidates[0]
                observed_type = "/".join(sorted(observed_types_set))
                declared_for_bad_path = None
                schema_entry_for_column = self._schema.get(column)
                if schema_entry_for_column is not None:
                    declared_for_bad_path = self._lookup_declared_schema_type(schema_entry_for_column, bad_path, column)
                if declared_for_bad_path is not None:
                    declared_type = declared_for_bad_path
                elif declared_filter:
                    declared_type = "/".join(declared_filter)
                else:
                    declared_type = observed_filter or "?"
            elif column in self._schema:
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

            # Fallback: heuristic JSON-Schema-oracle probe (no Glue oracle).
            # Only kicks in when no walker pinpointed a path.
            if bad_path is None and probe_path is not None:
                bad_path = probe_path
                observed_type = observed_filter
                schema_entry_for_column = self._schema.get(column)
                declared_for_bad_path = (
                    self._lookup_declared_schema_type(schema_entry_for_column, bad_path, column)
                    if schema_entry_for_column is not None
                    else None
                )
                if declared_for_bad_path is not None:
                    declared_type = declared_for_bad_path
                elif declared_filter:
                    declared_type = "/".join(declared_filter)
                else:
                    declared_type = "?"

        if bad_path is not None:
            message = (
                f'Stream "{self._table}" field "{bad_path}" has values of type '
                f"{observed_type} that do not match declared type {declared_type}."
            )
        elif column is not None:
            message = f'Stream "{self._table}" column "{column}" has values that do not match the declared schema type.'
        else:
            message = f'Stream "{self._table}" produced values that cannot be converted to the declared schema types.'

        candidates_repr = "; ".join(
            f"{path}={{{','.join(sorted(types))}}}" for path, types in mixed_candidates[:_MAX_MIXED_TYPE_CANDIDATES]
        )
        # When no candidate was found, dump a bounded slice of the observed
        # type map so we can diagnose why the walker missed the culprit.
        fallback_type_map_repr = ""
        if not mixed_candidates and observed_type_map:
            sorted_entries = sorted(observed_type_map.items())[:_MAX_MIXED_TYPE_CANDIDATES]
            fallback_type_map_repr = "; ".join(f"{path}={{{','.join(sorted(types))}}}" for path, types in sorted_entries)
        probe_repr = ""
        if probe_path is not None:
            probe_repr = f"probe_path={probe_path} probe_error={probe_error!r} "
        subkey_probe_repr = ""
        if subkey_probe_path is not None:
            subkey_probe_repr = f"subkey_probe_path={subkey_probe_path} subkey_probe_error={subkey_probe_error!r} "
        subkey_inference_repr = ""
        if subkey_inference_sample:
            sliced = subkey_inference_sample[:_MAX_SUBKEY_INFERENCE_SAMPLE]
            subkey_inference_repr = "subkey_inference_sample=[" + "; ".join(f"{k}={t}" for k, t in sliced) + "] "
        column_glue_type = self._last_flush_dtype.get(column) if column else None
        glue_repr = f"column_glue_type={column_glue_type} " if column_glue_type else ""
        internal_message = (
            f"[stream={self._table} column={column} field={bad_path} "
            f"observed_type={observed_type} declared_type={declared_type} "
            f"observed_filter={observed_filter} target_python_types={target_python_types} "
            f"target_glue_types={target_glue_types} "
            f"{glue_repr}"
            f"{subkey_probe_repr}"
            f"{probe_repr}"
            f"mixed_type_candidates=[{candidates_repr}] "
            f"{subkey_inference_repr}"
            f"observed_type_map_sample=[{fallback_type_map_repr}]] "
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

    @staticmethod
    def _parse_pyarrow_target_python_types(err_msg: str) -> Optional[Tuple[str, ...]]:
        """
        Parse the target conversion type out of a pyarrow error message and map
        it to the set of Python type names that satisfy it. Returns `None` if
        the target type cannot be parsed or has no known Python type mapping.
        """
        for pattern in _PYARROW_TYPE_HINT_RES:
            match = pattern.search(err_msg)
            if not match:
                continue
            target = match.group(2)
            return _TARGET_TO_PYTHON_TYPES.get(target)
        return None

    @staticmethod
    def _parse_pyarrow_target_glue_types(err_msg: str) -> Tuple[str, ...]:
        """
        Parse the target conversion type out of a pyarrow error message and map
        it to the tuple of Glue scalar type names that are plausibly the
        oracle pyarrow validated against. Returns `()` if the target type
        cannot be parsed.
        """
        for pattern in _PYARROW_TYPE_HINT_RES:
            match = pattern.search(err_msg)
            if not match:
                continue
            target = match.group(2)
            return _TARGET_TO_GLUE_TYPES.get(target, ())
        return ()

    @staticmethod
    def _parse_pyarrow_target_pa_type(err_msg: str) -> Optional[pa.DataType]:
        """
        Parse the target conversion type out of a pyarrow error message and map
        it to a concrete `pa.DataType` that can be used to replay
        `pa.array(values, type=...)`. Returns `None` if the target type
        cannot be parsed or is not in the supported map.
        """
        for pattern in _PYARROW_TYPE_HINT_RES:
            match = pattern.search(err_msg)
            if not match:
                continue
            target = match.group(2)
            return _TARGET_TO_PA_TYPE.get(target)
        return None

    @staticmethod
    def _extract_values_at_path(values: List[Any], path: str, column_prefix: str) -> List[Any]:
        """
        Walk `values` (the list of top-level values for `column_prefix`) and
        return the list of leaf values at dotted `path`. The path uses `.<key>`
        for dict keys and `[]` for array elements (matching the format produced
        by `_collect_observed_types`). Records that do not have the path are
        represented by `None` in the result, mirroring how `pa.array` would
        treat absent struct fields.
        """
        if not path.startswith(column_prefix):
            return []
        remainder = path[len(column_prefix) :]
        token_pattern = re.compile(r"\.([^.\[]+)|\[\]")
        tokens: List[Tuple[str, Optional[str]]] = []
        pos = 0
        for match in token_pattern.finditer(remainder):
            if match.start() != pos:
                return []
            pos = match.end()
            if match.group(0) == "[]":
                tokens.append(("array", None))
            else:
                tokens.append(("key", match.group(1)))
        if pos != len(remainder):
            return []

        extracted: List[Any] = []

        def walk(node: Any, idx: int) -> None:
            if idx == len(tokens):
                extracted.append(node)
                return
            kind, key = tokens[idx]
            if kind == "key":
                if isinstance(node, dict) and key in node:
                    walk(node[key], idx + 1)
                else:
                    extracted.append(None)
            else:
                if isinstance(node, list):
                    for item in node:
                        walk(item, idx + 1)

        for value in values[:_PROBE_RECORD_CAP]:
            walk(value, 0)
        return extracted

    @classmethod
    def _probe_struct_subkey_culprit(
        cls,
        values: List[Any],
        target_pa_type: pa.DataType,
    ) -> Tuple[Optional[str], Optional[str], List[Tuple[str, str]]]:
        """
        Identify the offending top-level subkey of a struct column by replaying
        `pa.array([record.get(key) for record in records], from_pandas=True)`
        for every distinct top-level key seen across `values`, with no target
        type hint.

        Returns `(culprit_key, culprit_error, sample)` where `culprit_key` is
        the first subkey whose probe raised an Arrow error whose target
        pyarrow type matches `target_pa_type`, `culprit_error` is the raw
        Arrow error string, and `sample` is the sorted list of
        `(key, inferred_type_or_error_excerpt)` pairs for diagnostic logging.

        Unlike `_probe_pyarrow_culprit`, this probe takes no schema
        oracle: pyarrow is asked exactly the question it would ask itself
        when inferring a struct from dicts, so a match is by construction
        the sub-field pyarrow choked on. This is the right strategy when
        the Glue dtype dict and the JSON Schema both fail to surface a
        candidate of the target type — for example when the dataframe
        column has more sub-keys than the declared Glue struct, and
        pyarrow's per-subkey type inference (rather than the Glue dtype)
        is what produced the target type in the original error.

        Matching is done by extracting the target pyarrow type from each
        replay error (which uses one of two pyarrow error formats — see
        `_PYARROW_TYPE_HINT_RES`) and comparing it against the original
        `target_pa_type`. This handles both `cannot be converted to int`
        (struct-from-pandas) and `tried to convert to int64`
        (sequence-from-pandas) error variants.
        """
        keys: Set[str] = set()
        for value in values:
            if isinstance(value, dict):
                keys.update(value.keys())

        sample: List[Tuple[str, str]] = []
        culprit: Optional[str] = None
        culprit_err: Optional[str] = None
        for key in sorted(keys):
            sub_values = [v.get(key) if isinstance(v, dict) else None for v in values]
            if not any(sv is not None for sv in sub_values):
                continue
            try:
                arr = pa.array(sub_values, from_pandas=True)
            except (pa.ArrowInvalid, pa.ArrowTypeError) as ex:
                err_str = str(ex)
                sample.append((key, f"ERR:{err_str[:80]}"))
                replay_target = cls._parse_pyarrow_target_pa_type(err_str)
                if culprit is None and replay_target is not None and replay_target == target_pa_type:
                    culprit = key
                    culprit_err = err_str
            else:
                sample.append((key, str(arr.type)))
        return culprit, culprit_err, sample

    def _probe_pyarrow_culprit(
        self,
        values: List[Any],
        column_prefix: str,
        target_pa_type: pa.DataType,
        observed_type_map: Dict[str, Set[str]],
        observed_filter: str,
        target_glue_types: Tuple[str, ...] = (),
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Identify the exact sub-path that triggers pyarrow's conversion failure
        by replaying `pa.array(values_at_path, type=target_pa_type)` against
        each candidate sub-path in `observed_type_map`. Returns
        `(path, probe_error_message)` for the first sub-path that raises an
        `ArrowInvalid` / `ArrowTypeError` for the target type, or `(None, None)`
        if no sub-path reproduces it.

        Candidate selection (most authoritative oracle first):
        1. Sub-paths whose Glue type in the awswrangler `dtype` dict matches
           the target (for example `bigint` when target is `int`). This
           directly mirrors the schema pyarrow validated against — if the
           probe reproduces the failure here, we have a 1:1 match with what
           pyarrow rejected.
        2. Sub-paths whose declared JSON Schema type matches the target type
           (for example declared `number` when target is `int`).
        3. Sub-paths not declared in either oracle.

        Sub-paths whose declared type is *incompatible* with the target are
        intentionally excluded: probing them produces false positives because
        `pa.array(strs, type=int64)` raises for any uniform-str path
        regardless of whether pyarrow itself would have failed there.
        """
        target_python_set = set(_TARGET_TO_PYTHON_TYPES.get(str(target_pa_type), ()))
        schema_entry = self._schema.get(column_prefix)
        column_glue_type = self._last_flush_dtype.get(column_prefix)
        glue_paths = (
            self._collect_glue_paths_matching_target(column_glue_type, column_prefix, target_glue_types)
            if column_glue_type and target_glue_types
            else set()
        )

        def declared_for(path: str) -> Optional[str]:
            if schema_entry is None:
                return None
            return self._lookup_declared_schema_type(schema_entry, path, column_prefix)

        def json_schema_matches_target(declared: Optional[str]) -> bool:
            if declared is None:
                return False
            if declared in ("integer", "number") and target_python_set & {"int", "float", "Decimal"}:
                return True
            if declared == "string" and "str" in target_python_set:
                return True
            if declared == "boolean" and "bool" in target_python_set:
                return True
            return False

        # When the Glue dtype is known and lists at least one sub-field of the
        # target type, that's the authoritative oracle pyarrow validated
        # against — restrict the probe to those sub-paths only. Otherwise
        # fall back to the JSON Schema as a heuristic oracle.
        candidates: List[str] = []
        if glue_paths:
            for path, observed_types in observed_type_map.items():
                if observed_filter in observed_types and path in glue_paths:
                    candidates.append(path)
        else:
            tier_2: List[str] = []
            tier_3: List[str] = []
            for path, observed_types in observed_type_map.items():
                if observed_filter not in observed_types:
                    continue
                declared = declared_for(path)
                if json_schema_matches_target(declared):
                    tier_2.append(path)
                elif declared is None:
                    tier_3.append(path)
            candidates = tier_2 + tier_3

        for path in candidates:
            extracted = self._extract_values_at_path(values, path, column_prefix)
            if not extracted:
                continue
            if not any(type(v).__name__ == observed_filter for v in extracted):
                continue
            try:
                pa.array(extracted, type=target_pa_type, from_pandas=True)
            except (pa.ArrowInvalid, pa.ArrowTypeError) as probe_ex:
                return path, str(probe_ex)
        return None, None

    @staticmethod
    def _collect_glue_paths_matching_target(
        glue_type: str,
        prefix: str,
        target_glue_types: Tuple[str, ...],
    ) -> Set[str]:
        """
        Walk a Glue type string (for example `struct<a:bigint,b:string,
        nested:struct<n:bigint>>`) starting from `prefix` and return the set of
        dotted sub-paths whose leaf Glue scalar type is in `target_glue_types`.
        Array elements contribute the sub-path with a `[]` segment, matching
        the format produced by `_collect_observed_types`.
        """
        matching: Set[str] = set()

        def normalize(raw: str) -> str:
            # Strip parameterized parts like `decimal(28,25)` -> `decimal`.
            return raw.split("(", 1)[0].strip().lower()

        def walk(typ: str, path_prefix: str) -> None:
            stripped = typ.strip()
            lower = stripped.lower()
            if lower.startswith("struct<") and stripped.endswith(">"):
                inner = stripped[len("struct<") : -1]
                for field_name, field_type in _split_struct_fields(inner):
                    sub_path = f"{path_prefix}.{field_name}"
                    walk(field_type, sub_path)
            elif lower.startswith("array<") and stripped.endswith(">"):
                inner = stripped[len("array<") : -1]
                walk(inner, f"{path_prefix}[]")
            else:
                if normalize(stripped) in target_glue_types:
                    matching.add(path_prefix)

        walk(glue_type, prefix)
        return matching

    def _collect_observed_type_map(self, values: List[Any], prefix: str) -> Dict[str, Set[str]]:
        """
        Walk up to `_MIXED_TYPE_RECORD_CAP` of `values` and return a mapping
        of dotted sub-path -> set of observed Python type names. Dict-valued
        leaves and `None` are skipped; list elements are aggregated under
        `<prefix>[]`.
        """
        type_map: Dict[str, Set[str]] = {}
        for value in values[:_MIXED_TYPE_RECORD_CAP]:
            self._collect_observed_types(value, prefix, type_map)
        return type_map

    def _lookup_declared_schema_type(self, schema_entry: Dict[str, Any], path: str, column_prefix: str) -> Optional[str]:
        """
        Resolve a dotted `path` (for example `properties.createdate` or
        `questions[].id`) against `schema_entry` (the top-level column's JSON
        Schema definition) and return the declared JSON Schema type of the
        leaf, or `None` if the path is not declared. `column_prefix` is the
        top-level column name, stripped before walking.
        """
        if not path.startswith(column_prefix):
            return None
        remainder = path[len(column_prefix) :]
        current = schema_entry
        if not remainder:
            return self._get_json_schema_type(current.get("type"))

        # Tokenize: split `.` boundaries but preserve `[]` as array markers.
        token_pattern = re.compile(r"\.([^.\[]+)|\[\]")
        pos = 0
        for match in token_pattern.finditer(remainder):
            if match.start() != pos:
                return None
            pos = match.end()
            if match.group(0) == "[]":
                typ = self._get_json_schema_type(current.get("type"))
                if typ != "array":
                    return None
                items = current.get("items") or {}
                if isinstance(items, list):
                    items = items[0] if items else {}
                current = items
            else:
                key = match.group(1)
                typ = self._get_json_schema_type(current.get("type"))
                if typ != "object":
                    return None
                props = current.get("properties") or {}
                if key not in props:
                    return None
                current = props[key]
        if pos != len(remainder):
            return None
        return self._get_json_schema_type(current.get("type"))

    def _rank_type_mismatch_candidates(
        self,
        type_map: Dict[str, Set[str]],
        observed_filter: Optional[str] = None,
        target_python_types: Optional[Tuple[str, ...]] = None,
        schema_entry: Optional[Dict[str, Any]] = None,
        column_prefix: Optional[str] = None,
    ) -> List[Tuple[str, Set[str]]]:
        """
        Rank entries in `type_map` by how likely they are to be the culprit
        of pyarrow's conversion failure. Two kinds of paths are considered:

        1. *Mixed-type paths* — more than one distinct non-null Python type
           observed across the batch. These trip pyarrow's struct inference
           on `object`-typed columns.
        2. *Uniform-offender paths* — every observed value at the path is of
           the offending Python type (for example `str`) and that type does
           not match any of the target Python types implied by pyarrow's
           error (for example pyarrow wanted `int`/`Decimal`). These are
           considered only when both `observed_filter` and
           `target_python_types` are known.

        When `observed_filter` is provided, paths whose type set does not
        contain that observed type are filtered out entirely.
        """
        target_set = set(target_python_types or ())
        # Map of observed Python type name -> compatible JSON Schema types.
        # Used to decide whether a uniform-type path is a genuine culprit or
        # just a declared field of the right type.
        observed_to_json_schema: Dict[str, Tuple[str, ...]] = {
            "str": ("string",),
            "int": ("integer", "number"),
            "float": ("number",),
            "Decimal": ("number", "integer"),
            "bool": ("boolean",),
        }
        candidates: List[Tuple[str, Set[str]]] = []
        for path, types in type_map.items():
            non_null = {t for t in types if t != "NoneType"}
            if not non_null:
                continue
            if observed_filter is not None and observed_filter not in non_null:
                continue
            declared_for_path: Optional[str] = None
            if schema_entry is not None and column_prefix is not None:
                declared_for_path = self._lookup_declared_schema_type(schema_entry, path, column_prefix)
            if len(non_null) == 1:
                # Only keep a uniform path when it's the offending type and
                # does not satisfy the target type. Otherwise it's a
                # single-type field of the expected type, not a culprit.
                if observed_filter is None or not target_set:
                    continue
                if non_null & target_set:
                    continue
                # When the path IS declared in the schema AND the observed
                # type is already compatible with the declared type, this is
                # not the culprit: pyarrow would not complain about a str
                # value in a field declared as string.
                if declared_for_path is not None:
                    compatible = observed_to_json_schema.get(observed_filter, ())
                    if declared_for_path in compatible:
                        continue
            candidates.append((path, non_null))

        def rank(item: Tuple[str, Set[str]]) -> Tuple[int, int, int, str]:
            path, types = item
            has_observed = observed_filter is not None and observed_filter in types
            has_target = bool(target_set & types)
            is_mixed = len(types) > 1
            # Lower tuple sorts first. Preference order:
            # 0: mixed, contains BOTH observed + target (ambiguous, very
            #    likely pyarrow's struct-inference culprit).
            # 1: mixed, contains observed.
            # 2: uniform offender (only observed type, target absent) — the
            #    "every record has a str in a field we need to be int" case.
            # 3: anything else (for example mixed without observed when the
            #    filter is not set).
            if is_mixed and has_observed and has_target:
                primary = 0
            elif is_mixed and has_observed:
                primary = 1
            elif not is_mixed and has_observed and not has_target:
                primary = 2
            else:
                primary = 3
            # Secondary: prefer paths whose declared JSON schema type matches
            # the target (for example declared `number` when pyarrow wanted
            # `int`). 0 = matches target, 1 = path not declared in schema,
            # 2 = declared but not target type.
            declared_rank = 1
            if schema_entry is not None and column_prefix is not None:
                declared = self._lookup_declared_schema_type(schema_entry, path, column_prefix)
                if declared is None:
                    declared_rank = 1
                elif declared in ("integer", "number") and target_set & {"int", "float", "Decimal"}:
                    declared_rank = 0
                elif declared == "string" and "str" in target_set:
                    declared_rank = 0
                elif declared == "boolean" and "bool" in target_set:
                    declared_rank = 0
                else:
                    declared_rank = 2
            return primary, declared_rank, -len(types), path

        candidates.sort(key=rank)
        return candidates

    @staticmethod
    def _collect_observed_types(value: Any, prefix: str, type_map: Dict[str, Set[str]]) -> None:
        """
        Recursively record the Python type of every leaf value reached from
        `value` into `type_map`, keyed by dotted path. Dict keys extend the
        path with `.<key>`; list elements extend it with `[]` so that all
        elements of a list are aggregated under the same path. Dict-valued
        leaves and `None` values are not recorded.
        """
        if isinstance(value, dict):
            if not value:
                return
            for key, sub_value in value.items():
                StreamWriter._collect_observed_types(sub_value, f"{prefix}.{key}", type_map)
            return
        if isinstance(value, list):
            if not value:
                return
            for item in value:
                StreamWriter._collect_observed_types(item, f"{prefix}[]", type_map)
            return
        if value is None:
            return
        type_map.setdefault(prefix, set()).add(type(value).__name__)

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
