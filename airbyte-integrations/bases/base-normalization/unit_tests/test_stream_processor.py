#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import os
from typing import List

import pytest
from airbyte_cdk.models import DestinationSyncMode, SyncMode
from normalization.destination_type import DestinationType
from normalization.transform_catalog.stream_processor import StreamProcessor
from normalization.transform_catalog.table_name_registry import TableNameRegistry


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
    "cursor_field, expecting_exception, expected_cursor_field",
    [
        (None, False, "_airbyte_emitted_at"),
        (["updated_at"], False, "updated_at"),
        (["_airbyte_emitted_at"], False, "_airbyte_emitted_at"),
        (["parent", "nested_field"], True, "nested_field"),
    ],
)
def test_cursor_field(cursor_field: List[str], expecting_exception: bool, expected_cursor_field: str):
    stream_processor = StreamProcessor.create(
        stream_name="test_cursor_field",
        destination_type=DestinationType.POSTGRES,
        default_schema="default_schema",
        raw_schema="raw_schema",
        schema="schema_name",
        source_sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append_dedup,
        cursor_field=cursor_field,
        primary_key=[],
        json_column_name="json_column_name",
        properties=dict(),
        tables_registry=TableNameRegistry(DestinationType.POSTGRES),
        from_table="",
    )
    try:
        assert (
            stream_processor.get_cursor_field(column_names={expected_cursor_field: (expected_cursor_field, "random")})
            == expected_cursor_field
        )
    except ValueError as e:
        if not expecting_exception:
            raise e


@pytest.mark.parametrize(
    "primary_key, column_type, expecting_exception, expected_primary_keys, expected_final_primary_key_string",
    [
        ([["id"]], "WellKnownTypes.json#/definitions/String", False, ["id"], "{{ adapter.quote('id') }}"),
        ([["id"]], "WellKnownTypes.json#/definitions/Number", False, ["id"], "cast({{ adapter.quote('id') }} as {{ dbt_utils.type_string() }})"),
        ([["first_name"], ["last_name"]], "WellKnownTypes.json#/definitions/String", False, ["first_name", "last_name"], "first_name, last_name"),
        ([["float_id"]], "WellKnownTypes.json#/definitions/Number", False, ["float_id"], "cast(float_id as {{ dbt_utils.type_string() }})"),
        ([["_airbyte_emitted_at"]], "WellKnownTypes.json#/definitions/String", False, [], "cast(_airbyte_emitted_at as {{ dbt_utils.type_string() }})"),
        (None, "WellKnownTypes.json#/definitions/String", True, [], ""),
        ([["parent", "nested_field"]], "WellKnownTypes.json#/definitions/String", True, [], ""),
    ],
)
def test_primary_key(
    primary_key: List[List[str]],
    column_type: str,
    expecting_exception: bool,
    expected_primary_keys: List[str],
    expected_final_primary_key_string: str,
):
    stream_processor = StreamProcessor.create(
        stream_name="test_primary_key",
        destination_type=DestinationType.POSTGRES,
        raw_schema="raw_schema",
        default_schema="default_schema",
        schema="schema_name",
        source_sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append_dedup,
        cursor_field=[],
        primary_key=primary_key,
        json_column_name="json_column_name",
        properties={key: {"$ref": column_type} for key in expected_primary_keys},
        tables_registry=TableNameRegistry(DestinationType.POSTGRES),
        from_table="",
    )
    try:
        assert (
            ", ".join(stream_processor.get_primary_key_partition(column_names=stream_processor.extract_column_names()))
            == expected_final_primary_key_string
        )
    except ValueError as e:
        if not expecting_exception:
            raise e
