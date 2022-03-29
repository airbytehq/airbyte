#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import os

import pytest
import yaml
from octavia_cli.apply.resources import Connection, Destination, Source
from octavia_cli.entrypoint import get_api_client, get_workspace_id

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def api_client():
    return get_api_client("http://localhost:8000")


@pytest.fixture(scope="module")
def workspace_id(api_client):
    return get_workspace_id(api_client, None)


@pytest.fixture(scope="module")
def source_configuration_and_path():
    path = f"{os.path.dirname(__file__)}/configurations/sources/poke/configuration.yaml"
    with open(path, "r") as f:
        local_configuration = yaml.safe_load(f)
    return local_configuration, path


def silent_remove(path):
    try:
        os.remove(path)
        return True
    except FileNotFoundError:
        return False


@pytest.fixture(scope="module")
def source_state_path():
    state_path = f"{os.path.dirname(__file__)}/configurations/sources/poke/state.yaml"
    silent_remove(state_path)
    yield state_path
    silent_remove(state_path)


@pytest.fixture(scope="module")
def source(api_client, workspace_id, source_configuration_and_path, source_state_path):
    configuration, path = source_configuration_and_path
    source = Source(api_client, workspace_id, configuration, path)
    yield source
    source.api_instance.delete_source(source.resource_id_request_body)


def test_source_lifecycle(source):
    assert not source.was_created
    source.create()
    source.state = source._get_state_from_file()
    assert source.was_created
    assert not source.get_diff_with_remote_resource()
    source.local_configuration["configuration"]["pokemon_name"] = "snorlex"
    assert 'changed from "ditto" to "snorlex"' in source.get_diff_with_remote_resource()
    source.update()
    assert not source.get_diff_with_remote_resource()
    assert source.catalog["streams"][0]["config"]["aliasName"] == "pokemon"


@pytest.fixture(scope="module")
def destination_configuration_and_path():
    path = f"{os.path.dirname(__file__)}/configurations/destinations/postgres/configuration.yaml"
    with open(path, "r") as f:
        local_configuration = yaml.safe_load(f)
    return local_configuration, path


@pytest.fixture(scope="module")
def destination_state_path():
    state_path = f"{os.path.dirname(__file__)}/configurations/destinations/postgres/state.yaml"
    silent_remove(state_path)
    yield state_path
    silent_remove(state_path)


@pytest.fixture(scope="module")
def destination(api_client, workspace_id, destination_configuration_and_path, destination_state_path):
    configuration, path = destination_configuration_and_path
    destination = Destination(api_client, workspace_id, configuration, path)
    yield destination
    destination.api_instance.delete_destination(destination.resource_id_request_body)


def test_destination_lifecycle(destination):
    assert not destination.was_created
    destination.create()
    destination.state = destination._get_state_from_file()
    assert destination.was_created
    assert not destination.get_diff_with_remote_resource()
    destination.local_configuration["configuration"]["host"] = "foo"
    assert 'changed from "localhost" to "foo"' in destination.get_diff_with_remote_resource()
    destination.update()
    assert not destination.get_diff_with_remote_resource()


@pytest.fixture(scope="module")
def connection_configuration_and_path():
    path = f"{os.path.dirname(__file__)}/configurations/connections/poke_to_pg/configuration.yaml"
    with open(path, "r") as f:
        local_configuration = yaml.safe_load(f)
    return local_configuration, path


@pytest.fixture(scope="module")
def connection_state_path():
    state_path = f"{os.path.dirname(__file__)}/configurations/connections/poke_to_pg/state.yaml"
    silent_remove(state_path)
    yield state_path
    silent_remove(state_path)


def updated_connection_configuration_and_path(source, destination):
    path = f"{os.path.dirname(__file__)}/configurations/connections/poke_to_pg/configuration.yaml"
    edited_path = f"{os.path.dirname(__file__)}/configurations/connections/poke_to_pg/updated_configuration.yaml"
    with open(path, "r") as dumb_local_configuration_file:
        local_configuration = yaml.safe_load(dumb_local_configuration_file)
    local_configuration["source_id"] = source.resource_id
    local_configuration["destination_id"] = destination.resource_id
    local_configuration["configuration"]["sourceId"] = source.resource_id
    local_configuration["configuration"]["destinationId"] = destination.resource_id
    with open(edited_path, "w") as updated_configuration_file:
        yaml.dump(local_configuration, updated_configuration_file)
    return local_configuration, edited_path


def test_connection_lifecycle(source, destination, api_client, workspace_id, connection_state_path):
    assert source.was_created
    assert destination.was_created
    configuration, configuration_path = updated_connection_configuration_and_path(source, destination)
    connection = Connection(api_client, workspace_id, configuration, configuration_path)
    assert not connection.was_created
    connection.create()
    connection.state = connection._get_state_from_file()
    assert connection.was_created
    assert not connection.get_diff_with_remote_resource()
    connection.local_configuration["configuration"]["status"] = "inactive"
    assert 'changed from "active" to "inactive"' in connection.get_diff_with_remote_resource()
    connection.update()
    assert not connection.get_diff_with_remote_resource()
    connection.api_instance.delete_connection(connection.resource_id_request_body)
    silent_remove(configuration_path)
