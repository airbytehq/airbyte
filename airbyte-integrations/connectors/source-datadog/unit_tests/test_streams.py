#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import MagicMock, patch

import pytest
import requests
import requests_mock as req_mock
from airbyte_cdk.models import SyncMode
from source_datadog.source import SourceDatadog
from source_datadog.streams import (
    AuditLogs,
    Dashboards,
    DatadogStream,
    Downtimes,
    Incidents,
    IncidentTeams,
    Logs,
    Metrics,
    SeriesStream,
    SyntheticTests,
    Users,
)


@pytest.mark.parametrize(
    "stream",
    [AuditLogs, Dashboards, Downtimes, Incidents, IncidentTeams, Logs, Metrics, SyntheticTests, Users],
)
def test_task_stream(requests_mock, stream, config, mock_responses):
    requests_mock.get(req_mock.ANY, json=mock_responses.get(stream.__name__))
    requests_mock.post(req_mock.ANY, json=mock_responses.get(stream.__name__))
    args = SourceDatadog().connector_config(config)
    instance = stream(**args)

    stream_slice = instance.stream_slices(sync_mode=SyncMode.full_refresh)
    record = next(instance.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice))

    assert record


@patch.multiple(DatadogStream, __abstractmethods__=set())
def test_next_page_token(config):
    stream = DatadogStream(
        site=config["site"],
        query=config["query"],
        max_records_per_request=config["max_records_per_request"],
        start_date=config["start_date"],
        end_date=config["end_date"],
        query_start_date=config["start_date"],
        query_end_date=config["end_date"],
    )
    inputs = {"response": MagicMock()}
    assert stream.next_page_token(**inputs) is None


def test_site_config(config):
    assert config['site'] == 'datadoghq.com'


def test_site_config_eu(config_eu):
    assert config_eu['site'] == 'datadoghq.eu'


@pytest.mark.parametrize(
    "stream",
    [AuditLogs, Dashboards, Downtimes, Incidents, IncidentTeams, Logs, Metrics, SyntheticTests, Users],
)
def test_next_page_token_empty_response(stream, config):
    expected_token = None
    args = SourceDatadog().connector_config(config)
    instance = stream(**args)
    response = requests.Response()
    response._content = json.dumps({}).encode("utf-8")
    assert instance.next_page_token(response=response) == expected_token


@pytest.mark.parametrize(
    "stream",
    [AuditLogs, Logs],
)
def test_next_page_token_inc(stream, config):
    args = SourceDatadog().connector_config(config)
    instance = stream(**args)
    response = requests.Response()
    body_content = {"meta": {"page": {"after": "test_cursor"}}}
    response._content = json.dumps(body_content).encode("utf-8")
    result = instance.next_page_token(response=response)
    assert result.get("page").get("cursor") == "test_cursor"


@pytest.mark.parametrize(
    "stream",
    [Incidents, IncidentTeams],
)
def test_next_page_token_paginated(stream, config):
    args = SourceDatadog().connector_config(config)
    instance = stream(**args)
    response = requests.Response()
    body_content = {
        "meta": {
            "pagination": {
                "offset": 998,
                "next_offset": 999,
            }
        }
    }
    response._content = json.dumps(body_content).encode("utf-8")
    result = instance.next_page_token(response=response)
    assert result.get("offset") == 999


@patch.multiple(DatadogStream, __abstractmethods__=set())
def test_site_parameter_is_set(config):
    site = "example.com"
    stream = DatadogStream(
        site=site,
        query=config["query"],
        max_records_per_request=config["max_records_per_request"],
        start_date=config["start_date"],
        end_date=config["end_date"],
        query_start_date=config["start_date"],
        query_end_date=config["end_date"],
    )
    url_base = stream.url_base
    expected_url_base = f"https://api.{site}/api"
    assert url_base == expected_url_base


@patch.multiple(DatadogStream, __abstractmethods__=set())
def test_site_parameter_is_not_set(config):
    stream = DatadogStream(
        site=config["site"],
        query=config["query"],
        max_records_per_request=config["max_records_per_request"],
        start_date=config["start_date"],
        end_date=config["end_date"],
        query_start_date=config["start_date"],
        query_end_date=config["end_date"],
    )
    url_base = stream.url_base
    expected_url_base = "https://api.datadoghq.com/api"
    assert url_base == expected_url_base


@patch.multiple(SeriesStream, __abstractmethods__=set())
def test_request_body_json(config):
    stream = SeriesStream(
        site=config["site"],
        query=config["query"],
        max_records_per_request=config["max_records_per_request"],
        start_date=config["start_date"],
        end_date=config["end_date"],
        query_start_date="2023-01-01T00:00:00Z",
        query_end_date="2023-02-01T00:00:00Z",
        name="test_stream",
        data_source="metrics",
        query_string="test_query"
    )
    stream_state = {
        "stream_state_key": "value"
    }
    expected_payload = {
        "data": {
            "type": "timeseries_request",
            "attributes": {
                "to": 1675209600000,
                "from": 1672531200000,
                "queries": [
                    {
                        "data_source": "metrics",
                        "query": "test_query",
                        "name": "test_stream"
                    }
                ]
            }
        }
    }
    payload = stream.request_body_json(stream_state)
    assert payload == expected_payload


@patch.multiple(SeriesStream, __abstractmethods__=set())
def test_get_json_schema(config):
    stream = SeriesStream(
        site=config["site"],
        query=config["query"],
        max_records_per_request=config["max_records_per_request"],
        start_date=config["start_date"],
        end_date=config["end_date"],
        query_start_date=config["start_date"],
        query_end_date=config["end_date"],
        name="test_stream",
        data_source="metrics",
        query_string="test_query"
    )
    expected_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {},
        "additionalProperties": True
    }
    assert stream.get_json_schema() == expected_schema
