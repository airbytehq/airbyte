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

    def needs_quotes(self, input_name: str):
        """
        @param input_name to test if it needs to manipulated with quotes or not
        """
        if is_reserved_keyword(input_name, self.integration_type):
            return True
        if self.integration_type.value == DestinationType.BIGQUERY.value:
            return False
        doesnt_start_with_alphaunderscore = match("[^A-Za-z_]", input_name[0])
        contains_non_alphanumeric = match(".*[^A-Za-z0-9_].*", input_name)
        return doesnt_start_with_alphaunderscore or contains_non_alphanumeric

    def normalize_schema_name(self, schema_name: str, in_jinja: bool = False):
        """
        @param schema_name is the schema to normalize
        @param in_jinja is a boolean to specify if the returned normalized will be used inside a jinja macro or not
        """
        return self.__normalize_non_column_identifier_name(schema_name, in_jinja)

    def normalize_table_name(self, table_name: str, in_jinja: bool = False):
        """
        @param table_name is the table to normalize
        @param in_jinja is a boolean to specify if the returned normalized will be used inside a jinja macro or not
        """
        return self.__normalize_non_column_identifier_name(table_name, in_jinja)

    def normalize_column_name(self, column_name: str, in_jinja: bool = False):
        """
        @param column_name is the column to normalize
        @param in_jinja is a boolean to specify if the returned normalized will be used inside a jinja macro or not
        """
        return self.__normalize_identifier_name(column_name, in_jinja)

    # Private methods

    def __normalize_non_column_identifier_name(self, input_name: str, in_jinja: bool = False) -> str:
        # We force standard naming for non column names (see issue #1785)
        result = transform_standard_naming(input_name)
        result = self.__truncate_identifier_name(result)
        result = self.__normalize_identifier_case(result, is_quoted=False)
        return result

    def __normalize_identifier_name(self, column_name: str, in_jinja: bool = False):
        result = self.__truncate_identifier_name(column_name)
        if self.needs_quotes(result):
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

    def __truncate_identifier_name(self, input_name: str) -> str:
        if self.integration_type.value == DestinationType.BIGQUERY.value:
            if len(input_name) >= (1024 - TRUNCATE_RESERVED_SIZE):
                # bigquery has limit of 1024 characters
                input_name = input_name[0 : (1024 - TRUNCATE_RESERVED_SIZE)]
            input_name = transform_standard_naming(input_name)
            doesnt_start_with_alphaunderscore = match("[^A-Za-z_]", input_name[0])
            if doesnt_start_with_alphaunderscore:
                input_name = f"_{input_name}"
            return input_name
        elif self.integration_type.value == DestinationType.REDSHIFT.value:
            if len(input_name) >= (127 - TRUNCATE_RESERVED_SIZE):
                # redshift has limit of 127 characters
                input_name = input_name[0 : (127 - TRUNCATE_RESERVED_SIZE)]
        elif self.integration_type.value == DestinationType.POSTGRES.value:
            if len(input_name) >= (63 - TRUNCATE_RESERVED_SIZE):
                # postgres has limit of 63 characters
                # BUT postgres with DBT-v18.0.1 has limit of 29 characters
                # BUT postgres with DBT-v19.0.0 has limit of 51 characters
                # see https://github.com/fishtown-analytics/dbt/pull/2850
                input_name = input_name[0 : (63 - TRUNCATE_RESERVED_SIZE)]
        elif self.integration_type.value == DestinationType.SNOWFLAKE.value:
            if len(input_name) >= (255 - TRUNCATE_RESERVED_SIZE):
                # snowflake has limit of 255 characters
                input_name = input_name[0 : (255 - TRUNCATE_RESERVED_SIZE)]
        else:
            raise KeyError(f"Unknown integration type {self.integration_type}")
        return input_name

    def __normalize_identifier_case(self, input_name: str, is_quoted: bool = False):
        if self.integration_type.value == DestinationType.BIGQUERY.value:
            pass
        elif self.integration_type.value == DestinationType.REDSHIFT.value:
            # all tables (even quoted ones) are coerced to lowercase.
            input_name = input_name.lower()
        elif self.integration_type.value == DestinationType.POSTGRES.value:
            if not is_quoted and not self.needs_quotes(input_name):
                input_name = input_name.lower()
        elif self.integration_type.value == DestinationType.SNOWFLAKE.value:
            if not is_quoted and not self.needs_quotes(input_name):
                input_name = input_name.upper()
        else:
            raise KeyError(f"Unknown integration type {self.integration_type}")
        return input_name


# Static Functions


def transform_standard_naming(input_name: str) -> str:
    input_name = input_name.strip()
    input_name = strip_accents(input_name)
    input_name = sub(r"\s+", "_", input_name)
    input_name = sub(r"[^a-zA-Z0-9_]", "_", input_name)
    return input_name


def strip_accents(s):
    return "".join(c for c in ud.normalize("NFD", s) if ud.category(c) != "Mn")
