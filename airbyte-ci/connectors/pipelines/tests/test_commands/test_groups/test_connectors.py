#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Callable

import asyncclick as click
import pytest
from asyncclick.testing import CliRunner
from connector_ops.utils import METADATA_FILE_NAME, ConnectorLanguage
from pipelines.airbyte_ci.connectors import commands as connectors_commands
from pipelines.airbyte_ci.connectors.build_image import commands as connectors_build_command
from pipelines.airbyte_ci.connectors.publish import commands as connectors_publish_command
from pipelines.airbyte_ci.connectors.test import commands as connectors_test_command
from pipelines.helpers.connectors.modifed import ConnectorWithModifiedFiles
from tests.utils import pick_a_random_connector


@pytest.fixture(scope="session")
def runner():
    return CliRunner()


def test_get_selected_connectors_by_name_no_file_modification():
    connector = pick_a_random_connector()
    selected_connectors = connectors_commands.get_selected_connectors_with_modified_files(
        selected_names=(connector.technical_name,),
        selected_support_levels=(),
        selected_languages=(),
        modified=False,
        metadata_changes_only=False,
        metadata_query=None,
        modified_files=set(),
    )

    assert len(selected_connectors) == 1
    assert isinstance(selected_connectors[0], ConnectorWithModifiedFiles)
    assert selected_connectors[0].technical_name == connector.technical_name
    assert not selected_connectors[0].modified_files


def test_get_selected_connectors_by_support_level_no_file_modification():
    selected_connectors = connectors_commands.get_selected_connectors_with_modified_files(
        selected_names=(),
        selected_support_levels=["certified"],
        selected_languages=(),
        modified=False,
        metadata_changes_only=False,
        metadata_query=None,
        modified_files=set(),
    )

    set([c.support_level for c in selected_connectors]) == {"certified"}


def test_get_selected_connectors_by_language_no_file_modification():
    selected_connectors = connectors_commands.get_selected_connectors_with_modified_files(
        selected_names=(),
        selected_support_levels=(),
        selected_languages=(ConnectorLanguage.LOW_CODE,),
        modified=False,
        metadata_changes_only=False,
        metadata_query=None,
        modified_files=set(),
    )

    set([c.language for c in selected_connectors]) == {ConnectorLanguage.LOW_CODE}


def test_get_selected_connectors_by_name_with_file_modification():
    connector = pick_a_random_connector()
    modified_files = {connector.code_directory / "setup.py"}
    selected_connectors = connectors_commands.get_selected_connectors_with_modified_files(
        selected_names=(connector.technical_name,),
        selected_support_levels=(),
        selected_languages=(),
        modified=False,
        metadata_changes_only=False,
        metadata_query=None,
        modified_files=modified_files,
    )

    assert len(selected_connectors) == 1
    assert isinstance(selected_connectors[0], ConnectorWithModifiedFiles)
    assert selected_connectors[0].technical_name == connector.technical_name
    assert selected_connectors[0].modified_files == modified_files


def test_get_selected_connectors_by_name_and_support_level_or_languages_leads_to_intersection():
    connector = pick_a_random_connector()
    modified_files = {connector.code_directory / "setup.py"}
    selected_connectors = connectors_commands.get_selected_connectors_with_modified_files(
        selected_names=(connector.technical_name,),
        selected_support_levels=(connector.support_level,),
        selected_languages=(connector.language,),
        modified=False,
        metadata_changes_only=False,
        metadata_query=None,
        modified_files=modified_files,
    )

    assert len(selected_connectors) == 1


def test_get_selected_connectors_with_modified():
    first_modified_connector = pick_a_random_connector()
    second_modified_connector = pick_a_random_connector(other_picked_connectors=[first_modified_connector])
    modified_files = {first_modified_connector.code_directory / "setup.py", second_modified_connector.code_directory / "setup.py"}
    selected_connectors = connectors_commands.get_selected_connectors_with_modified_files(
        selected_names=(),
        selected_support_levels=(),
        selected_languages=(),
        modified=True,
        metadata_changes_only=False,
        metadata_query=None,
        modified_files=modified_files,
    )

    assert len(selected_connectors) == 2


def test_get_selected_connectors_with_modified_and_language():
    first_modified_connector = pick_a_random_connector(language=ConnectorLanguage.PYTHON)
    second_modified_connector = pick_a_random_connector(language=ConnectorLanguage.JAVA, other_picked_connectors=[first_modified_connector])
    modified_files = {first_modified_connector.code_directory / "setup.py", second_modified_connector.code_directory / "setup.py"}
    selected_connectors = connectors_commands.get_selected_connectors_with_modified_files(
        selected_names=(),
        selected_support_levels=(),
        selected_languages=(ConnectorLanguage.JAVA,),
        modified=True,
        metadata_changes_only=False,
        metadata_query=None,
        modified_files=modified_files,
    )

    assert len(selected_connectors) == 1
    assert selected_connectors[0].technical_name == second_modified_connector.technical_name


