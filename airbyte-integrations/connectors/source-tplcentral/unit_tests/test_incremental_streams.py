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

import pytest
from airbyte_cdk.models import SyncMode
from source_tplcentral.streams import IncrementalTplcentralStream


@pytest.fixture
def config():
    return {
        "config": {
            "authenticator": None,
            "url_base": "https://secure-wms.com/",
            "client_id": "xxx",
            "client_secret": "yyy",
            "user_login_id": 123,
            "tpl_key": "{00000000-0000-0000-0000-000000000000}",
            "customer_id": 4,
            "facility_id": 5,
            "start_date": "2021-10-01"
        }
    }


@pytest.fixture
def patch_incremental_base_class(mocker):
    mocker.patch.object(IncrementalTplcentralStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalTplcentralStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalTplcentralStream, "cursor_field", "test_cursor_field")
    mocker.patch.object(IncrementalTplcentralStream, "collection_field", "CollectionField")
    mocker.patch.object(IncrementalTplcentralStream, "__abstractmethods__", set())


@pytest.fixture
def stream(patch_incremental_base_class, config):
    return IncrementalTplcentralStream(**config)


def test_cursor_field(stream):
    expected_cursor_field = "test_cursor_field"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(stream):
    inputs = {
        "current_stream_state": {
            "test_cursor_field": "2021-01-01T01:02:34+01:56",
        },
        "latest_record": {},
    }
    expected_state = {"test_cursor_field": "2021-01-01T01:02:34+01:56"}
    assert stream.get_updated_state(**inputs) == expected_state

    inputs = {
        "current_stream_state": {},
        "latest_record": {
            "test_cursor_field": "2021-01-01T01:02:34+01:56",
        },
    }
    expected_state = {"test_cursor_field": "2021-01-01T01:02:34+01:56"}
    assert stream.get_updated_state(**inputs) == expected_state

    inputs = {
        "current_stream_state": {
            "test_cursor_field": "2021-01-01T01:02:34+01:56",
        },
        "latest_record": {
            "test_cursor_field": "2021-01-01T01:02:34+01:57",
        },
    }
    expected_state = {"test_cursor_field": "2021-01-01T01:02:34"}
    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices(stream, config):
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {}}
    expected_stream_slice = [{"test_cursor_field": config["config"]["start_date"]}]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(stream):
    assert stream.supports_incremental


def test_source_defined_cursor(stream):
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(stream):
    expected_checkpoint_interval = 100
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
