# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import copy
import logging
from typing import Dict

import pytest

from airbyte_cdk.sources.streams.http.exceptions import BaseBackoffException
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

from .records import (
    breakdowns_record,
    children_record,
    clear_url_record,
    clear_url_record_transformed,
    expected_breakdown_record_transformed,
    expected_children_transformed,
    insights_record,
    insights_record_transformed,
)


def mock_path(requests_mock, graph_url: str, path: str, method: str = "GET", response: Dict = None):
    complete_url = f"{graph_url}/{path}"
    requests_mock.register_uri(method, complete_url, json=response)


def test_instagram_media_children_transformation(components_module, requests_mock, config):
    graph_url = components_module.GRAPH_URL

    params = "?fields=id,ig_id,media_type,media_url,owner,permalink,shortcode,thumbnail_url,timestamp,username"
    children_record_data = children_record["children"]["data"]
    expected_children_transformed_data = expected_children_transformed["children"]
    for index in range(len(children_record_data)):
        mock_path(
            requests_mock,
            graph_url=graph_url,
            path=f"{children_record_data[index]['id']}{params}",
            response=expected_children_transformed_data[index],
        )

    record_transformation = components_module.InstagramMediaChildrenTransformation()
    transformation_result = record_transformation.transform(children_record, config)
    assert transformation_result == expected_children_transformed


def test_instagram_clear_url_transformation(components_module):
    record_transformation = components_module.InstagramClearUrlTransformation().transform(clear_url_record)
    assert record_transformation == clear_url_record_transformed


def test_break_down_results_transformation(components_module):
    record_transformation_result = components_module.InstagramBreakDownResultsTransformation().transform(breakdowns_record)
    assert record_transformation_result == expected_breakdown_record_transformed


def test_instagram_insights_transformation(components_module, config):
    record_transformation = components_module.InstagramInsightsTransformation().transform(insights_record)
    assert record_transformation == insights_record_transformed


def test_instagram_media_children_transformation_skips_failed_child(components_module, config, mocker):
    """When one carousel child returns an HTTP error, the transform should skip it and return the rest."""
    # Use fresh data since the module-level children_record is mutated in-place by the earlier happy-path test
    original_children_data = [{"id": "7608776690540"}, {"id": "2896800415362"}, {"id": "9559889460059"}, {"id": "7359925580923"}]
    expected_children_transformed_data = expected_children_transformed["children"]
    failing_index = 1  # second child will fail

    def mock_get_http_response(name, path, request_params, config):
        for index, child in enumerate(original_children_data):
            if child["id"] == path:
                if index == failing_index:
                    raise AirbyteTracedException(message="HTTP error occurred: 400 - Bad request")
                return copy.deepcopy(expected_children_transformed_data[index])
        raise AirbyteTracedException(message=f"Unexpected child ID: {path}")

    mocker.patch.object(components_module, "get_http_response", side_effect=mock_get_http_response)

    record_transformation = components_module.InstagramMediaChildrenTransformation()
    input_record = {"id": "parent_media_123", "children": {"data": copy.deepcopy(original_children_data)}}
    result = record_transformation.transform(input_record, config)

    # The failed child should be skipped; 3 children should remain
    assert len(result["children"]) == 3
    result_ids = [c["id"] for c in result["children"]]
    assert original_children_data[failing_index]["id"] not in result_ids


def test_instagram_media_children_transformation_all_children_fail(components_module, config, mocker):
    """When all carousel children fail, the transform should return an empty children array."""
    # Use fresh data since the module-level children_record is mutated in-place by the earlier happy-path test
    fresh_record = {
        "children": {"data": [{"id": "7608776690540"}, {"id": "2896800415362"}, {"id": "9559889460059"}, {"id": "7359925580923"}]}
    }
    mocker.patch.object(
        components_module,
        "get_http_response",
        side_effect=AirbyteTracedException(message="HTTP error occurred: 500 - Internal server error"),
    )

    record_transformation = components_module.InstagramMediaChildrenTransformation()
    result = record_transformation.transform(fresh_record, config)

    assert result["children"] == []


