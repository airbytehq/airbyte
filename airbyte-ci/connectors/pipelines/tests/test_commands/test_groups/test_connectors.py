#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from pathlib import Path

import pytest
from click.testing import CliRunner
from connector_ops.utils import Connector
from pipelines.commands.groups import connectors


@pytest.fixture(scope="session")
def runner():
    return CliRunner()


@pytest.fixture()
def click_context_obj():
    return {
        "git_branch": "test_branch",
        "git_revision": "test_revision",
        "pipeline_start_timestamp": 0,
        "ci_context": "manual",
        "show_dagger_logs": False,
        "is_local": True,
        "is_ci": False,
        "select_modified_connectors": False,
        "selected_connectors_and_files": {},
        "gha_workflow_run_url": None,
        "ci_report_bucket_name": None,
        "use_remote_secrets": False,
        "ci_gcs_credentials": None,
        "execute_timeout": 0,
    }


def test_test_command_select_modified_connectors(mocker, runner: CliRunner, click_context_obj: dict, new_connector: Connector):
    """Test that on test all the modified connectors, even the new ones, are tested."""
    click_context_obj["select_modified_connectors"] = True
    click_context_obj["modified_files"] = [
        Path("airbyte-integrations/connectors/source-pokeapi/setup.py"),
        new_connector.code_directory / "metadata.yaml",
    ]
    mock_connector_context = mocker.MagicMock()
    mocker.patch.object(connectors, "ConnectorContext", mock_connector_context)
    runner.invoke(connectors.test, catch_exceptions=False, obj=click_context_obj)
    assert click_context_obj["selected_connectors_and_files"] == {
        Connector("source-pokeapi"): [Path("airbyte-integrations/connectors/source-pokeapi/setup.py")],
        Connector("source-new-connector"): [new_connector.code_directory / "metadata.yaml"],
    }
    assert mock_connector_context.call_count == 2
    mock_connector_context.call_args_list[0].kwargs["connector"] == Connector("source-pokeapi")
    mock_connector_context.call_args_list[0].kwargs["modified_files"] == [Path("airbyte-integrations/connectors/source-pokeapi/setup.py")]
    mock_connector_context.call_args_list[1].kwargs["connector"] == Connector("source-new-connector")
    mock_connector_context.call_args_list[1].kwargs["modified_files"] == [new_connector.code_directory / "metadata.yaml"]


def test_test_command_select_selected_connectors(mocker, runner: CliRunner, click_context_obj: dict, new_connector: Connector):
    """Test that on test a selected connectors is tested and the other modified one are not if select_modified_connectors is not False."""

    click_context_obj["selected_connectors_and_files"] = {
        Connector("source-openweather"): [Path("airbyte-integrations/connectors/source-openweather/setup.py")],
    }
    pre_selected_connectors_and_files = click_context_obj["selected_connectors_and_files"]

    click_context_obj["modified_files"] = [
        Path("airbyte-integrations/connectors/source-pokeapi/setup.py"),
        new_connector.code_directory / "metadata.yaml",
        Path("airbyte-integrations/connectors/source-openweather/setup.py"),
    ]

    click_context_obj["select_modified_connectors"] = False
    mock_connector_context = mocker.MagicMock()
    mocker.patch.object(connectors, "ConnectorContext", mock_connector_context)
    runner.invoke(connectors.test, catch_exceptions=False, obj=click_context_obj)

    assert click_context_obj["selected_connectors_and_files"] == pre_selected_connectors_and_files
    assert mock_connector_context.call_count == 1
    mock_connector_context.call_args_list[0].kwargs["connector"] == Connector("source-openwehater")
    mock_connector_context.call_args_list[0].kwargs["modified_files"] == [
        Path("airbyte-integrations/connectors/source-openweather/setup.py")
    ]


def test_publish_command_select_modified_connectors(mocker, runner: CliRunner, click_context_obj: dict, new_connector: Connector):
    """Test that on publish only the connectors with modified metadata.yaml files are published."""
    click_context_obj["select_modified_connectors"] = True
    click_context_obj["modified_files"] = [
        Path("airbyte-integrations/connectors/source-pokeapi/setup.py"),
        new_connector.code_directory / "metadata.yaml",
    ]
    mock_connector_context = mocker.MagicMock()
    mocker.patch.object(connectors, "PublishConnectorContext", mock_connector_context)
    mocker.patch.object(connectors.click, "confirm")

    runner.invoke(
        connectors.publish,
        [
            "--spec-cache-gcs-credentials",
            "test",
            "--spec-cache-bucket-name",
            "test",
            "--metadata-service-gcs-credentials",
            "test",
            "--metadata-service-bucket-name",
            "test",
            "--docker-hub-username",
            "test",
            "--docker-hub-password",
            "test",
        ],
        catch_exceptions=False,
        obj=click_context_obj,
    )
    assert click_context_obj["selected_connectors_and_files"] == {
        Connector("source-new-connector"): [new_connector.code_directory / "metadata.yaml"]
    }
    assert mock_connector_context.call_count == 1
    mock_connector_context.call_args_list[0].kwargs["connector"] == Connector("source-new-connector")
    mock_connector_context.call_args_list[0].kwargs["modified_files"] == [new_connector.code_directory / "metadata.yaml"]
