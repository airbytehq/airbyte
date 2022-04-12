#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import pytest

pytestmark = pytest.mark.integration


def test_source_lifecycle(source):
    assert not source.was_created
    source.create()
    source.state = source._get_state_from_file()
    assert source.was_created
    assert not source.get_diff_with_remote_resource()
    source.local_configuration["configuration"]["pokemon_name"] = "snorlax"
    assert 'changed from "ditto" to "snorlax"' in source.get_diff_with_remote_resource()
    source.update()
    assert not source.get_diff_with_remote_resource()
    assert source.catalog["streams"][0]["config"]["aliasName"] == "pokemon"


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


def test_connection_lifecycle(source, destination, connection):
    assert source.was_created
    assert destination.was_created
    assert not connection.was_created
    connection.create()
    connection.state = connection._get_state_from_file()
    assert connection.was_created
    assert not connection.get_diff_with_remote_resource()
    connection.local_configuration["configuration"]["status"] = "inactive"
    assert 'changed from "active" to "inactive"' in connection.get_diff_with_remote_resource()
    connection.update()
    assert not connection.get_diff_with_remote_resource()
