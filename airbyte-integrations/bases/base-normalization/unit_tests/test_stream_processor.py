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

import os
import re

import pytest
from normalization.destination_type import DestinationType
from normalization.transform_catalog.catalog_processor import CatalogProcessor, add_table_to_registry, read_json
from normalization.transform_catalog.stream_processor import get_table_name
from normalization.transform_catalog.destination_name_transformer import DestinationNameTransformer


@pytest.fixture
def setup_test_path():
    # This makes the test pass no matter if it is executed from Tests folder (with pytest) or from base-normalization folder (through pycharm)
    if os.path.exists(os.path.join(os.curdir, "unit_tests")):
        os.chdir("unit_tests")


@pytest.mark.parametrize(
    "catalog_file",
    [
        "hubspot_catalog",
        "facebook_catalog",
        "stripe_catalog",
    ],
)
@pytest.mark.parametrize(
    "integration_type",
    [
        "Postgres",
        "BigQuery",
        "Snowflake",
        "Redshift",
    ],
)
def test_stream_processor_tables_naming(integration_type: str, catalog_file: str, setup_test_path):
    destination_type = DestinationType.from_string(integration_type)
    tables_registry = set()

    substreams = []
    catalog = read_json(f"resources/{catalog_file}.json")

    # process top level
    for stream_processor in CatalogProcessor.build_stream_processor(
        catalog=catalog,
        json_column_name="'json_column_name_test'",
        target_schema="schema_test",
        name_transformer=DestinationNameTransformer(destination_type),
        destination_type=destination_type,
        tables_registry=tables_registry,
    ):
        nested_processors = stream_processor.process()
        for table in stream_processor.local_registry:
            found_sql_output = False
            for sql_output in stream_processor.sql_outputs:
                if re.match(r".*/" + table + ".sql", sql_output) is not None:
                    found_sql_output = True
                    break
            assert found_sql_output
        add_table_to_registry(tables_registry, stream_processor)
        if nested_processors and len(nested_processors) > 0:
            substreams += nested_processors

    if os.path.exists(f"resources/{catalog_file}_expected_top_level_{integration_type.lower()}.json"):
        expected_top_level = set(read_json(f"resources/{catalog_file}_expected_top_level_{integration_type.lower()}.json")["tables"])
    else:
        expected_top_level = set(read_json(f"resources/{catalog_file}_expected_top_level.json")["tables"])
        if DestinationType.SNOWFLAKE.value == destination_type.value:
            expected_top_level = {table.upper() for table in expected_top_level}
        elif DestinationType.REDSHIFT.value == destination_type.value:
            expected_top_level = {table.lower() for table in expected_top_level}

    # process substreams
    while substreams:
        children = substreams
        substreams = []
        for substream in children:
            substream.tables_registry = tables_registry
            nested_processors = substream.process()
            add_table_to_registry(tables_registry, substream)
            if nested_processors:
                substreams += nested_processors

    if os.path.exists(f"resources/{catalog_file}_expected_nested_{integration_type.lower()}.json"):
        expected_nested = set(read_json(f"resources/{catalog_file}_expected_nested_{integration_type.lower()}.json")["tables"])
    else:
        expected_nested = set(read_json(f"resources/{catalog_file}_expected_nested.json")["tables"])
        if DestinationType.SNOWFLAKE.value == destination_type.value:
            expected_nested = {table.upper() for table in expected_nested}
        elif DestinationType.REDSHIFT.value == destination_type.value:
            expected_nested = {table.lower() for table in expected_nested}

    table_list = list(tables_registry - expected_top_level)
    table_list.sort()
    for table in table_list:
        print("table =", table)

    assert (tables_registry - expected_top_level) == expected_nested


@pytest.mark.parametrize(
    "root_table, base_table_name, suffix, expected",
    [
        ("abcdefghijklmnopqrstuvwxyz", "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz", "", "abcdefghij_HSH_abcdefghijklm__nopqrstuvwxyz"),
        ("abcdefghijklmnopqrstuvwxyz", "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz", "_ab1", "abcdefghij_HSH_abcdefghijk__pqrstuvwxyz_ab1"),
        ("abcde", "fghijk", "_ab1", "abcde_HSH_fghijk_ab1"),
        ("abcde", "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz", "", "abcde_HSH_abcdefghijklmnop__lmnopqrstuvwxyz"),
    ],
)
def test_get_table_name(root_table: str, base_table_name: str, suffix: str, expected: str):
    name_transformer = DestinationNameTransformer(DestinationType.POSTGRES)
    name = get_table_name(name_transformer, root_table, base_table_name, suffix, "HSH")
    assert name == expected
