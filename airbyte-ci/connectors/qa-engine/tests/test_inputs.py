#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from importlib.resources import files
from unittest.mock import MagicMock, call

import pandas as pd
import pytest
import requests
from qa_engine import constants, inputs


@pytest.mark.parametrize("catalog_url", [constants.OSS_CATALOG_URL, constants.CLOUD_CATALOG_URL])
def test_fetch_remote_catalog(catalog_url):
    catalog = inputs.fetch_remote_catalog(catalog_url)
    assert isinstance(catalog, pd.DataFrame)
    expected_columns = ["connector_type", "connector_definition_id"]
    assert all(expected_column in catalog.columns for expected_column in expected_columns)
    assert set(catalog.connector_type.unique()) == {"source", "destination"}


def test_fetch_adoption_metrics_per_connector_version(mocker):
    fake_bigquery_results = pd.DataFrame(
        [
            {
                "connector_definition_id": "abcdefgh",
                "connector_version": "0.0.0",
                "number_of_connections": 10,
                "number_of_users": 2,
                "succeeded_syncs_count": 12,
                "failed_syncs_count": 1,
                "total_syncs_count": 3,
                "sync_success_rate": 0.99,
                "unexpected_column": "foobar",
            }
        ]
    )
    mocker.patch.object(inputs.pd, "read_gbq", mocker.Mock(return_value=fake_bigquery_results))
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
    expected_sql_query = files("qa_engine").joinpath("connector_adoption.sql").read_text()
    expected_project_id = "airbyte-data-prod"
    adoption_metrics_per_connector_version = inputs.fetch_adoption_metrics_per_connector_version()
    assert isinstance(adoption_metrics_per_connector_version, pd.DataFrame)
    assert set(adoption_metrics_per_connector_version.columns) == expected_columns
    inputs.pd.read_gbq.assert_called_with(expected_sql_query, project_id=expected_project_id)


@pytest.mark.parametrize(
    "connector_name, mocked_json_payload, mocked_status_code, expected_status",
    [
        (
            "connectors/source-pokeapi",
            [
                {
                    "connector_version": "0.3.0",
                    "success": True,
                    "gha_workflow_run_url": "https://github.com/airbytehq/airbyte/actions/runs/5222619538",
                    "date": "2023-06-09T06:50:04",
                },
                {
                    "connector_version": "0.3.0",
                    "success": False,
                    "gha_workflow_run_url": "https://github.com/airbytehq/airbyte/actions/runs/5220000547",
                    "date": "2023-06-09T01:42:46",
                },
            ],
            200,
            inputs.BUILD_STATUSES.SUCCESS,
        ),
        (
            "connectors/source-pokeapi",
            [
                {
                    "connector_version": "0.3.0",
                    "success": False,
                    "gha_workflow_run_url": "https://github.com/airbytehq/airbyte/actions/runs/5222619538",
                    "date": "2023-06-09T06:50:04",
                },
                {
                    "connector_version": "0.3.0",
                    "success": True,
                    "gha_workflow_run_url": "https://github.com/airbytehq/airbyte/actions/runs/5220000547",
                    "date": "2023-06-09T01:42:46",
                },
            ],
            200,
            inputs.BUILD_STATUSES.FAILURE,
        ),
        ("connectors/source-pokeapi", None, 404, inputs.BUILD_STATUSES.NOT_FOUND),
        (
            "connectors/source-pokeapi",
            [
                {
                    "connector_version": "0.3.0",
                    "success": None,
                    "gha_workflow_run_url": "https://github.com/airbytehq/airbyte/actions/runs/5222619538",
                    "date": "2023-06-09T06:50:04",
                }
            ],
            200,
            inputs.BUILD_STATUSES.NOT_FOUND,
        ),
        ("connectors/source-pokeapi", None, 404, inputs.BUILD_STATUSES.NOT_FOUND),
    ],
)
def test_fetch_latest_build_status_for_connector(mocker, connector_name, mocked_json_payload, mocked_status_code, expected_status):
    # Mock the api call to get the latest build status for a connector version
    mock_response = MagicMock()
    mock_response.json.return_value = mocked_json_payload
    mock_response.status_code = mocked_status_code
    mock_get = mocker.patch.object(requests, "get", return_value=mock_response)
    connector_name = connector_name.replace("connectors/", "")

    assert inputs.fetch_latest_build_status_for_connector(connector_name) == expected_status
    assert mock_get.call_args == call(f"{constants.CONNECTOR_TEST_SUMMARY_URL}/{connector_name}/index.json")


def test_fetch_latest_build_status_for_connector_invalid_status(mocker, caplog):
    connector_name = "connectors/source-pokeapi"
    mocked_json_payload = [
        {
            "connector_version": "0.3.0",
            "success": "unknown_outcome_123",
            "gha_workflow_run_url": "https://github.com/airbytehq/airbyte/actions/runs/5222619538",
            "date": "2023-06-09T06:50:04",
        },
        {
            "connector_version": "0.3.0",
            "success": False,
            "gha_workflow_run_url": "https://github.com/airbytehq/airbyte/actions/runs/5220000547",
            "date": "2023-06-09T01:42:46",
        },
        {
            "connector_version": "0.3.0",
            "success": True,
            "gha_workflow_run_url": "https://github.com/airbytehq/airbyte/actions/runs/5212578854",
            "date": "2023-06-08T07:46:37",
        },
        {
            "connector_version": "0.3.0",
            "success": True,
            "gha_workflow_run_url": "https://github.com/airbytehq/airbyte/actions/runs/5198665885",
            "date": "2023-06-07T03:05:40",
        },
    ]
    # Mock the api call to get the latest build status for a connector version
    mock_response = MagicMock()
    mock_response.json.return_value = mocked_json_payload
    mock_response.status_code = 200
    mocker.patch.object(requests, "get", return_value=mock_response)

    assert inputs.fetch_latest_build_status_for_connector(connector_name) == inputs.BUILD_STATUSES.NOT_FOUND
    assert "Error: Unexpected build status value: unknown_outcome_123 for connector connectors/source-pokeapi" in caplog.text
