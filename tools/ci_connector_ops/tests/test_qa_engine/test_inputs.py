#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from importlib.resources import files

import pandas as pd
import pytest
from unittest.mock import MagicMock, call
import requests

from ci_connector_ops.qa_engine import inputs, constants

@pytest.mark.parametrize("catalog_url", [constants.OSS_CATALOG_URL, constants.CLOUD_CATALOG_URL])
def test_fetch_remote_catalog(catalog_url):
    catalog = inputs.fetch_remote_catalog(catalog_url)
    assert isinstance(catalog, pd.DataFrame)
    expected_columns = ["connector_type", "connector_definition_id"]
    assert all(expected_column in catalog.columns for expected_column in expected_columns)
    assert set(catalog.connector_type.unique()) == {"source", "destination"}

def test_fetch_adoption_metrics_per_connector_version(mocker):
    fake_bigquery_results = pd.DataFrame([{
        "connector_definition_id": "abcdefgh",
        "connector_version": "0.0.0",
        "number_of_connections": 10,
        "number_of_users": 2,
        "succeeded_syncs_count": 12,
        "failed_syncs_count": 1,
        "total_syncs_count": 3,
        "sync_success_rate": .99,
        "unexpected_column": "foobar"
    }])
    mocker.patch.object(inputs.pd, "read_gbq", mocker.Mock(return_value=fake_bigquery_results))
    mocker.patch.object(inputs.os, "environ", {"QA_ENGINE_AIRBYTE_DATA_PROD_SA": '{"type": "fake_service_account"}'})
    mocker.patch.object(inputs.service_account.Credentials, "from_service_account_info")
    expected_columns = {
        "connector_definition_id",
        "connector_version",
        "number_of_connections",
        "number_of_users",
        "succeeded_syncs_count",
        "failed_syncs_count",
        "total_syncs_count",
        "sync_success_rate",
    }
    expected_sql_query = files("ci_connector_ops.qa_engine").joinpath("connector_adoption.sql").read_text()
    expected_project_id = "airbyte-data-prod"
    adoption_metrics_per_connector_version = inputs.fetch_adoption_metrics_per_connector_version()
    assert isinstance(adoption_metrics_per_connector_version, pd.DataFrame)
    assert set(adoption_metrics_per_connector_version.columns) == expected_columns
    inputs.service_account.Credentials.from_service_account_info.assert_called_with(
        {"type": "fake_service_account"}
    )
    inputs.pd.read_gbq.assert_called_with(
        expected_sql_query,
        project_id=expected_project_id,
        credentials=inputs.service_account.Credentials.from_service_account_info.return_value
    )

@pytest.mark.parametrize("connector_name, connector_version, mocked_json_payload, mocked_status_code, expected_status", [
    (
        "connectors/source-pokeapi",
        "0.1.5",
        {
            "link": "https://github.com/airbytehq/airbyte/actions/runs/4029659593",
            "outcome": "success",
            "docker_version": "0.1.5",
            "timestamp": "1674872401",
            "connector": "connectors/source-pokeapi"
        },
        200,
        inputs.BUILD_STATUSES.SUCCESS
    ),
    (
        "connectors/source-pokeapi",
        "0.1.5",
        {
            "link": "https://github.com/airbytehq/airbyte/actions/runs/4029659593",
            "outcome": "failure",
            "docker_version": "0.1.5",
            "timestamp": "1674872401",
            "connector": "connectors/source-pokeapi"
        },
        200,
        inputs.BUILD_STATUSES.FAILURE
    ),
    (
        "connectors/source-pokeapi",
        "0.1.5",
        None,
        404,
        inputs.BUILD_STATUSES.NOT_FOUND
    ),
    (
        "connectors/source-pokeapi",
        "0.1.5",
        {
            "link": "https://github.com/airbytehq/airbyte/actions/runs/4029659593",
            "docker_version": "0.1.5",
            "timestamp": "1674872401",
            "connector": "connectors/source-pokeapi"
        },
        200,
        inputs.BUILD_STATUSES.NOT_FOUND
    ),
    (
        "connectors/source-pokeapi",
        "0.1.5",
        None,
        404,
        inputs.BUILD_STATUSES.NOT_FOUND
    ),
])
def test_fetch_latest_build_status_for_connector_version(mocker, connector_name, connector_version, mocked_json_payload, mocked_status_code, expected_status):
    # Mock the api call to get the latest build status for a connector version
    mock_response = MagicMock()
    mock_response.json.return_value = mocked_json_payload
    mock_response.status_code = mocked_status_code
    mock_get = mocker.patch.object(requests, 'get', return_value=mock_response)

    assert inputs.fetch_latest_build_status_for_connector_version(connector_name, connector_version) == expected_status
    assert mock_get.call_args == call(f"{constants.CONNECTOR_BUILD_OUTPUT_URL}/{connector_name}/version-{connector_version}.json")

def test_fetch_latest_build_status_for_connector_version_invalid_status(mocker, caplog):
    connector_name = "connectors/source-pokeapi"
    connector_version = "0.1.5"
    mocked_json_payload = {
        "link": "https://github.com/airbytehq/airbyte/actions/runs/4029659593",
        "outcome": "unknown_outcome_123",
        "docker_version": "0.1.5",
        "timestamp": "1674872401",
        "connector": "connectors/source-pokeapi"
    }
    # Mock the api call to get the latest build status for a connector version
    mock_response = MagicMock()
    mock_response.json.return_value = mocked_json_payload
    mock_response.status_code = 200
    mocker.patch.object(requests, 'get', return_value=mock_response)

    assert inputs.fetch_latest_build_status_for_connector_version(connector_name, connector_version) == inputs.BUILD_STATUSES.NOT_FOUND
    assert 'Error: Unexpected build status value: unknown_outcome_123 for connector connectors/source-pokeapi:0.1.5' in caplog.text
