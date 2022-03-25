#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import os

import pytest
import yaml
from octavia_cli.apply.resources import Destination, Source
from octavia_cli.entrypoint import get_api_client, get_workspace_id

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def api_client():
    return get_api_client("http://localhost:8000")


@pytest.fixture
def workspace_id(api_client):
    return get_workspace_id(api_client, None)


class TestSource:
    @pytest.fixture
    def source_configuration_path(
        self,
    ):
        return f"{os.path.dirname(__file__)}/configurations/sources/poke/configuration.yaml"

    @pytest.fixture
    def source_state_path(
        self,
    ):
        state_path = f"{os.path.dirname(__file__)}/configurations/sources/poke/state.yaml"
        try:
            os.remove(state_path)
        except FileNotFoundError:
            pass
        yield state_path
        os.remove(state_path)

    @pytest.fixture
    def source(self, api_client, workspace_id, source_configuration_path, source_state_path):
        with open(source_configuration_path, "r") as f:
            local_configuration = yaml.safe_load(f)
        source = Source(api_client, workspace_id, local_configuration, source_configuration_path)
        yield source
        source.api_instance.delete_source(source.resource_id_request_body)

    def test_manage_lifecycle(self, source):
        assert not source.was_created
        source.create()
        assert source.was_created
        assert not source.get_diff_with_remote_resource()
        source.local_configuration["configuration"]["pokemon_name"] = "snorlex"
        assert 'changed from "ditto" to "snorlex"' in source.get_diff_with_remote_resource()
        source.state = source._get_state_from_file()
        source.update()
        assert not source.get_diff_with_remote_resource()
        assert source.catalog["streams"][0]["config"]["aliasName"] == "pokemon"


class TestDestination:
    @pytest.fixture
    def destination_configuration_path(self):
        return f"{os.path.dirname(__file__)}/configurations/destinations/postgres/configuration.yaml"

    @pytest.fixture
    def destination_state_path(self):
        state_path = f"{os.path.dirname(__file__)}/configurations/destinations/postgres/state.yaml"
        try:
            os.remove(state_path)
        except FileNotFoundError:
            pass
        yield state_path
        os.remove(state_path)

    @pytest.fixture
    def destination(self, api_client, workspace_id, destination_configuration_path, destination_state_path):
        with open(destination_configuration_path, "r") as f:
            local_configuration = yaml.safe_load(f)
        destination = Destination(api_client, workspace_id, local_configuration, destination_configuration_path)
        yield destination
        destination.api_instance.delete_destination(destination.resource_id_request_body)

    def test_manage_lifecycle(self, destination):
        assert not destination.was_created
        destination.create()
        assert destination.was_created
        assert not destination.get_diff_with_remote_resource()
        destination.local_configuration["configuration"]["host"] = "foo"
        assert 'changed from "localhost" to "foo"' in destination.get_diff_with_remote_resource()
        destination.state = destination._get_state_from_file()
        destination.update()
        assert not destination.get_diff_with_remote_resource()
