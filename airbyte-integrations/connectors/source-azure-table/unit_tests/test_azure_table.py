#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest


def test_get_table_service_client_return(mocker, reader):
    """
    Test that the get_table_service_client method returns the expected Table Service Client.
    """
    mock_client = "dummy-client"
    mocker.patch(
        "source_azure_table.azure_table.TableServiceClient.from_connection_string",
        return_value=mock_client,
    )

    client = reader.get_table_service_client()
    assert client == mock_client


def test_get_table_service_client_handles_exception(mocker, reader):
    """
    Test that get_table_service_client method handles exceptions correctly.
    """
    mocker.patch(
        "source_azure_table.azure_table.TableServiceClient.from_connection_string",
        side_effect=Exception("Connection error")
    )

    with pytest.raises(Exception) as exc_info:
        reader.get_table_service_client()
    
    assert "Connection error" in str(exc_info.value)


def test_get_table_client_return(mocker, reader):
    """
    Test that the get_table_client method returns the expected Table Client.
    """
    mock_client = "dummy-client"
    mocker.patch(
        "source_azure_table.azure_table.TableClient.from_connection_string",
        return_value=mock_client,
    )

    table = reader.get_table_client("dummy-table")
    assert table == mock_client


def test_get_table_client_handles_exception(mocker, reader):
    """
    Test that get_table_client method handles exceptions correctly.
    """

    # The method throws its own exception for empty table names
    with pytest.raises(Exception) as exc_info:
        reader.get_table_client("")
    assert "table name is not valid." in str(exc_info.value)

    mocker.patch(
        "source_azure_table.azure_table.TableClient.from_connection_string",
        side_effect=Exception("Connection error")
    )

    with pytest.raises(Exception) as exc_info:
        reader.get_table_client("valid_table_name")
    assert "Connection error" in str(exc_info.value)


def test_get_tables_return(mocker, reader, tables):
    """
    Test that the get_tables method returns the expected tables.
    """
    mock_client = mocker.MagicMock()
    mock_client.list_tables.return_value = tables.__iter__()
    mocker.patch(
        "azure.data.tables.TableServiceClient.from_connection_string",
        return_value=mock_client
    )

    result = reader.get_tables()
    result_table_names = [table.name for table in result]

    expected_table_names = ["AzureTable1", "AzureTable2"]
    assert result_table_names == expected_table_names


def test_get_tables_handles_exception(mocker, reader):
    """
    Test that get_tables method handles exceptions correctly.
    """
    mock_client = mocker.MagicMock()
    mock_client.list_tables.side_effect = Exception("Failed to list tables")
    mocker.patch(
        "azure.data.tables.TableServiceClient.from_connection_string",
        return_value=mock_client
    )

    with pytest.raises(Exception) as exc_info:
        reader.get_tables()

    assert "Failed to list tables" in str(exc_info.value)
