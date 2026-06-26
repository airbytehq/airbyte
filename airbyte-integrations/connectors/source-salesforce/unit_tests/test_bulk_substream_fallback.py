# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest.mock import MagicMock, patch

import pytest
from config_builder import ConfigBuilder
from conftest import generate_stream, mock_stream_api
from source_salesforce.rate_limiting import BulkNotSupportedException
from source_salesforce.streams import BulkSalesforceSubStream, RestSalesforceSubStream

from airbyte_cdk.models import SyncMode


_STREAM_NAME = "ContentDocumentLink"


def _create_substream():
    config = ConfigBuilder().build()
    sf_api = mock_stream_api(config)
    stream = generate_stream(_STREAM_NAME, config, sf_api)
    return stream


def _patch_instantiate(stream, side_effect=None):
    """Patch `_instantiate_declarative_stream` to set up a mock `_bulk_job_stream`.

    If `side_effect` is provided, the mock stream slicer's `stream_slices` will
    use it (e.g. to raise `BulkNotSupportedException`).
    """
    mock_bulk_job = MagicMock()
    if side_effect:
        mock_bulk_job.retriever.stream_slicer.stream_slices.side_effect = side_effect
    else:
        mock_bulk_job.retriever.stream_slicer.stream_slices.return_value = iter([{"partition": "slice1"}])

    original_instantiate = stream._instantiate_declarative_stream

    def fake_instantiate(*args, **kwargs):
        stream._bulk_job_stream = mock_bulk_job

    return patch.object(stream, "_instantiate_declarative_stream", side_effect=fake_instantiate)


def test_given_bulk_not_supported_exception_when_stream_slices_then_falls_back_to_rest():
    stream = _create_substream()
    assert isinstance(stream, BulkSalesforceSubStream)

    mock_rest_stream = MagicMock()
    mock_rest_stream.name = _STREAM_NAME
    mock_rest_stream.stream_slices.return_value = iter([{"parents": [{"Id": "abc"}]}])

    with (
        _patch_instantiate(stream, side_effect=BulkNotSupportedException()),
        patch.object(stream, "get_standard_instance", return_value=mock_rest_stream) as mock_get_standard,
        patch("source_salesforce.streams.SalesforceAvailabilityStrategy") as mock_availability,
    ):

        mock_availability.return_value.check_availability.return_value = (True, None)

        slices = list(stream.stream_slices(sync_mode=SyncMode.full_refresh))

        assert stream._switch_from_bulk_to_rest is True
        mock_get_standard.assert_called_once()
        mock_rest_stream.stream_slices.assert_called_once()
        assert slices == [{"parents": [{"Id": "abc"}]}]


def test_given_bulk_not_supported_and_rest_unavailable_when_stream_slices_then_yields_nothing():
    stream = _create_substream()

    mock_rest_stream = MagicMock()
    mock_rest_stream.name = _STREAM_NAME

    with (
        _patch_instantiate(stream, side_effect=BulkNotSupportedException()),
        patch.object(stream, "get_standard_instance", return_value=mock_rest_stream),
        patch("source_salesforce.streams.SalesforceAvailabilityStrategy") as mock_availability,
    ):

        mock_availability.return_value.check_availability.return_value = (False, "stream is not queryable")

        slices = list(stream.stream_slices(sync_mode=SyncMode.full_refresh))

        assert stream._switch_from_bulk_to_rest is True
        assert slices == []


def test_given_no_exception_when_stream_slices_then_does_not_fall_back():
    stream = _create_substream()

    with _patch_instantiate(stream):
        slices = list(stream.stream_slices(sync_mode=SyncMode.full_refresh))

        assert stream._switch_from_bulk_to_rest is False
        assert stream._rest_stream is None
        assert slices == [{"partition": "slice1"}]


def test_get_standard_instance_returns_rest_sub_stream():
    stream = _create_substream()
    rest_instance = stream.get_standard_instance()
    assert isinstance(rest_instance, RestSalesforceSubStream)
