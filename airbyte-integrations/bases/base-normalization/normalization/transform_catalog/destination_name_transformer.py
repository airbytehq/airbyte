#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import unicodedata as ud
from re import match, sub

from normalization.destination_type import DestinationType
from normalization.transform_catalog.reserved_keywords import is_reserved_keyword
from normalization.transform_catalog.utils import jinja_call

DESTINATION_SIZE_LIMITS = {
    # https://cloud.google.com/bigquery/quotas#all_tables
    DestinationType.BIGQUERY.value: 1024,
    # https://docs.snowflake.com/en/sql-reference/identifiers-syntax.html
    DestinationType.SNOWFLAKE.value: 255,
    # https://docs.aws.amazon.com/redshift/latest/dg/r_names.html
    DestinationType.REDSHIFT.value: 127,
    # https://www.postgresql.org/docs/12/limits.html
    DestinationType.POSTGRES.value: 63,
    # https://dev.mysql.com/doc/refman/8.0/en/identifier-length.html
    DestinationType.MYSQL.value: 64,
    # https://oracle-base.com/articles/12c/long-identifiers-12cr2
    DestinationType.ORACLE.value: 128,
    # https://docs.microsoft.com/en-us/sql/odbc/microsoft/column-name-limitations?view=sql-server-ver15
    DestinationType.MSSQL.value: 64,
    # https://stackoverflow.com/questions/68358686/what-is-the-maximum-length-of-a-column-in-clickhouse-can-it-be-modified
    DestinationType.CLICKHOUSE.value: 63,
    # https://docs.pingcap.com/tidb/stable/tidb-limitations
    DestinationType.TIDB.value: 64,
}

# DBT also needs to generate suffix to table names, so we need to make sure it has enough characters to do so...
TRUNCATE_DBT_RESERVED_SIZE = 12
# we keep 4 characters for 1 underscore and 3 characters for suffix (_ab1, _ab2, etc)
# we keep 4 characters for 1 underscore and 3 characters hash (of the schema)
TRUNCATE_RESERVED_SIZE = 8