def test_get_selected_connectors_with_modified_and_support_level():
    first_modified_connector = pick_a_random_connector(support_level="community")
    second_modified_connector = pick_a_random_connector(support_level="certified", other_picked_connectors=[first_modified_connector])
    modified_files = {first_modified_connector.code_directory / "setup.py", second_modified_connector.code_directory / "setup.py"}
    selected_connectors = connectors_commands.get_selected_connectors_with_modified_files(
        selected_names=(),
        selected_support_levels=["certified"],
        selected_languages=(),
        modified=True,
        metadata_changes_only=False,
        metadata_query=None,
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
    selected_connectors = connectors_commands.get_selected_connectors_with_modified_files(
        selected_names=(),
        selected_support_levels=(),
        selected_languages=(),
        modified=True,
        metadata_changes_only=True,
        metadata_query=None,
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
    selected_connectors = connectors_commands.get_selected_connectors_with_modified_files(
        selected_names=(),
        selected_support_levels=(),
        selected_languages=(),
        modified=False,
        metadata_changes_only=True,
        metadata_query=None,
        modified_files=modified_files,
    )

    assert len(selected_connectors) == 1
    assert selected_connectors[0].technical_name == second_modified_connector.technical_name
    assert selected_connectors[0].modified_files == {
        second_modified_connector.code_directory / METADATA_FILE_NAME,
        second_modified_connector.code_directory / "setup.py",
    }


def test_get_selected_connectors_with_metadata_query():
    connector = pick_a_random_connector()
    metadata_query = f"data.dockerRepository == '{connector.metadata['dockerRepository']}'"
    selected_connectors = connectors_commands.get_selected_connectors_with_modified_files(
        selected_names=(),
        selected_support_levels=(),
        selected_languages=(),
        modified=False,
        metadata_changes_only=False,
        metadata_query=metadata_query,
        modified_files=set(),
    )

    assert len(selected_connectors) == 1
    assert isinstance(selected_connectors[0], ConnectorWithModifiedFiles)
    assert selected_connectors[0].technical_name == connector.technical_name
    assert not selected_connectors[0].modified_files


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
        "docker_hub_username": "foo",
        "docker_hub_password": "bar",
    }


@pytest.mark.parametrize(
    "command, command_args",
    [
        (connectors_test_command.test, []),
        (
            connectors_publish_command.publish,
            [
                "--spec-cache-gcs-credentials",
                "test",
                "--spec-cache-bucket-name",
                "test",
                "--metadata-service-gcs-credentials",
                "test",
                "--metadata-service-bucket-name",
                "test",
            ],
        ),
        (connectors_build_command.build, []),
    ],
)
@pytest.mark.anyio
async def test_commands_do_not_override_connector_selection(
    mocker, runner: CliRunner, click_context_obj: dict, command: Callable, command_args: list
):
    """
    This test is here to make sure that the commands do not override the connector selection
    This is important because we want to control the connector selection in a single place.
    """

    selected_connector = mocker.MagicMock()
    click_context_obj["selected_connectors_with_modified_files"] = [selected_connector]

    mocker.patch.object(click, "confirm")
    mock_connector_context = mocker.MagicMock()
    mocker.patch.object(connectors_test_command, "ConnectorContext", mock_connector_context)
    mocker.patch.object(connectors_build_command, "ConnectorContext", mock_connector_context)
    mocker.patch.object(connectors_publish_command, "PublishConnectorContext", mock_connector_context)
    await runner.invoke(command, command_args, catch_exceptions=True, obj=click_context_obj)
    assert mock_connector_context.call_count == 1
    # If the connector selection is overriden the context won't be instantiated with the selected connector mock instance
    assert mock_connector_context.call_args_list[0].kwargs["connector"] == selected_connector


@pytest.mark.parametrize(
    "use_remote_secrets_user_input, gsm_env_var_set, expected_use_remote_secrets, expect_click_usage_error",
    [
        (None, True, True, False),
        (None, False, False, False),
        (True, False, None, True),
        (True, True, True, False),
        (False, True, False, False),
        (False, False, False, False),
    ],
)
def test_should_use_remote_secrets(
    mocker, use_remote_secrets_user_input, gsm_env_var_set, expected_use_remote_secrets, expect_click_usage_error
):
    mocker.patch.object(connectors_commands.os, "getenv", return_value="test" if gsm_env_var_set else None)
    if expect_click_usage_error:
        with pytest.raises(click.UsageError):
            connectors_commands.should_use_remote_secrets(use_remote_secrets_user_input)
    else:
        final_use_remote_secrets = connectors_commands.should_use_remote_secrets(use_remote_secrets_user_input)
        assert final_use_remote_secrets == expected_use_remote_secrets
