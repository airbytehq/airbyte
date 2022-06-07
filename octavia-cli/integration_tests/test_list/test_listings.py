#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import pytest
from octavia_cli.list.listings import Connections, DestinationConnectorsDefinitions, Destinations, SourceConnectorsDefinitions, Sources

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("ConnectorsDefinitionListing", [SourceConnectorsDefinitions, DestinationConnectorsDefinitions])
def test_list_connectors(api_client, ConnectorsDefinitionListing):
    connector_definitions = ConnectorsDefinitionListing(api_client)
    listing = connector_definitions.get_listing()
    assert len(listing) > 0
    assert len(listing[0]) == len(ConnectorsDefinitionListing.fields_to_display)
    assert str(listing)


@pytest.mark.parametrize("WorkspaceListing", [Sources, Destinations, Connections])
def test_list_workspace_resource(api_client, source, destination, connection, workspace_id, WorkspaceListing):
    assert source.was_created
    assert destination.was_created
    assert connection.was_created
    connector_definitions = WorkspaceListing(api_client, workspace_id)
    listing = connector_definitions.get_listing()
    assert len(listing) >= 1
    assert len(listing[0]) == len(WorkspaceListing.fields_to_display)
    assert str(listing)
