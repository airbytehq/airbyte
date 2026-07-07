#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import source_salesforce.streams as streams_module
from conftest import generate_stream

from source_salesforce.streams import BulkDatetimeStreamSlicer


def test_preserve_na_values_defaults_to_false(stream_config, stream_api):
    stream = generate_stream("Account", stream_config, stream_api)
    assert stream._preserve_na_values is False


def test_preserve_na_values_flows_from_config_to_stream(stream_config, stream_api):
    config = {**stream_config, "preserve_na_values": True}
    stream = generate_stream("Account", config, stream_api)
    assert stream._preserve_na_values is True


def test_preserve_na_values_passed_to_response_extractor(stream_config, stream_api, mocker):
    config = {**stream_config, "preserve_na_values": True}
    stream = generate_stream("Account", config, stream_api)

    spy = mocker.patch.object(streams_module, "ResponseToFileExtractor")
    stream._instantiate_declarative_stream(BulkDatetimeStreamSlicer(None), has_bulk_parent=False)

    spy.assert_called_once_with(parameters={}, preserve_na_values=True)


def test_response_extractor_defaults_to_not_preserving(stream_config, stream_api, mocker):
    stream = generate_stream("Account", stream_config, stream_api)

    spy = mocker.patch.object(streams_module, "ResponseToFileExtractor")
    stream._instantiate_declarative_stream(BulkDatetimeStreamSlicer(None), has_bulk_parent=False)

    spy.assert_called_once_with(parameters={}, preserve_na_values=False)