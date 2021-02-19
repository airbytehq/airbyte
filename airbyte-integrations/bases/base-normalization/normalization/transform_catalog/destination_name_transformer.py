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

import unicodedata as ud
from re import match, sub

from normalization.destination_type import DestinationType
from normalization.transform_catalog.reserved_keywords import is_reserved_keyword
from normalization.transform_catalog.utils import jinja_call

DESTINATION_SIZE_LIMITS = {
    DestinationType.BIGQUERY.value: 1024,
    DestinationType.SNOWFLAKE.value: 255,
    DestinationType.REDSHIFT.value: 127,
    DestinationType.POSTGRES.value: 63,
}

# in DBT Versions < 19.0:
TRUNCATE_DBT_RESERVED_SIZE = 29
# in DBT Versions >= 19.0:
# see https://github.com/fishtown-analytics/dbt/pull/2850
TRUNCATE_DBT_RESERVED_SIZE_v19 = 12

# We reserve this many characters from identifier names to be used for prefix/suffix for airbyte
# before reaching the database name length limit
TRUNCATE_RESERVED_SIZE: int = 5


class DestinationNameTransformer:
    """
    Handles naming conventions in destinations for all kind of sql identifiers:
    - schema
    - table
    - column
    """

    def __init__(self, integration_type: DestinationType):
        """
        @param integration_type is the destination type of warehouse
        """
        self.integration_type: DestinationType = integration_type

    # Public methods

    def needs_quotes(self, input_name: str) -> bool:
        """
        @param input_name to test if it needs to manipulated with quotes or not
        """
        if is_reserved_keyword(input_name, self.integration_type):
            return True
        if self.integration_type.value == DestinationType.BIGQUERY.value:
            return False
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
        return self.__normalize_non_column_identifier_name(input_name=schema_name, in_jinja=in_jinja, truncate=truncate)

    def normalize_table_name(self, table_name: str, in_jinja: bool = False, truncate: bool = True) -> str:
        """
        @param table_name is the table to normalize
        @param in_jinja is a boolean to specify if the returned normalized will be used inside a jinja macro or not
        @param truncate force ignoring truncate operation on resulting normalized name. For example, if we don't
        control how the name would be normalized
        """
        return self.__normalize_non_column_identifier_name(input_name=table_name, in_jinja=in_jinja, truncate=truncate)

    def normalize_column_name(self, column_name: str, in_jinja: bool = False, truncate: bool = True) -> str:
        """
        @param column_name is the column to normalize
        @param in_jinja is a boolean to specify if the returned normalized will be used inside a jinja macro or not
        @param truncate force ignoring truncate operation on resulting normalized name. For example, if we don't
        control how the name would be normalized
        """
        return self.__normalize_identifier_name(column_name=column_name, in_jinja=in_jinja, truncate=truncate)

    # Private methods

    def __normalize_non_column_identifier_name(self, input_name: str, in_jinja: bool = False, truncate: bool = True) -> str:
        # We force standard naming for non column names (see issue #1785)
        result = transform_standard_naming(input_name)
        result = self.__normalize_naming_conventions(result)
        if truncate:
            result = self.__truncate_identifier_name(result)
        result = self.__normalize_identifier_case(result, is_quoted=False)
        return result

    def __normalize_identifier_name(self, column_name: str, in_jinja: bool = False, truncate: bool = True) -> str:
        result = self.__normalize_naming_conventions(column_name)
        if truncate:
            result = self.__truncate_identifier_name(result)
        if self.needs_quotes(result):
            result = result.replace('"', '""')
            result = result.replace("'", "\\'")
            result = f"adapter.quote('{result}')"
            result = self.__normalize_identifier_case(result, is_quoted=True)
            if not in_jinja:
                result = jinja_call(result)
            return result
        else:
            result = self.__normalize_identifier_case(result, is_quoted=False)
        if in_jinja:
            # to refer to columns while already in jinja context, always quote
            return f"'{result}'"
        return result

    def __normalize_naming_conventions(self, input_name: str) -> str:
        result = input_name
        if self.integration_type.value == DestinationType.BIGQUERY.value:
            result = transform_standard_naming(result)
            doesnt_start_with_alphaunderscore = match("[^A-Za-z_]", result[0]) is not None
            if doesnt_start_with_alphaunderscore:
                result = f"_{result}"
        return result

    def __truncate_identifier_name(self, input_name: str) -> str:
        if self.integration_type.value in DESTINATION_SIZE_LIMITS:
            limit = DESTINATION_SIZE_LIMITS[self.integration_type.value]
            limit = limit - TRUNCATE_RESERVED_SIZE - TRUNCATE_DBT_RESERVED_SIZE
            # TODO smarter truncate (or hash) in the middle to preserve prefix/suffix instead?
            input_name = input_name[0:limit]
        else:
            raise KeyError(f"Unknown integration type {self.integration_type}")
        return input_name

    def __normalize_identifier_case(self, input_name: str, is_quoted: bool = False) -> str:
        result = input_name
        if self.integration_type.value == DestinationType.BIGQUERY.value:
            pass
        elif self.integration_type.value == DestinationType.REDSHIFT.value:
            # all tables (even quoted ones) are coerced to lowercase.
            result = input_name.lower()
        elif self.integration_type.value == DestinationType.POSTGRES.value:
            if not is_quoted and not self.needs_quotes(input_name):
                result = input_name.lower()
        elif self.integration_type.value == DestinationType.SNOWFLAKE.value:
            if not is_quoted and not self.needs_quotes(input_name):
                result = input_name.upper()
        else:
            raise KeyError(f"Unknown integration type {self.integration_type}")
        return result


# Static Functions


def transform_standard_naming(input_name: str) -> str:
    result = input_name.strip()
    result = strip_accents(result)
    result = sub(r"\s+", "_", result)
    result = sub(r"[^a-zA-Z0-9_]", "_", result)
    return result


def strip_accents(input_name: str) -> str:
    return "".join(c for c in ud.normalize("NFD", input_name) if ud.category(c) != "Mn")
