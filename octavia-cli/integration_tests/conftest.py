#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import os

import pytest
import yaml
from airbyte_api_client.api import connection_api
from airbyte_api_client.model.connection_id_request_body import ConnectionIdRequestBody
from octavia_cli.apply.resources import Connection, Destination, Source
from octavia_cli.entrypoint import get_api_client, get_workspace_id
from octavia_cli.init.commands import DIRECTORIES_TO_CREATE as OCTAVIA_PROJECT_DIRECTORIES


def silent_remove(path):
    try:
        os.remove(path)
        return True
    except FileNotFoundError:
        return False


@pytest.fixture
def octavia_tmp_project_directory(tmpdir):
    for directory in OCTAVIA_PROJECT_DIRECTORIES:
        tmpdir.mkdir(directory)
    return tmpdir


@pytest.fixture(scope="session")
def octavia_test_project_directory():
    return f"{os.path.dirname(__file__)}/configurations"


@pytest.fixture(scope="session")
def api_client():
    return get_api_client("http://localhost:8000", "airbyte", "password", "octavia-cli/integration-tests", None)


@pytest.fixture(scope="session")
def workspace_id(api_client):
    return get_workspace_id(api_client, None)


def open_yaml_configuration(path: str):
    with open(path, "r") as f:
        local_configuration = yaml.safe_load(f)
    return local_configuration, path


@pytest.fixture(scope="session")
def source_configuration_and_path(octavia_test_project_directory):
    path = f"{octavia_test_project_directory}/sources/poke/configuration.yaml"
    return open_yaml_configuration(path)


@pytest.fixture(scope="session")
def source_state_path(octavia_test_project_directory, workspace_id):
    state_path = f"{octavia_test_project_directory}/sources/poke/state_{workspace_id}.yaml"
    silent_remove(state_path)
    yield state_path
    silent_remove(state_path)


@pytest.fixture(scope="session")
def source(api_client, workspace_id, source_configuration_and_path, source_state_path):
    configuration, path = source_configuration_and_path
    source = Source(api_client, workspace_id, configuration, path)
    yield source
    source.api_instance.delete_source(source.get_payload)


@pytest.fixture(scope="session")
def destination_configuration_and_path(octavia_test_project_directory):
    path = f"{octavia_test_project_directory}/destinations/postgres/configuration.yaml"
    return open_yaml_configuration(path)


@pytest.fixture(scope="session")
def destination_state_path(octavia_test_project_directory, workspace_id):
    state_path = f"{octavia_test_project_directory}/destinations/postgres/state_{workspace_id}.yaml"
    silent_remove(state_path)
    yield state_path
    silent_remove(state_path)


@pytest.fixture(scope="session")
def destination(api_client, workspace_id, destination_configuration_and_path, destination_state_path):
    configuration, path = destination_configuration_and_path
    destination = Destination(api_client, workspace_id, configuration, path)
    yield destination
    destination.api_instance.delete_destination(destination.get_payload)


@pytest.fixture(scope="session")
def connection_configuration_and_path(octavia_test_project_directory):
    path = f"{octavia_test_project_directory}/connections/poke_to_pg/configuration.yaml"
    with open(path, "r") as f:
        local_configuration = yaml.safe_load(f)
    return local_configuration, path


@pytest.fixture(scope="session")
def connection_state_path(octavia_test_project_directory, workspace_id):
    state_path = f"{octavia_test_project_directory}/connections/poke_to_pg/state_{workspace_id}.yaml"
    silent_remove(state_path)
    yield state_path
    silent_remove(state_path)


@pytest.fixture(scope="session")
def connection_with_normalization_state_path(octavia_test_project_directory, workspace_id):
    state_path = f"{octavia_test_project_directory}/connections/poke_to_pg_normalization/state_{workspace_id}.yaml"
    silent_remove(state_path)
    yield state_path
    silent_remove(state_path)


def updated_connection_configuration_and_path(octavia_test_project_directory, source, destination, with_normalization=False):
    if with_normalization:
        path = f"{octavia_test_project_directory}/connections/poke_to_pg_normalization/configuration.yaml"
        edited_path = f"{octavia_test_project_directory}/connections/poke_to_pg_normalization/updated_configuration.yaml"
    else:
        path = f"{octavia_test_project_directory}/connections/poke_to_pg/configuration.yaml"
        edited_path = f"{octavia_test_project_directory}/connections/poke_to_pg/updated_configuration.yaml"
    with open(path, "r") as dumb_local_configuration_file:
        local_configuration = yaml.safe_load(dumb_local_configuration_file)
    local_configuration["source_configuration_path"] = source.configuration_path
    local_configuration["destination_configuration_path"] = destination.configuration_path
    with open(edited_path, "w") as updated_configuration_file:
        yaml.dump(local_configuration, updated_configuration_file)
    return local_configuration, edited_path


@pytest.fixture(scope="session")
def connection(api_client, workspace_id, octavia_test_project_directory, source, destination, connection_state_path):
    configuration, configuration_path = updated_connection_configuration_and_path(octavia_test_project_directory, source, destination)
    connection = Connection(api_client, workspace_id, configuration, configuration_path)
    yield connection
    connection_api.ConnectionApi(api_client).delete_connection(ConnectionIdRequestBody(connection.resource_id))
    silent_remove(configuration_path)


@pytest.fixture(scope="session")
def connection_with_normalization(
    api_client, workspace_id, octavia_test_project_directory, source, destination, connection_with_normalization_state_path
):
    configuration, configuration_path = updated_connection_configuration_and_path(
        octavia_test_project_directory, source, destination, with_normalization=True
    )
    connection = Connection(api_client, workspace_id, configuration, configuration_path)
    yield connection
    connection_api.ConnectionApi(api_client).delete_connection(ConnectionIdRequestBody(connection.resource_id))
    silent_remove(configuration_path)
