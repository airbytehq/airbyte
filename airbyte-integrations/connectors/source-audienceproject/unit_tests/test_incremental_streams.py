#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pytest import fixture
from source_audienceproject.streams import Campaigns, IncrementalAudienceprojectStream

authenticator = ""
config = {}
parent = Campaigns


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalAudienceprojectStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalAudienceprojectStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalAudienceprojectStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = IncrementalAudienceprojectStream(config, authenticator, parent)
    expected_cursor_field = []
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class):
    stream = IncrementalAudienceprojectStream(config, authenticator, parent)
    inputs = {"current_stream_state": None, "latest_record": None}
    expected_state = {}
    assert stream.get_updated_state(**inputs) == expected_state


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(IncrementalAudienceprojectStream, "cursor_field", "dummy_field")
    stream = IncrementalAudienceprojectStream(config, authenticator, parent)
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = IncrementalAudienceprojectStream(config, authenticator, parent)
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = IncrementalAudienceprojectStream(config, authenticator, parent)
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
