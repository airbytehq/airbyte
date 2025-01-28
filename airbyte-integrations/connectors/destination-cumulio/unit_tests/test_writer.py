#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import unittest
from typing import Any, Mapping
from unittest.mock import MagicMock, patch

import pytest
from destination_cumulio.writer import CumulioWriter

from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode


@pytest.fixture(name="logger")
def logger_fixture() -> MagicMock:
    return MagicMock()


@pytest.fixture(name="config")
def config_fixture() -> Mapping[str, Any]:
    return {
        "api_key": "123abc",
        "api_token": "456def",
        "api_host": "https://api.cumul.io",
    }


@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture() -> ConfiguredAirbyteCatalog:
    orders_stream_schema = {
        "type": "object",
        "properties": {
            "order_id": {"type": "integer"},
            "amount": {"type": "integer"},
            "customer_id": {"type": "string"},
        },
    }
    products_stream_schema = {
        "type": "object",
        "properties": {"product_id": {"type": "integer"}},
    }

    orders_append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name="orders",
            json_schema=orders_stream_schema,
            supported_sync_modes=[SyncMode.incremental],
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )

    products_overwrite_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name="products",
            json_schema=products_stream_schema,
            supported_sync_modes=[SyncMode.incremental],
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )

    return ConfiguredAirbyteCatalog(streams=[orders_append_stream, products_overwrite_stream])


@pytest.fixture(name="writer")
def writer_no_existing_cumulio_columns(
    config: Mapping[str, Any],
    configured_catalog: ConfiguredAirbyteCatalog,
    logger: MagicMock,
) -> CumulioWriter:
    """Returns a CumulioWriter using MagicMock, and mocking the return_value of all used CumulioClient methods."""
    with patch("destination_cumulio.writer.CumulioClient", MagicMock()) as cumulio_client_mock:
        # Mock get_ordered_columns to return no existing Cumul.io columns (dataset hasn't been created yet --> first sync)
        cumulio_client_mock.return_value.get_ordered_columns.return_value = []
        # cumulio_client_mock.return_value.batch_write.return_value = None
        # cumulio_client_mock.return_value.set_replace_tag_on_dataset.return_value = None
        return CumulioWriter(config, configured_catalog, logger)


def test_small_enough_data_point_limit(writer: CumulioWriter):
    """Tests whether the FLUSH_INTERVAL variable is smaller than the maximum amount of data points Cumul.io supports."""
    assert writer.FLUSH_INTERVAL <= 10000


def test_init(writer: CumulioWriter):
    """Tests whether CumulioWriter is correctly initialized for streams with no known Cumulio dataset (i.e. first sync for each stream)."""

    # Assert each stream is correctly initializing writers
    assert "orders" in writer.writers
    assert "products" in writer.writers

    # Assert each stream is correctly initializing empty write buffer
    assert len(writer.writers["orders"]["write_buffer"]) == 0
    assert len(writer.writers["products"]["write_buffer"]) == 0

    # Assert each stream is correctly initializing is_in_overwrite_sync_mode
    assert writer.writers["orders"]["is_in_overwrite_sync_mode"] is False
    assert writer.writers["products"]["is_in_overwrite_sync_mode"] is True

    # Assert each stream is correctly initializing is_first_batch to True
    assert writer.writers["orders"]["is_first_batch"] is True
    assert writer.writers["products"]["is_first_batch"] is True

    # Assert each stream is correctly initializing update_metadata (due to no columns from Cumul.io in this writer, both are True)
    assert writer.writers["orders"]["update_metadata"] is True
    assert writer.writers["products"]["update_metadata"] is True


def test_transform_data(writer: CumulioWriter):
    case = unittest.TestCase()

    data = {"order_id": 1, "amount": 100.0, "customer_id": "cust_1"}
    transformed_data = writer.transform_data("orders", data)
    case.assertCountEqual(transformed_data, ["cust_1", 1, 100.0])


def test_transform_data_missing_data(writer: CumulioWriter):
    case = unittest.TestCase()

    missing_data = {"order_id": 1, "customer_id": "cust_1"}
    transformed_data = writer.transform_data("orders", missing_data)
    case.assertCountEqual(transformed_data, ["cust_1", 1, None])


