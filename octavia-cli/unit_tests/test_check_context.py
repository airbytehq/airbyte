#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import os
import shutil
import tempfile
from pathlib import Path

import airbyte_api_client
import pytest
from airbyte_api_client.model.workspace_id_request_body import WorkspaceIdRequestBody
from octavia_cli import check_context
from urllib3.exceptions import MaxRetryError


@pytest.fixture
def mock_api_client(mocker):
    return mocker.Mock()


def test_api_check_health_available(mock_api_client, mocker):
    mocker.patch.object(check_context, "health_api")
    mock_api_response = mocker.Mock(available=True)
    check_context.health_api.HealthApi.return_value.get_health_check.return_value = mock_api_response

    assert check_context.check_api_health(mock_api_client) is None
    check_context.health_api.HealthApi.assert_called_with(mock_api_client)
    api_instance = check_context.health_api.HealthApi.return_value
    api_instance.get_health_check.assert_called()


def test_api_check_health_unavailable(mock_api_client, mocker):
    mocker.patch.object(check_context, "health_api")
    mock_api_response = mocker.Mock(available=False)
    check_context.health_api.HealthApi.return_value.get_health_check.return_value = mock_api_response
    with pytest.raises(check_context.UnhealthyApiError):
        check_context.check_api_health(mock_api_client)


def test_api_check_health_unreachable_api_exception(mock_api_client, mocker):
    mocker.patch.object(check_context, "health_api")
    check_context.health_api.HealthApi.return_value.get_health_check.side_effect = airbyte_api_client.ApiException()
    with pytest.raises(check_context.UnreachableAirbyteInstanceError):
        check_context.check_api_health(mock_api_client)


def test_api_check_health_unreachable_max_retry_error(mock_api_client, mocker):
    mocker.patch.object(check_context, "health_api")
    check_context.health_api.HealthApi.return_value.get_health_check.side_effect = MaxRetryError("foo", "bar")
    with pytest.raises(check_context.UnreachableAirbyteInstanceError):
        check_context.check_api_health(mock_api_client)


def test_check_workspace_exists(mock_api_client, mocker):
    mocker.patch.object(check_context, "workspace_api")
    mock_api_instance = mocker.Mock()
    check_context.workspace_api.WorkspaceApi.return_value = mock_api_instance
    assert check_context.check_workspace_exists(mock_api_client, "foo") is None
    check_context.workspace_api.WorkspaceApi.assert_called_with(mock_api_client)
    mock_api_instance.get_workspace.assert_called_with(WorkspaceIdRequestBody("foo"), _check_return_type=False)


def test_check_workspace_exists_error(mock_api_client, mocker):
    mocker.patch.object(check_context, "workspace_api")
    check_context.workspace_api.WorkspaceApi.return_value.get_workspace.side_effect = airbyte_api_client.ApiException()
    with pytest.raises(check_context.WorkspaceIdError):
        check_context.check_workspace_exists(mock_api_client, "foo")


@pytest.fixture
def project_directories():
    dirpath = tempfile.mkdtemp()
    yield str(Path(dirpath).parent.absolute()), [os.path.basename(dirpath)]
    shutil.rmtree(dirpath)


def test_check_is_initialized(mocker, project_directories):
    project_directory, sub_directories = project_directories
    mocker.patch.object(check_context, "REQUIRED_PROJECT_DIRECTORIES", sub_directories)
    assert check_context.check_is_initialized(project_directory)


def test_check_not_initialized():
    assert not check_context.check_is_initialized(".")
