#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


def test_get_table_service_client_returns_expected_client(mocker, reader):
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


def test_get_table_client_returns_expected_table(mocker, reader):
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


def test_get_tables_returns_expected_tables(mocker, reader, tables):
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