def test_transform_data_additional_data(writer: CumulioWriter):
    case = unittest.TestCase()

    additional_data = {
        "order_id": 1,
        "amount": 100.0,
        "customer_id": "cust_1",
        "custmer_name": "Customer 1",
    }
    transformed_data = writer.transform_data("orders", additional_data)
    case.assertCountEqual(transformed_data, ["cust_1", 1, 100.0])


def test_transform_data_bool_data(writer: CumulioWriter):
    case = unittest.TestCase()

    bool_data = {"order_id": 1, "amount": 100.0, "customer_id": True}
    transformed_data = writer.transform_data("orders", bool_data)
    case.assertCountEqual(transformed_data, ["true", 1, 100.0])


def test_transform_data_dict_data(writer: CumulioWriter):
    case = unittest.TestCase()

    dict_data = {"order_id": 1, "amount": 100.0, "customer_id": {"key": "value"}}
    transformed_data = writer.transform_data("orders", dict_data)
    case.assertCountEqual(transformed_data, ['{"key": "value"}', 1, 100.0])


def test_transform_data_arr_data(writer: CumulioWriter):
    case = unittest.TestCase()

    arr_data = {"order_id": 1, "amount": 100.0, "customer_id": ["test1", "test2"]}
    transformed_data = writer.transform_data("orders", arr_data)
    case.assertCountEqual(transformed_data, ['["test1", "test2"]', 1, 100.0])


def test_queue_write_operation(writer: CumulioWriter):
    # Set flush interval to max value to avoid flushing data
    writer.FLUSH_INTERVAL = 10000

    writer.client.batch_write = MagicMock()  # type: ignore

    case = unittest.TestCase()

    order_data = {"order_id": 1, "amount": 100.0, "customer_id": "customer_1"}
    writer.queue_write_operation("orders", order_data)

    # Assert that write_buffer from the orders stream contains a single value
    assert len(writer.writers["orders"]["write_buffer"]) == 1
    case.assertCountEqual(writer.writers["orders"]["write_buffer"][0], ["customer_1", 1, 100.0])


def test_queue_write_operation_two_streams(writer: CumulioWriter):
    # Set flush interval to max value to avoid flushing data
    writer.FLUSH_INTERVAL = 10000

    writer.client.batch_write = MagicMock()  # type: ignore

    order_data = {"order_id": 1, "amount": 100.0, "customer_id": "customer_1"}
    writer.queue_write_operation("orders", order_data)

    # Assert that write_buffer from the orders stream contains a single value
    assert len(writer.writers["orders"]["write_buffer"]) == 1

    product_data = {"product_id": 1}
    writer.queue_write_operation("products", product_data)

    # Assert that the orders write_buffer isn't influenced by write operations from the products stream
    assert len(writer.writers["orders"]["write_buffer"]) == 1

    # Assert that write_buffer from the products stream contains a single value
    assert len(writer.writers["products"]["write_buffer"]) == 1
    assert writer.writers["products"]["write_buffer"] == [[1]]

    product_data = {"product_id": 2}
    writer.queue_write_operation("products", product_data)
    # Assert that write_buffer from the orders stream contains two values
    assert writer.writers["products"]["write_buffer"] == [[1], [2]]


def test_queue_write_operation_non_existing_stream(writer: CumulioWriter):
    # Set flush interval to max value to avoid flushing data
    writer.FLUSH_INTERVAL = 10000

    writer.client.batch_write = MagicMock()  # type: ignore

    with pytest.raises(Exception):
        # Assert that an Exception is thrown upon trying to write to a non-existing stream
        writer.queue_write_operation("non_existing_stream", {"column": "value"})


def test_flush(writer: CumulioWriter):
    writer.client.batch_write = MagicMock()  # type: ignore

    writer.writers["orders"]["write_buffer"] = [["customer_1", 1, 100.0]]
    writer.flush("orders")
    assert writer.writers["orders"]["write_buffer"] == []


