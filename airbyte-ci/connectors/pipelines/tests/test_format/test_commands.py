#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import shutil

import pytest
from asyncclick.testing import CliRunner
from pipelines.airbyte_ci.format import commands
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext

pytestmark = [
    pytest.mark.anyio,
]

PATH_TO_NON_FORMATTED_CODE = "airbyte-ci/connectors/pipelines/tests/test_format/non_formatted_code"
PATH_TO_FORMATTED_CODE = "airbyte-ci/connectors/pipelines/tests/test_format/formatted_code"


@pytest.fixture
def tmp_dir_with_non_formatted_code(tmp_path):
    """
    This fixture creates a directory with non formatted code and a license file in the tmp_path.
    It copies the content of non_formatted_code into the tmp_path.
    The non_formatted_code directory has non formatted java, python, json, and yaml files missing license headers.
    """
    shutil.copytree(PATH_TO_NON_FORMATTED_CODE, tmp_path / "non_formatted_code")
    return str(tmp_path / "non_formatted_code")


@pytest.fixture
def tmp_dir_with_formatted_code(tmp_path):
    """
    This fixture creates a directory with correctly formatted code and a license file in the tmp_path.
    It copies the content of formatted_code into the tmp_path.
    The formatted_code has correctly formatted java, python, json, and yaml files with license headers.
    """
    shutil.copytree(PATH_TO_FORMATTED_CODE, tmp_path / "formatted_code")
    return str(tmp_path / "formatted_code")


@pytest.fixture
def now_formatted_directory(dagger_client, tmp_dir_with_non_formatted_code):
    return dagger_client.host().directory(tmp_dir_with_non_formatted_code).with_timestamps(0)


@pytest.fixture
def already_formatted_directory(dagger_client, tmp_dir_with_formatted_code):
    return dagger_client.host().directory(tmp_dir_with_formatted_code).with_timestamps(0)


@pytest.fixture
def directory_with_expected_formatted_code(dagger_client):
    expected_formatted_code_path = PATH_TO_FORMATTED_CODE
    return dagger_client.host().directory(expected_formatted_code_path).with_timestamps(0)


@pytest.mark.slow
@pytest.mark.parametrize("subcommand", ["check", "fix"])
async def test_check_and_fix_all_on_non_formatted_code(
    mocker, subcommand, dagger_client, tmp_dir_with_non_formatted_code, now_formatted_directory, directory_with_expected_formatted_code
):
    """
    Test that when given non formatted files the 'check' and 'fix' all command exit with status 1.
    We also check that 'fix' correctly exports back the formatted code and that it matches what we expect.
    """
    mocker.patch.object(ClickPipelineContext, "get_dagger_client", mocker.AsyncMock(return_value=dagger_client))
    mocker.patch.object(commands.FormatCommand, "LOCAL_REPO_PATH", tmp_dir_with_non_formatted_code)
    runner = CliRunner()
    result = await runner.invoke(commands.format_code, [subcommand, "all"], catch_exceptions=False)
    if subcommand == "fix":
        assert await now_formatted_directory.diff(directory_with_expected_formatted_code).entries() == []
    assert result.exit_code == 1


@pytest.mark.slow
@pytest.mark.parametrize("subcommand", ["check", "fix"])
async def test_check_and_fix_all_on_formatted_code(
    mocker, subcommand, dagger_client, tmp_dir_with_formatted_code, already_formatted_directory, directory_with_expected_formatted_code
):
    """
    Test that when given formatted files the 'check' and 'fix' all command exit with status 0.
    We also check that 'fix' does not exports back any file change to the host.
    """
    mocker.patch.object(ClickPipelineContext, "get_dagger_client", mocker.AsyncMock(return_value=dagger_client))
    mocker.patch.object(commands.FormatCommand, "LOCAL_REPO_PATH", tmp_dir_with_formatted_code)
    runner = CliRunner()
    result = await runner.invoke(commands.format_code, [subcommand, "all"], catch_exceptions=False)
    if subcommand == "fix":
        assert await already_formatted_directory.diff(directory_with_expected_formatted_code).entries() == []
    assert result.exit_code == 0