def test_instagram_media_children_transformation_logs_warning_on_failure(components_module, config, mocker, caplog):
    """When a child fetch fails, a warning should be logged identifying the child and parent IDs."""
    failing_child_id = "7608776690540"
    parent_record = {"id": "parent_media_456", "children": {"data": [{"id": failing_child_id}]}}

    mocker.patch.object(
        components_module, "get_http_response", side_effect=AirbyteTracedException(message="HTTP error occurred: 403 - Permission denied")
    )

    record_transformation = components_module.InstagramMediaChildrenTransformation()
    with caplog.at_level(logging.WARNING):
        result = record_transformation.transform(copy.deepcopy(parent_record), config)

    assert result["children"] == []
    assert any(failing_child_id in msg and "parent_media_456" in msg for msg in caplog.messages)


@pytest.mark.parametrize(
    "error_response",
    [
        pytest.param(
            {
                "error": {
                    "message": "(#80002) There have been too many calls to this Instagram account.",
                    "type": "OAuthException",
                    "code": 80002,
                    "fbtrace_id": "abc123",
                }
            },
            id="instagram_rate_limit_error_code_80002",
        ),
        pytest.param(
            {
                "error": {
                    "message": "Application request limit reached.",
                    "type": "OAuthException",
                    "code": 4,
                    "fbtrace_id": "xyz789",
                }
            },
            id="application_rate_limit_error_code_4",
        ),
        pytest.param(
            {
                "error": {
                    "message": "too many calls to this account.",
                    "type": "OAuthException",
                    "code": 32,
                    "fbtrace_id": "def456",
                }
            },
            id="too_many_calls_error_message",
        ),
    ],
)
def test_get_http_response_raises_on_rate_limit(components_module, requests_mock, config, error_response):
    """Rate limit responses (HTTP 400 with known rate limit indicators) should
    retry and then raise with a descriptive error message preserving rate limit context."""
    graph_url = components_module.GRAPH_URL
    requests_mock.register_uri(
        "GET",
        f"{graph_url}/test_media_id?fields=id",
        status_code=400,
        json=error_response,
    )

    with pytest.raises((AirbyteTracedException, BaseBackoffException)) as exc_info:
        components_module.get_http_response("test_stream", "test_media_id", {"fields": "id"}, config=config)

    assert "Rate limit exceeded for Instagram Graph API." in str(exc_info.value)


def test_get_http_response_non_rate_limit_400_fails_immediately(components_module, requests_mock, config):
    """Non-rate-limit HTTP 400 errors should fail immediately without retrying."""
    graph_url = components_module.GRAPH_URL
    requests_mock.register_uri(
        "GET",
        f"{graph_url}/test_media_id?fields=id",
        status_code=400,
        json={
            "error": {
                "message": "Invalid parameter",
                "type": "OAuthException",
                "code": 100,
                "fbtrace_id": "test123",
            }
        },
    )

    with pytest.raises(AirbyteTracedException):
        components_module.get_http_response("test_stream", "test_media_id", {"fields": "id"}, config=config)


def test_get_http_response_success(components_module, requests_mock, config):
    """Successful responses should return the JSON body without raising."""
    graph_url = components_module.GRAPH_URL
    expected_data = {"id": "12345", "media_type": "IMAGE"}
    requests_mock.register_uri(
        "GET",
        f"{graph_url}/test_media_id?fields=id",
        status_code=200,
        json=expected_data,
    )

    result = components_module.get_http_response("test_stream", "test_media_id", {"fields": "id"}, config=config)
    assert result == expected_data


def test_get_http_response_raises_specific_exception_on_server_error(components_module, requests_mock, config):
    """Server errors should propagate as typed exceptions (not generic `Exception`),
    preserving the original error context for proper Airbyte error classification."""
    graph_url = components_module.GRAPH_URL
    requests_mock.register_uri(
        "GET",
        f"{graph_url}/test_media_id?fields=id",
        status_code=500,
        json={"error": {"message": "Internal server error"}},
    )

    with pytest.raises((AirbyteTracedException, BaseBackoffException)):
        components_module.get_http_response("test_stream", "test_media_id", {"fields": "id"}, config=config)
