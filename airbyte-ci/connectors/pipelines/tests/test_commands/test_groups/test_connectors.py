#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import Callable

import pytest
from click.testing import CliRunner
from connector_ops.utils import METADATA_FILE_NAME, ConnectorLanguage
from pipelines.bases import ConnectorWithModifiedFiles
from pipelines.commands.groups import connectors
from tests.utils import pick_a_random_connector


@pytest.fixture(scope="session")
def runner():
    return CliRunner()


def test_get_selected_connectors_by_name_no_file_modification():
    connector = pick_a_random_connector()
    selected_connectors = connectors.get_selected_connectors_with_modified_files(
        selected_names=(connector.technical_name,),
        selected_release_stages=(),
        selected_languages=(),
        modified=False,
        metadata_changes_only=False,
        modified_files=set(),
    )

    assert len(selected_connectors) == 1
    assert isinstance(selected_connectors[0], ConnectorWithModifiedFiles)
    assert selected_connectors[0].technical_name == connector.technical_name
    assert not selected_connectors[0].modified_files


def test_get_selected_connectors_by_release_stage_no_file_modification():
    selected_connectors = connectors.get_selected_connectors_with_modified_files(
        selected_names=(),
        selected_release_stages=("generally_available", "beta"),
        selected_languages=(),
        modified=False,
        metadata_changes_only=False,
        modified_files=set(),
    )

    set([c.release_stage for c in selected_connectors]) == {"generally_available", "beta"}


def test_get_selected_connectors_by_language_no_file_modification():
    selected_connectors = connectors.get_selected_connectors_with_modified_files(
        selected_names=(),
        selected_release_stages=(),
        selected_languages=(ConnectorLanguage.LOW_CODE,),
        modified=False,
        metadata_changes_only=False,
        modified_files=set(),
    )

    set([c.language for c in selected_connectors]) == {ConnectorLanguage.LOW_CODE}


def test_get_selected_connectors_by_name_with_file_modification():
    connector = pick_a_random_connector()
    modified_files = {connector.code_directory / "setup.py"}
    selected_connectors = connectors.get_selected_connectors_with_modified_files(
        selected_names=(connector.technical_name,),
        selected_release_stages=(),
        selected_languages=(),
        modified=False,
        metadata_changes_only=False,
        modified_files=modified_files,
    )

    assert len(selected_connectors) == 1
    assert isinstance(selected_connectors[0], ConnectorWithModifiedFiles)
    assert selected_connectors[0].technical_name == connector.technical_name
    assert selected_connectors[0].modified_files == modified_files


def test_get_selected_connectors_by_name_and_release_stage_or_languages_leads_to_intersection():
    connector = pick_a_random_connector()
    modified_files = {connector.code_directory / "setup.py"}
    selected_connectors = connectors.get_selected_connectors_with_modified_files(
        selected_names=(connector.technical_name,),
        selected_release_stages=(connector.release_stage,),
        selected_languages=(connector.language,),
        modified=False,
        metadata_changes_only=False,
        modified_files=modified_files,
    )

    assert len(selected_connectors) == 1


def test_get_selected_connectors_with_modified():
    first_modified_connector = pick_a_random_connector()
    second_modified_connector = pick_a_random_connector(other_picked_connectors=[first_modified_connector])
    modified_files = {first_modified_connector.code_directory / "setup.py", second_modified_connector.code_directory / "setup.py"}
    selected_connectors = connectors.get_selected_connectors_with_modified_files(
        selected_names=(),
        selected_release_stages=(),
        selected_languages=(),
        modified=True,
        metadata_changes_only=False,
        modified_files=modified_files,
    )

    assert len(selected_connectors) == 2


def test_get_selected_connectors_with_modified_and_language():
    first_modified_connector = pick_a_random_connector(language=ConnectorLanguage.PYTHON)
    second_modified_connector = pick_a_random_connector(language=ConnectorLanguage.JAVA, other_picked_connectors=[first_modified_connector])
    modified_files = {first_modified_connector.code_directory / "setup.py", second_modified_connector.code_directory / "setup.py"}
    selected_connectors = connectors.get_selected_connectors_with_modified_files(
        selected_names=(),
        selected_release_stages=(),
        selected_languages=(ConnectorLanguage.JAVA,),
        modified=True,
        metadata_changes_only=False,
        modified_files=modified_files,
    )

    assert len(selected_connectors) == 1
    assert selected_connectors[0].technical_name == second_modified_connector.technical_name


