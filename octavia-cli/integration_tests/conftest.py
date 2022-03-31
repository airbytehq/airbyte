#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import os

import pytest
import yaml
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
    return get_api_client("http://localhost:8000")


@pytest.fixture(scope="session")
def workspace_id(api_client):
    return get_workspace_id(api_client, None)


@pytest.fixture(scope="session")
def source_configuration_and_path(octavia_test_project_directory):
    path = f"{octavia_test_project_directory}/sources/poke/configuration.yaml"
    with open(path, "r") as f:
        local_configuration = yaml.safe_load(f)
    return local_configuration, path


@pytest.fixture(scope="session")
def source_state_path(octavia_test_project_directory):
    state_path = f"{octavia_test_project_directory}/sources/poke/state.yaml"
    silent_remove(state_path)
    yield state_path
    silent_remove(state_path)


@pytest.fixture(scope="session")
def source(api_client, workspace_id, source_configuration_and_path, source_state_path):
    configuration, path = source_configuration_and_path
    source = Source(api_client, workspace_id, configuration, path)
    yield source
    source.api_instance.delete_source(source.resource_id_request_body)


@pytest.fixture(scope="session")
def destination_configuration_and_path(octavia_test_project_directory):
    path = f"{octavia_test_project_directory}/destinations/postgres/configuration.yaml"
    with open(path, "r") as f:
        local_configuration = yaml.safe_load(f)
    return local_configuration, path


@pytest.fixture(scope="session")
def destination_state_path(octavia_test_project_directory):
    state_path = f"{octavia_test_project_directory}/destinations/postgres/state.yaml"
    silent_remove(state_path)
    yield state_path
    silent_remove(state_path)


@pytest.fixture(scope="session")
def destination(api_client, workspace_id, destination_configuration_and_path, destination_state_path):
    configuration, path = destination_configuration_and_path
    destination = Destination(api_client, workspace_id, configuration, path)
    yield destination
    destination.api_instance.delete_destination(destination.resource_id_request_body)


@pytest.fixture(scope="session")
def connection_configuration_and_path(octavia_test_project_directory):
    path = f"{octavia_test_project_directory}/connections/poke_to_pg/configuration.yaml"
    with open(path, "r") as f:
        local_configuration = yaml.safe_load(f)
    return local_configuration, path


@pytest.fixture(scope="session")
def connection_state_path(octavia_test_project_directory):
    state_path = f"{octavia_test_project_directory}/connections/poke_to_pg/state.yaml"
    silent_remove(state_path)
    yield state_path
    silent_remove(state_path)


def updated_connection_configuration_and_path(octavia_test_project_directory, source, destination):
    path = f"{octavia_test_project_directory}/connections/poke_to_pg/configuration.yaml"
    edited_path = f"{octavia_test_project_directory}/connections/poke_to_pg/updated_configuration.yaml"
    with open(path, "r") as dumb_local_configuration_file:
        local_configuration = yaml.safe_load(dumb_local_configuration_file)
    local_configuration["source_id"] = source.resource_id
    local_configuration["destination_id"] = destination.resource_id
    local_configuration["configuration"]["sourceId"] = source.resource_id
    local_configuration["configuration"]["destinationId"] = destination.resource_id
    with open(edited_path, "w") as updated_configuration_file:
        yaml.dump(local_configuration, updated_configuration_file)
    return local_configuration, edited_path


@pytest.fixture(scope="session")
def connection(api_client, workspace_id, octavia_test_project_directory, source, destination):
    configuration, configuration_path = updated_connection_configuration_and_path(octavia_test_project_directory, source, destination)
    connection = Connection(api_client, workspace_id, configuration, configuration_path)
    yield connection
    connection.api_instance.delete_connection(connection.resource_id_request_body)
    silent_remove(configuration_path)