def test_queue_write_flush_operation(writer: CumulioWriter):
    # Set flush interval to 2 to cause flush after second row has been added to buffer
    writer.FLUSH_INTERVAL = 2

    writer.client.batch_write = MagicMock()  # type: ignore

    product_data = {"product_id": 1}
    writer.queue_write_operation("products", product_data)
    assert writer.writers["products"]["write_buffer"] == [[1]]

    product_data = {"product_id": 2}
    writer.queue_write_operation("products", product_data)
    assert writer.writers["products"]["write_buffer"] == []
    assert writer.writers["products"]["is_first_batch"] is False

    product_data = {"product_id": 3}
    writer.queue_write_operation("products", product_data)
    assert writer.writers["products"]["write_buffer"] == [[3]]


def test_flush_all(writer: CumulioWriter):
    writer.client.batch_write = MagicMock()  # type: ignore

    writer.writers["orders"]["write_buffer"] = [["cust_1", 1, 100.0]]
    writer.writers["products"]["write_buffer"] = [["cust_1", 1, 100.0]]
    writer.flush_all()
    assert writer.writers["orders"]["write_buffer"] == []
    assert writer.writers["products"]["write_buffer"] == []


def test_delete_stream_entries(writer: CumulioWriter):
    writer.client.set_replace_tag_on_dataset = MagicMock()  # type: ignore
    writer.delete_stream_entries("stream_name")
    writer.client.set_replace_tag_on_dataset.assert_called_once_with("stream_name")


def _get_cumulio_and_merged_columns(writer: CumulioWriter) -> Mapping[str, Any]:
    if len(writer.writers) < 0:
        raise Exception("No streams defined for writer")

    result = {}

    for stream_name in writer.writers:
        cumulio_columns = writer.client.get_ordered_columns(stream_name)
        merged_columns = writer.writers[stream_name]["column_headers"]
        result[stream_name] = {
            "cumulio_columns": cumulio_columns,
            "merged_columns": merged_columns,
        }
    return result


@pytest.fixture
def writer_existing_cumulio_columns(
    config: Mapping[str, Any],
    configured_catalog: ConfiguredAirbyteCatalog,
    logger: MagicMock,
) -> CumulioWriter:
    """This will return a CumulioWriter that mocks airbyte stream catalogs that contains the same columns as those existing in Cumul.io."""
    existing_cumulio_columns = {}
    for configured_stream in configured_catalog.streams:
        existing_cumulio_columns[configured_stream.stream.name] = [
            column_name for column_name in configured_stream.stream.json_schema["properties"]
        ]

    def get_existing_cumulio_columns(stream_name):
        return existing_cumulio_columns[stream_name]

    with patch("destination_cumulio.writer.CumulioClient", MagicMock()) as cumulio_client_mock:
        # Mock get_ordered_columns to return existing_cumulio_columns
        cumulio_client_mock.return_value.get_ordered_columns = MagicMock(side_effect=get_existing_cumulio_columns)
        return CumulioWriter(config, configured_catalog, logger)


def test_init_existing_cumulio_columns(writer_existing_cumulio_columns: CumulioWriter):
    """Tests whether each stream is correctly initializing update_metadata.
    Due to identical columns in Cumul.io for this writer, both are False.
    """
    assert writer_existing_cumulio_columns.writers["orders"]["update_metadata"] is False
    assert writer_existing_cumulio_columns.writers["products"]["update_metadata"] is False


def test_equal_cumulio_and_merged_columns(
    writer_existing_cumulio_columns: CumulioWriter,
):
    result = _get_cumulio_and_merged_columns(writer_existing_cumulio_columns)

    for stream_name in result:
        for index, column in enumerate(result[stream_name]["merged_columns"]):
            # Assert that merged_columns are in same order as columns defined on Cumul.io's side.
            assert result[stream_name]["cumulio_columns"][index] == column["name"]


def test_queue_write_operation_with_correct_data_order(
    writer_existing_cumulio_columns: CumulioWriter,
):
    writer_existing_cumulio_columns.client.batch_write = MagicMock()  # type: ignore

    result = _get_cumulio_and_merged_columns(writer_existing_cumulio_columns)
    # Set flush interval to max value to avoid flushing data
    writer_existing_cumulio_columns.FLUSH_INTERVAL = 10000

    order_data = {"order_id": 1, "amount": 100.0, "customer_id": "cust_1"}
    writer_existing_cumulio_columns.queue_write_operation("orders", order_data)
    expected_data = []
    for column in result["orders"]["merged_columns"]:
        expected_data.append(order_data[column["name"]])
    assert writer_existing_cumulio_columns.writers["orders"]["write_buffer"][0] == expected_data


