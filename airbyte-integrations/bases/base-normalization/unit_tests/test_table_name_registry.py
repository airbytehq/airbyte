#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import os
from typing import List

import pytest
from normalization.destination_type import DestinationType
from normalization.transform_catalog.catalog_processor import CatalogProcessor
from normalization.transform_catalog.destination_name_transformer import DestinationNameTransformer
from normalization.transform_catalog.table_name_registry import TableNameRegistry, get_nested_hashed_table_name


@pytest.fixture(scope="function", autouse=True)
def before_tests(request):
    # This makes the test run whether it is executed from the tests folder (with pytest/gradle)
    # or from the base-normalization folder (through pycharm)
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
        "long_name_truncate_collisions_catalog",  # collisions are generated on postgres because of character limits
        "un-nesting_collisions_catalog",  # collisions between top-level streams and nested ones
        "nested_catalog",  # sample catalog from facebook
    ],
)
@pytest.mark.parametrize("destination_type", DestinationType.testable_destinations())
def test_resolve_names(destination_type: DestinationType, catalog_file: str):
    """
    For a given catalog.json and destination, multiple cases can occur where naming becomes tricky.
    (especially since some destination like postgres have a very low limit to identifiers length of 64 characters)

    In case of nested objects/arrays in a stream, names can drag on to very long names.
    Tests are built here using resources files as follow:
    - `<name of source or test types>_catalog.json`:
        input catalog.json, typically as what source would provide.
        For example Hubspot, Stripe and Facebook catalog.json contains some level of nesting.
        (here, nested_catalog.json is an extracted smaller sample of stream/properties from the facebook catalog)
    - `<name of source or test types>_expected_names.json`:
        list of expected table names

    For the expected json files, it is possible to specialize the file to a certain destination.
    So if for example, the resources folder contains these two expected files:
        - edge_cases_catalog_expected_names.json
        - edge_cases_catalog_expected_postgres_names.json
    Then the test will be using the first edge_cases_catalog_expected_names.json except for
    Postgres destination where the expected table names will come from edge_cases_catalog_expected_postgres_names.json

    The content of the expected_*.json files are the serialization of the stream_processor.tables_registry.registry
    """
    integration_type = destination_type.value
    tables_registry = TableNameRegistry(destination_type)

    catalog = read_json(f"resources/{catalog_file}.json")

    # process top level
    stream_processors = CatalogProcessor.build_stream_processor(
        catalog=catalog,
        json_column_name="'json_column_name_test'",
        default_schema="schema_test",
        name_transformer=DestinationNameTransformer(destination_type),
        destination_type=destination_type,
        tables_registry=tables_registry,
    )
    for stream_processor in stream_processors:
        # Check properties
        if not stream_processor.properties:
            raise EOFError("Invalid Catalog: Unexpected empty properties in catalog")
        stream_processor.collect_table_names()
    for conflict in tables_registry.resolve_names():
        print(
            f"WARN: Resolving conflict: {conflict.schema}.{conflict.table_name_conflict} "
            f"from '{'.'.join(conflict.json_path)}' into {conflict.table_name_resolved}"
        )
    apply_function = identity
    if DestinationType.SNOWFLAKE.value == destination_type.value:
        apply_function = str.upper
    elif DestinationType.REDSHIFT.value == destination_type.value:
        apply_function = str.lower
    if os.path.exists(f"resources/{catalog_file}_expected_{integration_type.lower()}_names.json"):
        expected_names = read_json(f"resources/{catalog_file}_expected_{integration_type.lower()}_names.json", apply_function)
    else:
        expected_names = read_json(f"resources/{catalog_file}_expected_names.json", apply_function)

    assert tables_registry.to_dict(apply_function) == expected_names


def identity(x):
    return x


def read_json(input_path: str, apply_function=(lambda x: x)):
    with open(input_path, "r") as file:
        contents = file.read()
    if apply_function:
        contents = apply_function(contents)
    return json.loads(contents)


# This test is not intended to be exhaustive over the destinations,
# so it's not mandatory to add new destination expected field here.
# The intent here is to unit test simple_name vs nested_hashed_name
# functions in the table_name_registry. There are other tests that
# automatically test naming against all destinations whenever it is
# added to the enum.
@pytest.mark.parametrize(
    "json_path, expected_postgres, expected_bigquery",
    [
        (
            ["parent", "child"],
            "parent_child",
            "parent_child",
        ),
        (
            ["The parent stream has a nested column with a", "short_substream_name"],
            "the_parent_stream_ha___short_substream_name",
            "The_parent_stream_has_a_nested_column_with_a_short_substream_name",
        ),
        (
            ["The parent stream has a nested column with a", "substream with a rather long name"],
            "the_parent_stream_ha__th_a_rather_long_name",
            "The_parent_stream_has_a_nested_column_with_a_substream_with_a_rather_long_name",
        ),
    ],
)
def test_get_simple_table_name(json_path: List[str], expected_postgres: str, expected_bigquery: str):
    """
    Checks how to generate a simple and easy to understand name from a json path
    """
    postgres_registry = TableNameRegistry(DestinationType.POSTGRES)
    actual_postgres_name = postgres_registry.get_simple_table_name(json_path)
    assert actual_postgres_name == expected_postgres
    assert len(actual_postgres_name) <= 43  # explicitly check for our max postgres length in case tests are changed in the future

    bigquery_registry = TableNameRegistry(DestinationType.BIGQUERY)
    actual_bigquery_name = bigquery_registry.get_simple_table_name(json_path)
    assert actual_bigquery_name == expected_bigquery


@pytest.mark.parametrize(
    "json_path, expected_postgres, expected_bigquery",
    [
        (
            ["parent", "child"],
            "parent_30c_child",
            "parent_30c_child",
        ),
        (
            ["The parent stream has a nested column with a", "short_substream_name"],
            "the_parent_stream__cd9_short_substream_name",
            "The_parent_stream_has_a_nested_column_with_a_cd9_short_substream_name",
        ),
        (
            ["The parent stream has a nested column with a", "substream with a rather long name"],
            "the_parent_0a5_substream_wi__her_long_name",
            "The_parent_stream_has_a_nested_column_with_a_0a5_substream_with_a_rather_long_name",
        ),
    ],
)
def test_get_nested_hashed_table_name(json_path: List[str], expected_postgres: str, expected_bigquery: str):
    """
    Checks how to generate a unique name with strategies of combining all fields into a single table name for the user to (somehow)
    identify and recognize what data is available in there.
    A set of complicated rules are done in order to choose what parts to truncate or what to leave and handle
    name collisions.
    """
    child = json_path[-1]
    postgres_name_transformer = DestinationNameTransformer(DestinationType.POSTGRES)
    actual_postgres_name = get_nested_hashed_table_name(postgres_name_transformer, "schema", json_path, child)
    assert actual_postgres_name == expected_postgres
    assert len(actual_postgres_name) <= 43  # explicitly check for our max postgres length in case tests are changed in the future

    bigquery_name_transformer = DestinationNameTransformer(DestinationType.BIGQUERY)
    actual_bigquery_name = get_nested_hashed_table_name(bigquery_name_transformer, "schema", json_path, child)
    assert actual_bigquery_name == expected_bigquery