def test_get_selected_connectors_with_modified_and_release_stage():
    first_modified_connector = pick_a_random_connector(release_stage="alpha")
    second_modified_connector = pick_a_random_connector(
        release_stage="generally_available", other_picked_connectors=[first_modified_connector]
    )
    modified_files = {first_modified_connector.code_directory / "setup.py", second_modified_connector.code_directory / "setup.py"}
    selected_connectors = connectors.get_selected_connectors_with_modified_files(
        selected_names=(),
        selected_release_stages=("generally_available",),
        selected_languages=(),
        modified=True,
        metadata_changes_only=False,
        modified_files=modified_files,
    )

    assert len(selected_connectors) == 1
    assert selected_connectors[0].technical_name == second_modified_connector.technical_name


def test_get_selected_connectors_with_modified_and_metadata_only():
    first_modified_connector = pick_a_random_connector()
    second_modified_connector = pick_a_random_connector(other_picked_connectors=[first_modified_connector])
    modified_files = {
        first_modified_connector.code_directory / "setup.py",
        second_modified_connector.code_directory / METADATA_FILE_NAME,
        second_modified_connector.code_directory / "setup.py",
    }
    selected_connectors = connectors.get_selected_connectors_with_modified_files(
        selected_names=(),
        selected_release_stages=(),
        selected_languages=(),
        modified=True,
        metadata_changes_only=True,
        modified_files=modified_files,
    )

    assert len(selected_connectors) == 1
    assert selected_connectors[0].technical_name == second_modified_connector.technical_name
    assert selected_connectors[0].modified_files == {
        second_modified_connector.code_directory / METADATA_FILE_NAME,
        second_modified_connector.code_directory / "setup.py",
    }


def test_get_selected_connectors_with_metadata_only():
    first_modified_connector = pick_a_random_connector()
    second_modified_connector = pick_a_random_connector(other_picked_connectors=[first_modified_connector])
    modified_files = {
        first_modified_connector.code_directory / "setup.py",
        second_modified_connector.code_directory / METADATA_FILE_NAME,
        second_modified_connector.code_directory / "setup.py",
    }
    selected_connectors = connectors.get_selected_connectors_with_modified_files(
        selected_names=(),
        selected_release_stages=(),
        selected_languages=(),
        modified=False,
        metadata_changes_only=True,
        modified_files=modified_files,
    )

    assert len(selected_connectors) == 1
    assert selected_connectors[0].technical_name == second_modified_connector.technical_name
    assert selected_connectors[0].modified_files == {
        second_modified_connector.code_directory / METADATA_FILE_NAME,
        second_modified_connector.code_directory / "setup.py",
    }


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
        "selected_connectors_with_modified_files": {},
        "gha_workflow_run_url": None,
        "ci_report_bucket_name": None,
        "use_remote_secrets": False,
        "ci_gcs_credentials": None,
        "execute_timeout": 0,
        "concurrency": 1,
        "ci_git_user": None,
        "ci_github_access_token": None,
    }


@pytest.mark.parametrize(
    "command, command_args",
    [
        (connectors.test, []),
        (
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
        ),
        (connectors.format_code, []),
        (connectors.build, []),
    ],
)
def test_commands_do_not_override_connector_selection(
    mocker, runner: CliRunner, click_context_obj: dict, command: Callable, command_args: list
):
    """
    This test is here to make sure that the commands do not override the connector selection
    This is important because we want to control the connector selection in a single place.
    """

    selected_connector = mocker.MagicMock()
    click_context_obj["selected_connectors_with_modified_files"] = [selected_connector]

    mocker.patch.object(connectors.click, "confirm")
    mock_connector_context = mocker.MagicMock()
    mocker.patch.object(connectors, "ConnectorContext", mock_connector_context)
    mocker.patch.object(connectors, "PublishConnectorContext", mock_connector_context)
    runner.invoke(command, command_args, catch_exceptions=False, obj=click_context_obj)
    assert mock_connector_context.call_count == 1
    # If the connector selection is overriden the context won't be instantiated with the selected connector mock instance
    assert mock_connector_context.call_args_list[0].kwargs["connector"] == selected_connector
