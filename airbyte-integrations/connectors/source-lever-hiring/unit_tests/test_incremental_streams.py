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
from source_lever_hiring.streams import IncrementalLeverHiringStream


@pytest.fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalLeverHiringStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalLeverHiringStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalLeverHiringStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class, test_incremental_config):
    stream = IncrementalLeverHiringStream(**test_incremental_config)
    # TODO: replace this with your expected cursor field
    expected_cursor_field = "updatedAt"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class, test_incremental_config, test_opportunity_record):
    stream = IncrementalLeverHiringStream(**test_incremental_config)
    inputs = {"current_stream_state": {"opportunities": {"updatedAt": 1600000000000}}, "latest_record": test_opportunity_record}
    expected_state = {"updatedAt": 1738542849132}
    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices(patch_incremental_base_class, test_incremental_config):
    stream = IncrementalLeverHiringStream(**test_incremental_config)
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": ["updatedAt"], "stream_state": {"updatedAt": 1600000000000}}
    expected_stream_slice = [None]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker, test_incremental_config):
    mocker.patch.object(IncrementalLeverHiringStream, "cursor_field", "dummy_field")
    stream = IncrementalLeverHiringStream(**test_incremental_config)
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class, test_incremental_config):
    stream = IncrementalLeverHiringStream(**test_incremental_config)
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class, test_incremental_config):
    stream = IncrementalLeverHiringStream(**test_incremental_config)
    expected_checkpoint_interval = 100
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
