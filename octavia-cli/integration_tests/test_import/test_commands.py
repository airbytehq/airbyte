#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import glob
import os
import shutil
from distutils.dir_util import copy_tree
from pathlib import Path
from unittest import mock

import pytest
from airbyte_api_client.api import connection_api
from airbyte_api_client.model.connection_id_request_body import ConnectionIdRequestBody
from click.testing import CliRunner
from octavia_cli._import.commands import all as octavia_import_all
from octavia_cli._import.commands import connection as octavia_import_connection
from octavia_cli._import.commands import destination as octavia_import_destination
from octavia_cli._import.commands import source as octavia_import_source
from octavia_cli.apply.commands import apply as octavia_apply
from octavia_cli.apply.resources import ResourceState
from octavia_cli.apply.resources import factory as resource_factory

pytestmark = pytest.mark.integration
click_runner = CliRunner()


@pytest.fixture(scope="module")
def context_object(api_client, workspace_id):
    return {"TELEMETRY_CLIENT": mock.MagicMock(), "PROJECT_IS_INITIALIZED": True, "API_CLIENT": api_client, "WORKSPACE_ID": workspace_id}


@pytest.fixture(scope="module")
def initialized_project_directory(context_object):
    """This fixture initializes a temporary local directory with configuration.yaml files copied from ./octavia_project_to_migrate
    It runs octavia apply on these configurations and then removes the local yaml files.
    At the end of the run of this function we have remote resources an our Airbyte instance but they are not managed by octavia due to the file deletion.
    The fixture returns source, destination and connection previously instantiated resources to make sure the import command ran in the following tests imports configuration at the right location.
    """
    cwd = os.getcwd()
    dir_path = f"{os.path.dirname(__file__)}/octavia_test_project"
    copy_tree(f"{os.path.dirname(__file__)}/octavia_project_to_migrate", dir_path)
    os.chdir(dir_path)

    result = click_runner.invoke(octavia_apply, obj=context_object)
    assert result.exit_code == 0
    for configuration_file in glob.glob("./**/configuration.yaml", recursive=True):
        resource = resource_factory(context_object["API_CLIENT"], context_object["WORKSPACE_ID"], configuration_file)
        if resource.resource_type == "source":
            source_id, source_expected_configuration_path, source_expected_state_path = (
                resource.resource_id,
                resource.configuration_path,
                resource.state.path,
            )
        if resource.resource_type == "destination":
            destination_id, destination_expected_configuration_path, destination_expected_state_path = (
                resource.resource_id,
                resource.configuration_path,
                ResourceState._get_path_from_configuration_and_workspace_id(resource.configuration_path, context_object["WORKSPACE_ID"]),
            )
        if resource.resource_type == "connection":
            connection_id, connection_configuration_path, connection_expected_state_path = (
                resource.resource_id,
                resource.configuration_path,
                ResourceState._get_path_from_configuration_and_workspace_id(resource.configuration_path, context_object["WORKSPACE_ID"]),
            )
        os.remove(configuration_file)
        os.remove(resource.state.path)
    yield (source_id, source_expected_configuration_path, source_expected_state_path), (
        destination_id,
        destination_expected_configuration_path,
        destination_expected_state_path,
    ), (connection_id, connection_configuration_path, connection_expected_state_path)
    os.chdir(cwd)
    shutil.rmtree(dir_path)


@pytest.fixture(scope="module")
def expected_source(initialized_project_directory):
    yield initialized_project_directory[0]


@pytest.fixture(scope="module")
def expected_destination(initialized_project_directory):
    yield initialized_project_directory[1]


@pytest.fixture(scope="module")
def expected_connection(initialized_project_directory, context_object, expected_source, expected_destination):
    connection_id, connection_configuration_path, connection_expected_state_path = initialized_project_directory[2]
    yield connection_id, connection_configuration_path, connection_expected_state_path
    # To delete the connection we have to create a ConnectionApi instance because WebBackendApi instance does not have delete endpoint
    connection = resource_factory(context_object["API_CLIENT"], context_object["WORKSPACE_ID"], connection_configuration_path)
    connection_api_instance = connection_api.ConnectionApi(context_object["API_CLIENT"])
    connection_api_instance.delete_connection(
        ConnectionIdRequestBody(
            connection_id=connection.resource_id,
        )
    )
    # Delete source and destination after connection to not make the connection deprecated
    source = resource_factory(context_object["API_CLIENT"], context_object["WORKSPACE_ID"], expected_source[1])
    source.api_instance.delete_source(source.get_payload)
    destination = resource_factory(context_object["API_CLIENT"], context_object["WORKSPACE_ID"], expected_destination[1])
    destination.api_instance.delete_destination(destination.get_payload)


def test_import_source(expected_source, context_object):
    source_id, expected_configuration_path, expected_state_path = expected_source
    result = click_runner.invoke(octavia_import_source, source_id, obj=context_object)
    assert result.exit_code == 0
    assert Path(expected_configuration_path).is_file() and Path(expected_state_path).is_file()
    source = resource_factory(context_object["API_CLIENT"], context_object["WORKSPACE_ID"], expected_configuration_path)
    assert source.was_created  # Check if the remote resource is considered as managed by octavia and exists remotely
    assert source.get_diff_with_remote_resource() == ""
    assert source.state.path in str(expected_state_path)


def test_import_destination(expected_destination, context_object):
    destination_id, expected_configuration_path, expected_state_path = expected_destination
    result = click_runner.invoke(octavia_import_destination, destination_id, obj=context_object)
    assert result.exit_code == 0
    assert Path(expected_configuration_path).is_file() and Path(expected_state_path).is_file()
    destination = resource_factory(context_object["API_CLIENT"], context_object["WORKSPACE_ID"], expected_configuration_path)
    assert destination.was_created  # Check if the remote resource is considered as managed by octavia and exists remotely
    assert destination.get_diff_with_remote_resource() == ""
    assert destination.state.path in str(expected_state_path)
    assert destination.configuration["password"] == "**********"


def test_import_connection(expected_connection, context_object):
    connection_id, expected_configuration_path, expected_state_path = expected_connection
    result = click_runner.invoke(octavia_import_connection, connection_id, obj=context_object)
    assert result.exit_code == 0
    assert Path(expected_configuration_path).is_file() and Path(expected_state_path).is_file()
    connection = resource_factory(context_object["API_CLIENT"], context_object["WORKSPACE_ID"], expected_configuration_path)
    assert connection.was_created  # Check if the remote resource is considered as managed by octavia and exists remotely
    assert connection.get_diff_with_remote_resource() == ""
    assert connection.state.path in str(expected_state_path)


def test_import_all(expected_source, expected_destination, expected_connection, context_object):
    _, source_expected_configuration_path, source_expected_state_path = expected_source
    _, destination_expected_configuration_path, destination_expected_state_path = expected_destination
    _, connection_expected_configuration_path, connection_expected_state_path = expected_connection
    paths_to_first_delete_and_then_check_existence = [
        source_expected_configuration_path,
        source_expected_state_path,
        destination_expected_configuration_path,
        destination_expected_state_path,
        connection_expected_configuration_path,
        connection_expected_state_path,
    ]
    for path in paths_to_first_delete_and_then_check_existence:
        os.remove(path)
    result = click_runner.invoke(octavia_import_all, obj=context_object)
    assert result.exit_code == 0
    for path in paths_to_first_delete_and_then_check_existence:
        assert os.path.exists(path)
