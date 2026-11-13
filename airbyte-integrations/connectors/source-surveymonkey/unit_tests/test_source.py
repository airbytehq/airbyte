#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from requests import Response
from source_surveymonkey.source import SourceSurveymonkey

from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.wait_time_from_header_backoff_strategy import (
    WaitTimeFromHeaderBackoffStrategy,
)


source_config = {"start_date": "2021-01-01T00:00:00", "access_token": "something"}
new_source_config = {
    "start_date": "2021-01-01T00:00:00",
    "origin": "USA",
    "credentials": {"auth_method": "something", "access_token": "something", "client_secret": "client_secret", "client_id": "client_id"},
}


def test_source_streams():
    streams = SourceSurveymonkey().streams(config=new_source_config)
    assert len(streams) == 6


def test_source_check_connection_failed_missing_scopes(requests_mock):
    requests_mock.get("https://api.surveymonkey.com/v3/users/me", json={"scopes": {"granted": ["surveys_read", "users_read"]}})

    results = SourceSurveymonkey().check_connection(logger=None, config=new_source_config)
    assert results == (False, "missed required scopes: responses_read_detail")


def _collect_requesters(stream):
    requesters = [(stream.name, stream.retriever.requester)]
    slicer = stream.retriever.stream_slicer
    for partition_router in getattr(slicer, "stream_slicers", [slicer]):
        for parent_config in getattr(partition_router, "parent_stream_configs", []):
            requesters.extend(_collect_requesters(parent_config.stream))
    return requesters


def test_rate_limit_backoff():
    streams = SourceSurveymonkey().streams(config=new_source_config)
    collected_requesters = [
        (name, requester) for stream in streams if isinstance(stream, DeclarativeStream) for name, requester in _collect_requesters(stream)
    ]
    required_stream_names = {
        "survey_ids",
        "survey_pages",
        "survey_questions",
        "survey_responses",
        "survey_collectors",
        "collectors",
    }
    collected_stream_names = {name for name, _ in collected_requesters}
    assert required_stream_names <= collected_stream_names

    response = Response()
    response.status_code = 429
    response.headers["X-Ratelimit-App-Global-Minute-Reset"] = "42"
    for _, requester in collected_requesters:
        backoff_strategies = requester._http_client._backoff_strategies
        assert len(backoff_strategies) == 1
        strategy = backoff_strategies[0]
        assert isinstance(strategy, WaitTimeFromHeaderBackoffStrategy)
        assert strategy.header.eval(config=new_source_config) == "X-Ratelimit-App-Global-Minute-Reset"
        assert strategy.backoff_time(response, attempt_count=1) == 42.0
