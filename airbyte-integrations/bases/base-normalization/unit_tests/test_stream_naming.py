#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


import json
import os

import pytest
from normalization.destination_type import DestinationType
from normalization.transform_catalog.catalog_processor import CatalogProcessor, add_table_to_registry
from normalization.transform_catalog.destination_name_transformer import DestinationNameTransformer


@pytest.fixture(scope="function", autouse=True)
def before_tests(request):
    # This makes the test run whether it is executed from the tests folder (with pytest/gradle) or from the base-normalization folder (through pycharm)
    unit_tests_dir = os.path.join(request.fspath.dirname, "unit_tests")
    if os.path.exists(unit_tests_dir):
        os.chdir(unit_tests_dir)
    else:
        os.chdir(request.fspath.dirname)
    yield
    os.chdir(request.config.invocation_dir)


@pytest.mark.parametrize(
    "catalog_file",
    [
        "edge_cases_catalog",
        "nested_catalog",
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
def test_stream_processor_tables_naming(integration_type: str, catalog_file: str):
    """
    For a given catalog.json and destination, multiple cases can occur where naming becomes tricky.
    (especially since some destination like postgres have a very low limit to identifiers length of 64 characters)

    In case of nested objects/arrays in a stream, names can drag on to very long names.
    Tests are built here using resources files as follow:
    - `<name of source or test types>_catalog.json`:
        input catalog.json, typically as what source would provide.
        For example Hubspot, Stripe and Facebook catalog.json contains some level of nesting.
        (here, nested_catalog.json is an extracted smaller sample of stream/properties from the facebook catalog)
    - `<name of source or test types>_expected_top_level.json`:
        list of expected table names for the top level stream names
    - `<name of source or test types>_expected_nested.json`:
        list of expected table names for nested objects, extracted to their own and separate table names

    For the expected json files, it is possible to specialize the file to a certain destination.
    So if for example, the resources folder contains these two expected files:
        - edge_cases_catalog_expected_top_level.json
        - edge_cases_catalog_expected_top_level_postgres.json
    Then the test will be using the first edge_cases_catalog_expected_top_level.json except for
    Postgres destination where the expected table names will come from edge_cases_catalog_expected_top_level_postgres.json

    The content of the expected_*.json files are the serialization of the stream_processor.tables_registry
    (mapping per schema to all tables in that schema, mapping to the final filename)
    """
    destination_type = DestinationType.from_string(integration_type)
    tables_registry = {}

    substreams = []
    catalog = read_json(f"resources/{catalog_file}.json")

    # process top level
    for stream_processor in CatalogProcessor.build_stream_processor(
        catalog=catalog,
        json_column_name="'json_column_name_test'",
        default_schema="schema_test",
        name_transformer=DestinationNameTransformer(destination_type),
        destination_type=destination_type,
        tables_registry=tables_registry,
    ):
        nested_processors = stream_processor.process()
        tables_registry = add_table_to_registry(tables_registry, stream_processor)
        if nested_processors and len(nested_processors) > 0:
            substreams += nested_processors

    apply_function = None
    if DestinationType.SNOWFLAKE.value == destination_type.value:
        apply_function = str.upper
    elif DestinationType.REDSHIFT.value == destination_type.value:
        apply_function = str.lower
    if os.path.exists(f"resources/{catalog_file}_expected_top_level_{integration_type.lower()}.json"):
        expected_top_level = read_json(f"resources/{catalog_file}_expected_top_level_{integration_type.lower()}.json", apply_function)
    else:
        expected_top_level = read_json(f"resources/{catalog_file}_expected_top_level.json", apply_function)

    assert tables_registry == expected_top_level

    # process substreams
    while substreams:
        children = substreams
        substreams = []
        for substream in children:
            substream.tables_registry = tables_registry
            nested_processors = substream.process()
            tables_registry = add_table_to_registry(tables_registry, substream)
            if nested_processors:
                substreams += nested_processors

    apply_function = None
    if DestinationType.SNOWFLAKE.value == destination_type.value:
        apply_function = str.upper
    elif DestinationType.REDSHIFT.value == destination_type.value:
        apply_function = str.lower
    if os.path.exists(f"resources/{catalog_file}_expected_nested_{integration_type.lower()}.json"):
        expected_nested = read_json(f"resources/{catalog_file}_expected_nested_{integration_type.lower()}.json", apply_function)
    else:
        expected_nested = read_json(f"resources/{catalog_file}_expected_nested.json", apply_function)

    # remove expected top level tables from tables_registry
    for schema in expected_top_level:
        for table in expected_top_level[schema]:
            del tables_registry[schema][table]
        if len(tables_registry[schema]) == 0:
            del tables_registry[schema]
    assert tables_registry == expected_nested


def read_json(input_path: str, apply_function=None):
    with open(input_path, "r") as file:
        contents = file.read()
    if apply_function:
        contents = apply_function(contents)
    return json.loads(contents)