@pytest.fixture(name="configured_catalog_with_new_column")
def configured_catalog_with_new_column_fixture() -> ConfiguredAirbyteCatalog:
    """Creates a ConfiguredAirbyteCatalog that will be used to mock a new column."""
    # The stream should have at least 2 schema properties (i.e. columns) defined.
    orders_stream_schema = {
        "type": "object",
        "properties": {
            "order_id": {"type": "integer"},
            "amount": {"type": "integer"},
            "customer_id": {"type": "string"},
            "customer_name": {"type": "string"},
        },
    }

    orders_append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name="orders_append",
            json_schema=orders_stream_schema,
            supported_sync_modes=[SyncMode.incremental],
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )

    orders_overwrite_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name="orders_overwrite",
            json_schema=orders_stream_schema,
            supported_sync_modes=[SyncMode.incremental],
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )

    return ConfiguredAirbyteCatalog(streams=[orders_append_stream, orders_overwrite_stream])


@pytest.fixture
def writer_new_airbyte_column(
    config: Mapping[str, Any],
    configured_catalog_with_new_column: ConfiguredAirbyteCatalog,
    logger: MagicMock,
) -> CumulioWriter:
    """This will return a CumulioWriter that mocks airbyte stream catalogs that contains one column that does not exist in Cumul.io."""
    existing_cumulio_columns = {}
    for configured_stream in configured_catalog_with_new_column.streams:
        columns = [column_name for column_name in configured_stream.stream.json_schema["properties"]]
        # get rid of the second element to mimic a new column being defined in configured_stream
        del columns[1]
        existing_cumulio_columns[configured_stream.stream.name] = columns

    def get_existing_cumulio_columns(stream_name):
        return existing_cumulio_columns[stream_name]

    with patch("destination_cumulio.writer.CumulioClient", MagicMock()) as cumulio_client_mock:
        # Mock get_ordered_columns to return existing_cumulio_columns (which does not include one column defined in configured stream)
        cumulio_client_mock.return_value.get_ordered_columns = MagicMock(side_effect=get_existing_cumulio_columns)
        cumulio_client_mock.return_value.batch_writer.return_value = None
        cumulio_client_mock.return_value.set_replace_tag_on_dataset.return_value = None
        return CumulioWriter(config, configured_catalog_with_new_column, logger)


def test_init_new_airbyte_column(writer_new_airbyte_column: CumulioWriter):
    """Tests whether each stream is correctly initializing update_metadata (due to new Column in Airbyte for this writer, both are True)"""
    assert writer_new_airbyte_column.writers["orders_append"]["update_metadata"] is True
    assert writer_new_airbyte_column.writers["orders_overwrite"]["update_metadata"] is True


def test_new_column_update_metadata(writer_new_airbyte_column: CumulioWriter):
    """Tests whether Airbyte streams with at least one new column defined results in update_metadata,
    to inform Cumul.io about new column data being pushed."""
    for stream_name in writer_new_airbyte_column.writers:
        assert writer_new_airbyte_column.writers[stream_name]["update_metadata"] is True


def test_new_column_appended(writer_new_airbyte_column: CumulioWriter):
    """Tests whether the Airbyte streams with one new column appends it at the end of the column list"""
    result = _get_cumulio_and_merged_columns(writer_new_airbyte_column)
    for stream_name in result:
        assert len(result[stream_name]["merged_columns"]) == len(result[stream_name]["cumulio_columns"]) + 1
        for index, column in enumerate(result[stream_name]["cumulio_columns"]):
            # Assert that merged_columns are in same order as columns defined on Cumul.io's side.
            assert result[stream_name]["merged_columns"][index]["name"] == column
        with pytest.raises(Exception):
            # Test whether last element of merged_columns is the column that is not defined on Cumul.io's end.
            result[stream_name]["cumulio_columns"].index(result[stream_name]["merged_columns"][-1]["name"])