class DestinationNameTransformer:
    """
    Handles naming conventions in destinations for all kind of sql identifiers:
    - schema
    - table
    - column
    """

    def __init__(self, destination_type: DestinationType):
        """
        @param destination_type is the destination type of warehouse
        """
        self.destination_type: DestinationType = destination_type

    # Public methods

    def needs_quotes(self, input_name: str) -> bool:
        """
        @param input_name to test if it needs to manipulated with quotes or not
        """
        if is_reserved_keyword(input_name, self.destination_type):
            return True
        if self.destination_type.value == DestinationType.BIGQUERY.value:
            return False
        if self.destination_type.value == DestinationType.ORACLE.value and input_name.startswith("_"):
            return True
        doesnt_start_with_alphaunderscore = match("[^A-Za-z_]", input_name[0]) is not None
        contains_non_alphanumeric = match(".*[^A-Za-z0-9_].*", input_name) is not None
        return doesnt_start_with_alphaunderscore or contains_non_alphanumeric

    def normalize_schema_name(self, schema_name: str, in_jinja: bool = False, truncate: bool = True) -> str:
        """
        @param schema_name is the schema to normalize
        @param in_jinja is a boolean to specify if the returned normalized will be used inside a jinja macro or not
        @param truncate force ignoring truncate operation on resulting normalized name. For example, if we don't
        control how the name would be normalized
        """
        if self.destination_type == DestinationType.ORACLE and schema_name.startswith("_"):
            schema_name = schema_name[1:]
        return self.__normalize_non_column_identifier_name(input_name=schema_name, in_jinja=in_jinja, truncate=truncate)

    def normalize_table_name(
        self, table_name: str, in_jinja: bool = False, truncate: bool = True, conflict: bool = False, conflict_level: int = 0
    ) -> str:
        """
        @param table_name is the table to normalize
        @param in_jinja is a boolean to specify if the returned normalized will be used inside a jinja macro or not
        @param truncate force ignoring truncate operation on resulting normalized name. For example, if we don't
        control how the name would be normalized
        @param conflict if there is a conflict between stream name and fields
        @param conflict_level is the json_path level conflict happened
        """
        if self.destination_type == DestinationType.ORACLE and table_name.startswith("_"):
            table_name = table_name[1:]
        return self.__normalize_non_column_identifier_name(
            input_name=table_name, in_jinja=in_jinja, truncate=truncate, conflict=conflict, conflict_level=conflict_level
        )

    def normalize_column_name(
        self, column_name: str, in_jinja: bool = False, truncate: bool = True, conflict: bool = False, conflict_level: int = 0
    ) -> str:
        """
        @param column_name is the column to normalize
        @param in_jinja is a boolean to specify if the returned normalized will be used inside a jinja macro or not
        @param truncate force ignoring truncate operation on resulting normalized name. For example, if we don't
        control how the name would be normalized
        @param conflict if there is a conflict between stream name and fields
        @param conflict_level is the json_path level conflict happened
        """
        return self.__normalize_identifier_name(
            column_name=column_name, in_jinja=in_jinja, truncate=truncate, conflict=conflict, conflict_level=conflict_level
        )

    def truncate_identifier_name(self, input_name: str, custom_limit: int = -1, conflict: bool = False, conflict_level: int = 0) -> str:
        """
        @param input_name is the identifier name to middle truncate
        @param custom_limit uses a custom length as the max instead of the destination max length
        @param conflict if there is a conflict between stream name and fields
        @param conflict_level is the json_path level conflict happened
        """
        limit = custom_limit - 1 if custom_limit > 0 else self.get_name_max_length()

        if limit < len(input_name):
            middle = round(limit / 2)
            # truncate in the middle to preserve prefix/suffix instead
            prefix = input_name[: limit - middle - 1]
            suffix = input_name[1 - middle :]
            # Add extra characters '__', signaling a truncate in identifier
            print(f"Truncating {input_name} (#{len(input_name)}) to {prefix}_{suffix} (#{2 + len(prefix) + len(suffix)})")
            mid = "__"
            if conflict:
                mid = f"_{conflict_level}"
            input_name = f"{prefix}{mid}{suffix}"

        return input_name

    def get_name_max_length(self):
        if self.destination_type.value in DESTINATION_SIZE_LIMITS:
            destination_limit = DESTINATION_SIZE_LIMITS[self.destination_type.value]
            return destination_limit - TRUNCATE_DBT_RESERVED_SIZE - TRUNCATE_RESERVED_SIZE
        else:
            raise KeyError(f"Unknown destination type {self.destination_type}")

    # Private methods

    def __normalize_non_column_identifier_name(
        self, input_name: str, in_jinja: bool = False, truncate: bool = True, conflict: bool = False, conflict_level: int = 0
    ) -> str:
        # We force standard naming for non column names (see issue #1785)
        result = transform_standard_naming(input_name)
        result = self.__normalize_naming_conventions(result, is_column=False)
        if truncate:
            result = self.truncate_identifier_name(input_name=result, conflict=conflict, conflict_level=conflict_level)
        result = self.__normalize_identifier_case(result, is_quoted=False)
        if result[0].isdigit():
            if self.destination_type == DestinationType.MSSQL:
                result = "_" + result
            elif self.destination_type == DestinationType.ORACLE:
                result = "ab_" + result
        return result

    def __normalize_identifier_name(
        self, column_name: str, in_jinja: bool = False, truncate: bool = True, conflict: bool = False, conflict_level: int = 0
    ) -> str:
        result = self.__normalize_naming_conventions(column_name, is_column=True)
        if truncate:
            result = self.truncate_identifier_name(input_name=result, conflict=conflict, conflict_level=conflict_level)
        if self.needs_quotes(result):
            if self.destination_type.value == DestinationType.CLICKHOUSE.value:
                result = result.replace('"', "_")
                result = result.replace("`", "_")
                result = result.replace("'", "_")
            elif self.destination_type.value != DestinationType.MYSQL.value and self.destination_type.value != DestinationType.TIDB.value:
                result = result.replace('"', '""')
            else:
                result = result.replace("`", "_")
            result = result.replace("'", "\\'")
            result = self.__normalize_identifier_case(result, is_quoted=True)
            result = self.apply_quote(result)
            if not in_jinja:
                result = jinja_call(result)
            return result
        else:
            result = self.__normalize_identifier_case(result, is_quoted=False)
        if in_jinja:
            # to refer to columns while already in jinja context, always quote
            return f"'{result}'"
        return result

    def apply_quote(self, input: str, literal=True) -> str:
        if literal:
            input = f"'{input}'"
        if self.destination_type == DestinationType.ORACLE:
            # Oracle dbt lib doesn't implemented adapter quote yet.
            return f"quote({input})"
        elif self.destination_type == DestinationType.CLICKHOUSE:
            return f"quote({input})"
        return f"adapter.quote({input})"

    def __normalize_naming_conventions(self, input_name: str, is_column: bool = False) -> str:
        result = input_name
        if self.destination_type.value == DestinationType.ORACLE.value:
            return transform_standard_naming(result)
        elif self.destination_type.value == DestinationType.BIGQUERY.value:
            # Can start with number: datasetId, table
            # Can not start with number: column
            result = transform_standard_naming(result)
            doesnt_start_with_alphaunderscore = match("[^A-Za-z_]", result[0]) is not None
            if is_column and doesnt_start_with_alphaunderscore:
                result = f"_{result}"
        return result

    def __normalize_identifier_case(self, input_name: str, is_quoted: bool = False) -> str:
        result = input_name
        if self.destination_type.value == DestinationType.BIGQUERY.value:
            pass
        elif self.destination_type.value == DestinationType.REDSHIFT.value:
            # all tables (even quoted ones) are coerced to lowercase.
            result = input_name.lower()
        elif self.destination_type.value == DestinationType.POSTGRES.value:
            if not is_quoted and not self.needs_quotes(input_name):
                result = input_name.lower()
        elif self.destination_type.value == DestinationType.SNOWFLAKE.value:
            if not is_quoted and not self.needs_quotes(input_name):
                result = input_name.upper()
        elif self.destination_type.value == DestinationType.MYSQL.value:
            if not is_quoted and not self.needs_quotes(input_name):
                result = input_name.lower()
        elif self.destination_type.value == DestinationType.MSSQL.value:
            if not is_quoted and not self.needs_quotes(input_name):
                result = input_name.lower()
        elif self.destination_type.value == DestinationType.ORACLE.value:
            if not is_quoted and not self.needs_quotes(input_name):
                result = input_name.lower()
            else:
                result = input_name.upper()
        elif self.destination_type.value == DestinationType.CLICKHOUSE.value:
            pass
        elif self.destination_type.value == DestinationType.TIDB.value:
            if not is_quoted and not self.needs_quotes(input_name):
                result = input_name.lower()
        else:
            raise KeyError(f"Unknown destination type {self.destination_type}")
        return result

    def normalize_column_identifier_case_for_lookup(self, input_name: str, is_quoted: bool = False) -> str:
        """
        This function adds an additional normalization regarding the column name casing to determine if multiple columns
        are in collisions. On certain destinations/settings, case sensitivity matters, in others it does not.
        We separate this from standard identifier normalization "__normalize_identifier_case",
        so the generated SQL queries are keeping the original casing from the catalog.
        But we still need to determine if casing matters or not, thus by using this function.
        """
        result = input_name
        if self.destination_type.value == DestinationType.BIGQUERY.value:
            # Columns are considered identical regardless of casing
            result = input_name.lower()
        elif self.destination_type.value == DestinationType.REDSHIFT.value:
            # Columns are considered identical regardless of casing (even quoted ones)
            result = input_name.lower()
        elif self.destination_type.value == DestinationType.POSTGRES.value:
            if not is_quoted and not self.needs_quotes(input_name):
                result = input_name.lower()
        elif self.destination_type.value == DestinationType.SNOWFLAKE.value:
            if not is_quoted and not self.needs_quotes(input_name):
                result = input_name.upper()
        elif self.destination_type.value == DestinationType.MYSQL.value:
            # Columns are considered identical regardless of casing (even quoted ones)
            result = input_name.lower()
        elif self.destination_type.value == DestinationType.MSSQL.value:
            # Columns are considered identical regardless of casing (even quoted ones)
            result = input_name.lower()
        elif self.destination_type.value == DestinationType.ORACLE.value:
            if not is_quoted and not self.needs_quotes(input_name):
                result = input_name.lower()
            else:
                result = input_name.upper()
        elif self.destination_type.value == DestinationType.CLICKHOUSE.value:
            pass
        elif self.destination_type.value == DestinationType.TIDB.value:
            result = input_name.lower()
        else:
            raise KeyError(f"Unknown destination type {self.destination_type}")
        return result


# Static Functions


def transform_standard_naming(input_name: str) -> str:
    result = input_name.strip()
    result = strip_accents(result)
    result = sub(r"\s+", "_", result)
    result = sub(r"[^a-zA-Z0-9_]", "_", result)
    return result


def transform_json_naming(input_name: str) -> str:
    result = sub(r"['\"`]", "_", input_name)
    return result


def strip_accents(input_name: str) -> str:
    return "".join(c for c in ud.normalize("NFD", input_name) if ud.category(c) != "Mn")
