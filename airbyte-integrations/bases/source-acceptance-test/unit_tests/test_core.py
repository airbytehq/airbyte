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

from unittest.mock import MagicMock

import pytest
from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, Type
from source_acceptance_test.config import BasicReadTestConfig
from source_acceptance_test.tests.test_core import TestBasicRead as _TestBasicRead
from source_acceptance_test.tests.test_core import TestDiscovery as _TestDiscovery


@pytest.mark.parametrize(
    "schema, cursors, should_fail",
    [
        ({}, ["created"], True),
        ({"properties": {"created": {"type": "string"}}}, ["created"], False),
        ({"properties": {"created_at": {"type": "string"}}}, ["created"], True),
        ({"properties": {"created": {"type": "string"}}}, ["updated", "created"], True),
        ({"properties": {"updated": {"type": "object", "properties": {"created": {"type": "string"}}}}}, ["updated", "created"], False),
        ({"properties": {"created": {"type": "object", "properties": {"updated": {"type": "string"}}}}}, ["updated", "created"], True),
    ],
)
def test_discovery(schema, cursors, should_fail):
    t = _TestDiscovery()
    discovered_catalog = {
        "test_stream": AirbyteStream.parse_obj({"name": "test_stream", "json_schema": schema, "default_cursor_field": cursors})
    }
    if should_fail:
        with pytest.raises(AssertionError):
            t.test_defined_cursors_exist_in_schema(None, discovered_catalog)
    else:
        t.test_defined_cursors_exist_in_schema(None, discovered_catalog)


@pytest.mark.parametrize(
    "schema, record, should_fail",
    [
        ({"type": "object", "properties": {"created": {"type": "string"}}}, {"aa": 23}, True),
        ({"type": "object", "properties": {"created": {"type": "string"}}}, {"created": "23"}, False),
        ({"type": "object", "properties": {"created": {"type": "string"}}}, {"root": {"created": "23"}}, True),
    ],
)
def test_read(schema, record, should_fail):
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream.parse_obj({"name": "test_stream", "json_schema": schema}),
                sync_mode="full_refresh",
                destination_sync_mode="overwrite",
            )
        ]
    )
    input_config = BasicReadTestConfig()
    docker_runner_mock = MagicMock()
    docker_runner_mock.call_read.return_value = [
        AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream", data=record, emitted_at=111))
    ]
    t = _TestBasicRead()
    if should_fail:
        with pytest.raises(AssertionError, match="stream should have some fields mentioned by json schema"):
            t.test_read(None, catalog, input_config, [], docker_runner_mock, MagicMock())
    else:
        t.test_read(None, catalog, input_config, [], docker_runner_mock, MagicMock())
