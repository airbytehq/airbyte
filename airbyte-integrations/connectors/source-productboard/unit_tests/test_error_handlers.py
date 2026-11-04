# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import requests

from airbyte_cdk.sources.declarative.requesters.error_handlers import DefaultErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies import ConstantBackoffStrategy
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


STREAM_NAMES = (
    "products",
    "features",
    "components",
    "feature-statuses",
    "notes",
    "tags",
    "links",
    "feedback-form-configurations",
    "companies",
    "company-custom-fields",
    "users",
    "custom-fields",
    "custom-fields-values",
    "release-groups",
    "releases",
    "feature-release-assignments",
    "objectives",
)
CONSTANT_BACKOFF_STREAMS = tuple(name for name in STREAM_NAMES if name not in {"notes", "companies"})


def _error_handler(stream):
    return stream._stream_partition_generator._partition_factory._retriever.requester.error_handler


def test_all_streams_covered(streams):
    assert set(streams) == set(STREAM_NAMES)


@pytest.mark.parametrize("stream_name", STREAM_NAMES)
def test_default_error_handler(streams, stream_name):
    handler = _error_handler(streams[stream_name])
    assert isinstance(handler, DefaultErrorHandler)


@pytest.mark.parametrize("stream_name", STREAM_NAMES)
def test_rate_limited_response(streams, stream_name):
    response = requests.Response()
    response.status_code = 429
    assert _error_handler(streams[stream_name]).interpret_response(response).response_action == ResponseAction.RATE_LIMITED


@pytest.mark.parametrize("stream_name", CONSTANT_BACKOFF_STREAMS)
def test_constant_backoff_preserved(streams, stream_name):
    strategies = _error_handler(streams[stream_name]).backoff_strategies
    assert len(strategies) == 1
    assert isinstance(strategies[0], ConstantBackoffStrategy)
    assert strategies[0].backoff_time(None, attempt_count=1) == 1