@pytest.fixture(name="configured_catalog_with_deleted_column")
def configured_catalog_with_deleted_column_fixture() -> ConfiguredAirbyteCatalog:
    """Creates a ConfiguredAirbyteCatalog that will be used to mock a deleted column."""
    orders_stream_schema = {
        "type": "object",
        "properties": {"order_id": {"type": "integer"}, "amount": {"type": "integer"}},
    }

    orders_append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name="orders_append",
            json_schema=orders_stream_schema,
            supported_sync_modes=[SyncMode.incremental],
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )

    orders_overwrite_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name="orders_overwrite",
            json_schema=orders_stream_schema,
            supported_sync_modes=[SyncMode.incremental],
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )

    return ConfiguredAirbyteCatalog(streams=[orders_append_stream, orders_overwrite_stream])


@pytest.fixture
def writer_deleted_airbyte_column(
    config: Mapping[str, Any],
    configured_catalog_with_deleted_column: ConfiguredAirbyteCatalog,
    logger: MagicMock,
) -> CumulioWriter:
    """This will return a CumulioWriter that mocks airbyte stream catalogs that doesn't contain one column that does exist in Cumul.io."""
    existing_cumulio_columns = {}
    for configured_stream in configured_catalog_with_deleted_column.streams:
        columns = [column_name for column_name in configured_stream.stream.json_schema["properties"]]
        # Add customer_name column as second element to mimic a deleted column being defined in configured_stream
        columns.insert(1, "customer_name")
        existing_cumulio_columns[configured_stream.stream.name] = columns

    def get_existing_cumulio_columns(stream_name):
        return existing_cumulio_columns[stream_name]

    with patch("destination_cumulio.writer.CumulioClient", MagicMock()) as cumulio_client_mock:
        # Mock get_ordered_columns to return existing_cumulio_columns (which does not include one column defined in configured stream)
        cumulio_client_mock.return_value.get_ordered_columns = MagicMock(side_effect=get_existing_cumulio_columns)
        cumulio_client_mock.return_value.batch_writer.return_value = None
        cumulio_client_mock.return_value.set_replace_tag_on_dataset.return_value = None
        return CumulioWriter(config, configured_catalog_with_deleted_column, logger)


def test_init_deleted_airbyte_column(writer_deleted_airbyte_column: CumulioWriter):
    """Assert each stream is correctly initializing update_metadata.
    Due to deleted Column in Airbyte for this writer:
    - the update_metadata property for the orders dataset is set to False, as it's in append mode and thus should keep existing structure
    - the update_metadata property for the orders dataset is set to True, as it's in overwrite mode
    """
    assert writer_deleted_airbyte_column.writers["orders_append"]["update_metadata"] is False
    assert writer_deleted_airbyte_column.writers["orders_overwrite"]["update_metadata"] is True


def test_deleted_column_update_metadata(writer_deleted_airbyte_column: CumulioWriter):
    """Tests whether Airbyte streams that do not contain a column defined on Cumul.io's side results in update_metadata for only
    overwrite streams (to inform Cumul.io about new column data being pushed)"""
    assert writer_deleted_airbyte_column.writers["orders_append"]["update_metadata"] is False
    assert writer_deleted_airbyte_column.writers["orders_overwrite"]["update_metadata"] is True


def test_merged_columns_order_for_deleted_column(
    writer_deleted_airbyte_column: CumulioWriter,
):
    """Tests whether Airbyte streams that do not contain a column defined on Cumul.io's side still correctly puts the other columns in
    the right order"""
    result = _get_cumulio_and_merged_columns(writer_deleted_airbyte_column)
    for stream_name in result:
        # Test whether merged_columns contains one less element
        assert len(result[stream_name]["merged_columns"]) == len(result[stream_name]["cumulio_columns"]) - 1

        cumulio_columns_without_deleted = [
            column_name for column_name in result[stream_name]["cumulio_columns"] if column_name != "customer_name"
        ]
        # Test whether elements, without deleted column, are equal and in the same position
        assert cumulio_columns_without_deleted == [column["name"] for column in result[stream_name]["merged_columns"]]
