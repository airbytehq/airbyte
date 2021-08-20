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


import os
from typing import List

import pytest
from airbyte_protocol.models.airbyte_protocol import DestinationSyncMode, SyncMode
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
        ([["id"]], "string", False, ["id"], "{{ adapter.quote('id') }}"),
        ([["id"]], "number", False, ["id"], "cast({{ adapter.quote('id') }} as {{ dbt_utils.type_string() }})"),
        ([["first_name"], ["last_name"]], "string", False, ["first_name", "last_name"], "first_name, last_name"),
        ([["float_id"]], "number", False, ["float_id"], "cast(float_id as {{ dbt_utils.type_string() }})"),
        ([["_airbyte_emitted_at"]], "string", False, [], "cast(_airbyte_emitted_at as {{ dbt_utils.type_string() }})"),
        (None, "string", True, [], ""),
        ([["parent", "nested_field"]], "string", True, [], ""),
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
        schema="schema_name",
        source_sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append_dedup,
        cursor_field=[],
        primary_key=primary_key,
        json_column_name="json_column_name",
        properties={key: {"type": column_type} for key in expected_primary_keys},
        tables_registry=TableNameRegistry(DestinationType.POSTGRES),
        from_table="",
    )
    try:
        assert stream_processor.get_primary_key(column_names=stream_processor.extract_column_names()) == expected_final_primary_key_string
    except ValueError as e:
        if not expecting_exception:
            raise e
