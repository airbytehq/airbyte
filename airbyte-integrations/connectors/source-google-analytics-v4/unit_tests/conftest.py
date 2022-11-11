#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import copy
import json
from pathlib import Path

import pendulum
import pytest
from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.streams.http.auth import NoAuth


def read_file(file_name):
    parent_location = Path(__file__).absolute().parent
    file = open(parent_location / file_name).read()
    return file


@pytest.fixture
def mock_metrics_dimensions_type_list_link(requests_mock):
    requests_mock.get(
        "https://www.googleapis.com/analytics/v3/metadata/ga/columns",
        json=json.loads(read_file("metrics_dimensions_type_list.json")),
    )


@pytest.fixture
def mock_auth_call(requests_mock):
    yield requests_mock.post(
        "https://oauth2.googleapis.com/token",
        json={"access_token": "", "expires_in": 0},
    )


@pytest.fixture
def mock_auth_check_connection(requests_mock):
    yield requests_mock.post(
        "https://analyticsreporting.googleapis.com/v4/reports:batchGet",
        json={"data": {"test": "value"}},
    )


@pytest.fixture
def mock_unknown_metrics_or_dimensions_error(requests_mock):
    yield requests_mock.post(
        "https://analyticsreporting.googleapis.com/v4/reports:batchGet",
        status_code=400,
        json={"error": {"message": "Unknown metrics or dimensions"}},
    )


@pytest.fixture
def mock_daily_request_limit_error(requests_mock):
    yield requests_mock.post(
        "https://analyticsreporting.googleapis.com/v4/reports:batchGet",
        status_code=429,
        json={"error": {"code": 429, "message": "Quota Error: profileId 207066566 has exceeded the daily request limit."}},
    )


@pytest.fixture
def mock_api_returns_no_records(requests_mock):
    """API returns empty data for given date based slice"""
    yield requests_mock.post(
        "https://analyticsreporting.googleapis.com/v4/reports:batchGet",
        json=json.loads(read_file("empty_response.json")),
    )


@pytest.fixture
def mock_api_returns_valid_records(requests_mock):
    """API returns valid data for given date based slice"""
    response = json.loads(read_file("response_golden_data.json"))
    for report in response["reports"]:
        assert report["data"]["isDataGolden"] is True
    yield requests_mock.post("https://analyticsreporting.googleapis.com/v4/reports:batchGet", json=response)


@pytest.fixture
def mock_api_returns_sampled_results(requests_mock):
    """API returns valid data for given date based slice"""
    yield requests_mock.post(
        "https://analyticsreporting.googleapis.com/v4/reports:batchGet",
        json=json.loads(read_file("response_with_sampling.json")),
    )


@pytest.fixture
def mock_api_returns_is_data_golden_false(requests_mock):
    """API returns valid data for given date based slice"""
    response = json.loads(read_file("response_non_golden_data.json"))
    for report in response["reports"]:
        assert "isDataGolden" not in report["data"]
    yield requests_mock.post("https://analyticsreporting.googleapis.com/v4/reports:batchGet", json=response)


@pytest.fixture
def configured_catalog():
    return ConfiguredAirbyteCatalog.parse_obj(json.loads(read_file("./configured_catalog.json")))


@pytest.fixture()
def test_config():
    test_conf = {
        "view_id": "1234567",
        "window_in_days": 1,
        "authenticator": NoAuth(),
        "metrics": [],
        "start_date": pendulum.now().subtract(days=2).date().strftime("%Y-%m-%d"),
        "dimensions": [],
        "credentials": {
            "auth_type": "Client",
            "client_id": "client_id_val",
            "client_secret": "client_secret_val",
            "refresh_token": "refresh_token_val",
        },
    }
    return copy.deepcopy(test_conf)


@pytest.fixture()
def test_config_auth_service(test_config):
    test_config["credentials"] = {
        "auth_type": "Service",
        "credentials_json": '{"client_email": "", "private_key": "", "private_key_id": ""}',
    }
    return copy.deepcopy(test_config)
