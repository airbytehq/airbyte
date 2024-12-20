#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, Mapping
from unittest.mock import ANY, MagicMock, patch

import pytest
from destination_cumulio.client import CumulioClient


# "# type: ignore" was added in several places to avoid mypy complaining about patching functions with MagicMock


@pytest.fixture(name="logger")
def logger_fixture() -> MagicMock:
    return MagicMock()


@pytest.fixture(name="cumulio_client")
def cumulio_client_fixture(logger: MagicMock) -> CumulioClient:
    # Create a mock configuration dictionary
    config = {
        "api_key": "123456",
        "api_token": "abcdef",
        "api_host": "https://api.cumul.io",
    }
    # Initialize a CumulioClient object with the mock configuration for the Cumulio class
    with patch("destination_cumulio.client.Cumulio", MagicMock()):
        return CumulioClient(config, logger)


@pytest.fixture(name="dummy_data")
def dummy_data_fixture() -> Mapping[str, Any]:
    return {
        "data": [
            [
                "Text value 1",
                1,
                "2022-01-01T00:00:00.000Z",
            ],
            ["Text value 2", 2, "2022-02-01T00:00:00.000Z"],
            ["Text value 3", 3, "2022-03-01T00:00:00.000Z"],
        ],
        "columns": ["Text column", "Numeric column", "Datetime column"],
    }


# tests for batch_write method


def test_batch_write_append_empty_write_buffer(cumulio_client: CumulioClient):
    cumulio_client._get_dataset_id_from_stream_name = MagicMock(return_value="dataset_id")  # type: ignore
    cumulio_client._push_batch_to_new_dataset = MagicMock()  # type: ignore
    cumulio_client._push_batch_to_existing_dataset = MagicMock()  # type: ignore

    cumulio_client.batch_write(
        stream_name="test-stream",
        write_buffer=[],
        column_headers=["test-column"],
        is_in_overwrite_sync_mode=False,
        is_first_batch=True,
        update_metadata=True,
    )

    cumulio_client._get_dataset_id_from_stream_name.assert_not_called()
    cumulio_client._push_batch_to_new_dataset.assert_not_called()
    cumulio_client._push_batch_to_existing_dataset.assert_not_called()

    cumulio_client.batch_write(
        stream_name="test-stream",
        write_buffer=[[]],
        column_headers=["test-column"],
        is_in_overwrite_sync_mode=False,
        is_first_batch=True,
        update_metadata=True,
    )

    cumulio_client._get_dataset_id_from_stream_name.assert_not_called()
    cumulio_client._push_batch_to_new_dataset.assert_not_called()
    cumulio_client._push_batch_to_existing_dataset.assert_not_called()


def test_batch_write_append_no_existing_dataset(cumulio_client: CumulioClient, dummy_data: Mapping[str, Any]):
    cumulio_client.client.get = MagicMock(return_value={"count": 0, "Rows": []})
    cumulio_client._push_batch_to_new_dataset = MagicMock()  # type: ignore
    cumulio_client._push_batch_to_existing_dataset = MagicMock()  # type: ignore

    stream_name = "test-stream"

    cumulio_client.batch_write(
        stream_name=stream_name,
        write_buffer=dummy_data["data"],
        column_headers=dummy_data["columns"],
        is_in_overwrite_sync_mode=False,
        is_first_batch=True,
        update_metadata=True,
    )

    expected_properties = {
        "where": {"type": "dataset"},
        "attributes": ["id", "name"],
        "include": [
            {
                "model": "Tag",
                "where": {"tag": cumulio_client.TAG_PREFIX + stream_name},
                "attributes": ["id", "tag"],
                "jointype": "inner",
            }
        ],
    }

    cumulio_client.client.get.assert_called_once_with("securable", expected_properties)

    cumulio_client._push_batch_to_existing_dataset.assert_not_called()

    cumulio_client._push_batch_to_new_dataset.assert_called_once_with(stream_name, dummy_data["data"], dummy_data["columns"])


def test_batch_write_existing_dataset_no_first_batch_replace(cumulio_client: CumulioClient, dummy_data: Mapping[str, Any]):
    cumulio_client._get_dataset_id_from_stream_name = MagicMock(return_value="dataset_id")  # type: ignore
    cumulio_client._push_batch_to_new_dataset = MagicMock()  # type: ignore
    cumulio_client._push_batch_to_existing_dataset = MagicMock()  # type: ignore
    cumulio_client._dataset_contains_replace_tag = MagicMock(return_value=False)  # type: ignore

    stream_name = "test-stream"

    cumulio_client.batch_write(
        stream_name=stream_name,
        write_buffer=dummy_data["data"],
        column_headers=dummy_data["columns"],
        is_in_overwrite_sync_mode=False,
        is_first_batch=True,
        update_metadata=True,
    )
    cumulio_client._push_batch_to_new_dataset.assert_not_called()
    cumulio_client._dataset_contains_replace_tag.assert_called_once_with("dataset_id")
    cumulio_client._push_batch_to_existing_dataset.assert_called_once_with(
        "dataset_id", dummy_data["data"], dummy_data["columns"], False, True
    )


def test_batch_write_existing_dataset_first_batch_replace_overwrite_mode(cumulio_client: CumulioClient, dummy_data: Mapping[str, Any]):
    cumulio_client._get_dataset_id_from_stream_name = MagicMock(return_value="dataset_id")  # type: ignore
    cumulio_client._push_batch_to_new_dataset = MagicMock()  # type: ignore
    cumulio_client._push_batch_to_existing_dataset = MagicMock()  # type: ignore
    cumulio_client._dataset_contains_replace_tag = MagicMock(return_value=False)  # type: ignore

    stream_name = "test-stream"

    cumulio_client.batch_write(
        stream_name=stream_name,
        write_buffer=dummy_data["data"],
        column_headers=dummy_data["columns"],
        is_in_overwrite_sync_mode=True,
        is_first_batch=True,
        update_metadata=True,
    )
    cumulio_client._push_batch_to_new_dataset.assert_not_called()
    cumulio_client._dataset_contains_replace_tag.assert_called_once_with("dataset_id")
    cumulio_client._push_batch_to_existing_dataset.assert_called_once_with(
        "dataset_id", dummy_data["data"], dummy_data["columns"], True, True
    )


def test_batch_write_existing_dataset_first_batch_replace_tag(cumulio_client: CumulioClient, dummy_data: Mapping[str, Any]):
    cumulio_client._get_dataset_id_from_stream_name = MagicMock(return_value="dataset_id")  # type: ignore
    cumulio_client._push_batch_to_new_dataset = MagicMock()  # type: ignore
    cumulio_client._push_batch_to_existing_dataset = MagicMock()  # type: ignore
    cumulio_client._dataset_contains_replace_tag = MagicMock(return_value=True)  # type: ignore

    stream_name = "test-stream"

    cumulio_client.batch_write(
        stream_name=stream_name,
        write_buffer=dummy_data["data"],
        column_headers=dummy_data["columns"],
        is_in_overwrite_sync_mode=False,
        is_first_batch=True,
        update_metadata=True,
    )
    cumulio_client._push_batch_to_new_dataset.assert_not_called()
    cumulio_client._dataset_contains_replace_tag.assert_called_once_with("dataset_id")
    cumulio_client._push_batch_to_existing_dataset.assert_called_once_with(
        "dataset_id", dummy_data["data"], dummy_data["columns"], True, True
    )


def test_batch_write_existing_dataset_non_first_batch(cumulio_client: CumulioClient, dummy_data: Mapping[str, Any]):
    cumulio_client._get_dataset_id_from_stream_name = MagicMock(return_value="dataset_id")  # type: ignore
    cumulio_client._push_batch_to_new_dataset = MagicMock()  # type: ignore
    cumulio_client._push_batch_to_existing_dataset = MagicMock()  # type: ignore
    cumulio_client._dataset_contains_replace_tag = MagicMock(return_value=True)  # type: ignore

    stream_name = "test-stream"

    cumulio_client.batch_write(
        stream_name=stream_name,
        write_buffer=dummy_data["data"],
        column_headers=dummy_data["columns"],
        is_in_overwrite_sync_mode=True,
        is_first_batch=False,
        update_metadata=True,
    )
    cumulio_client._push_batch_to_new_dataset.assert_not_called()
    cumulio_client._dataset_contains_replace_tag.assert_called_once_with("dataset_id")
    cumulio_client._push_batch_to_existing_dataset.assert_called_once_with(
        "dataset_id", dummy_data["data"], dummy_data["columns"], False, True
    )


# tests for test_api_token method


def test_api_token_unknown_combination(cumulio_client: CumulioClient):
    """ "Test that the test_api_token method correctly throws an error upon an invalid combination"""
    cumulio_client.client.get = MagicMock(return_value={"count": 0})
    with pytest.raises(Exception):
        cumulio_client.test_api_token()


def test_api_token_api_call(cumulio_client: CumulioClient):
    """ "Test that the test_api_token method makes an API request to the authorization endpoint"""
    cumulio_client.client.get = MagicMock(return_value={"count": 1})
    cumulio_client.test_api_token()
    cumulio_client.client.get.assert_called_with("authorization", {"where": {"type": "api"}})


def test_test_data_push_method(cumulio_client: CumulioClient, dummy_data: Mapping[str, Any]):
    """ "Test that the test_data_push method deletes the dataset afterwards"""
    cumulio_client.batch_write = MagicMock()  # type: ignore
    cumulio_client.delete_dataset = MagicMock()  # type: ignore

    stream_name = "test-stream"

    cumulio_client.test_data_push(stream_name, dummy_data["data"], dummy_data["columns"])

    cumulio_client.delete_dataset.assert_called_once_with("test-stream")


# tests for delete_dataset method


def test_delete_dataset_no_dataset_found(cumulio_client: CumulioClient):
    cumulio_client.client.delete = MagicMock()
    cumulio_client._get_dataset_id_from_stream_name = MagicMock(return_value=None)  # type: ignore

    cumulio_client.delete_dataset("stream_name")

    # assert that the _get_dataset_id_from_stream_name method was called once with the correct arguments
    cumulio_client._get_dataset_id_from_stream_name.assert_called_once_with("stream_name")

    # assert that the client.delete method is not called as no dataset was found
    cumulio_client.client.delete.assert_not_called()


def test_delete_dataset_dataset_found(cumulio_client: CumulioClient):
    cumulio_client.client.delete = MagicMock()
    cumulio_client._get_dataset_id_from_stream_name = MagicMock(  # type: ignore
        return_value="dataset_id"
    )  # type: ignore

    cumulio_client.delete_dataset("stream_name")

    # assert that the _get_dataset_id_from_stream_name method was called once with the correct arguments
    cumulio_client._get_dataset_id_from_stream_name.assert_called_once_with("stream_name")

    # assert that the client.delete method was called once with the correct arguments
    cumulio_client.client.delete.assert_called_once_with("securable", "dataset_id")


# tests for get_ordered_columns method


def test_get_ordered_columns_dataset_not_created(cumulio_client: CumulioClient):
    cumulio_client.get_dataset_and_columns_from_stream_name = MagicMock(return_value=None)  # type: ignore
    result = cumulio_client.get_ordered_columns("stream_name")
    assert result == []


def test_get_ordered_columns_same_order(cumulio_client: CumulioClient):
    cumulio_dataset_and_columns = {
        "id": "dataset_id",
        "columns": [
            {"source_name": "column1", "order": 2},
            {"source_name": "column2", "order": 1},
        ],
    }
    cumulio_client.get_dataset_and_columns_from_stream_name = MagicMock(return_value=cumulio_dataset_and_columns)  # type: ignore
    result = cumulio_client.get_ordered_columns("stream_name")
    assert result == ["column2", "column1"]


# tests for _push_batch_to_new_dataset method


def test_push_batch_to_new_dataset(cumulio_client: CumulioClient, dummy_data: Mapping[str, Any]):
    cumulio_client.client.create = MagicMock(return_value={"rows": [{"id": "new_dataset_id"}]})
    cumulio_client._associate_tag_dataset_id = MagicMock()  # type: ignore

    stream_name = "test_stream"

    expected_request_properties = {
        "type": "create",
        "data": dummy_data["data"],
        "options": {
            "header": dummy_data["columns"],
            "update_metadata": True,
            "name": {"en": cumulio_client.INITIAL_DATASET_NAME_PREFIX + stream_name},
        },
    }
    cumulio_client._push_batch_to_new_dataset(stream_name, dummy_data["data"], dummy_data["columns"])
    cumulio_client.client.create.assert_called_once_with("data", expected_request_properties)
    cumulio_client._associate_tag_dataset_id.assert_called_once_with(stream_name, "new_dataset_id")


def test_push_batch_to_new_dataset_all_retries_error(cumulio_client: CumulioClient, dummy_data: Mapping[str, Any]):
    cumulio_client.client.create = MagicMock(side_effect=RuntimeError("Internal Server Error"))
    stream_name = "test_stream"

    with patch("destination_cumulio.client.time", MagicMock()):
        with pytest.raises(Exception):
            cumulio_client._push_batch_to_new_dataset(stream_name, dummy_data["data"], dummy_data["columns"])


def test_push_batch_to_new_dataset_first_try_fails(cumulio_client: CumulioClient, dummy_data: Mapping[str, Any]):
    effects = iter([RuntimeError("Internal Server Error")])

    def side_effect(*_):
        try:
            raise next(effects)
        except StopIteration:
            return {"rows": [{"id": "new_dataset_id"}]}

    cumulio_client.client.create = MagicMock(side_effect=side_effect)
    cumulio_client._associate_tag_dataset_id = MagicMock()  # type: ignore

    stream_name = "test_stream"

    expected_request_properties = {
        "type": "create",
        "data": dummy_data["data"],
        "options": {
            "header": dummy_data["columns"],
            "update_metadata": True,
            "name": {"en": cumulio_client.INITIAL_DATASET_NAME_PREFIX + stream_name},
        },
    }

    with patch("destination_cumulio.client.time", MagicMock()):
        cumulio_client._push_batch_to_new_dataset(stream_name, dummy_data["data"], dummy_data["columns"])
        cumulio_client.client.create.assert_called_with("data", expected_request_properties)

        assert cumulio_client.client.create.call_count == 2

        cumulio_client._associate_tag_dataset_id.assert_called_once_with(stream_name, "new_dataset_id")


# tests for _push_batch_to_existing_dataset method


def test_push_batch_to_existing_dataset_all_retries_error(cumulio_client: CumulioClient, dummy_data: Mapping[str, Any]):
    cumulio_client.client.create = MagicMock(side_effect=RuntimeError("Internal Server Error"))
    cumulio_client._remove_replace_tag_dataset_id_association = MagicMock()  # type: ignore

    dataset_id = "dataset_id"

    with patch("destination_cumulio.client.time", MagicMock()):
        with pytest.raises(Exception):
            cumulio_client._push_batch_to_existing_dataset(dataset_id, dummy_data["data"], dummy_data["columns"], False, True)


def test_push_batch_to_existing_dataset_first_try_fails(cumulio_client: CumulioClient, dummy_data: Mapping[str, Any]):
    effects = iter([RuntimeError("Internal Server Error")])

    def side_effect(*_):
        try:
            raise next(effects)
        except StopIteration:
            return None

    cumulio_client.client.create = MagicMock(side_effect=side_effect)
    cumulio_client._remove_replace_tag_dataset_id_association = MagicMock()  # type: ignore

    dataset_id = "dataset_id"

    expected_request_properties = {
        "type": "append",
        "data": dummy_data["data"],
        "securable_id": dataset_id,
        "options": {
            "header": dummy_data["columns"],
            "update_metadata": True,
        },
    }

    with patch("destination_cumulio.client.time", MagicMock()):
        cumulio_client._push_batch_to_existing_dataset(dataset_id, dummy_data["data"], dummy_data["columns"], False, True)
        cumulio_client.client.create.assert_called_with("data", expected_request_properties)

        assert cumulio_client.client.create.call_count == 2

        cumulio_client._remove_replace_tag_dataset_id_association.assert_not_called()


def test_push_batch_to_existing_dataset_no_first_batch_replace(cumulio_client: CumulioClient, dummy_data: Mapping[str, Any]):
    cumulio_client.client.create = MagicMock()
    cumulio_client._remove_replace_tag_dataset_id_association = MagicMock()  # type: ignore

    dataset_id = "dataset_id"

    expected_request_properties = {
        "type": "append",
        "data": dummy_data["data"],
        "securable_id": dataset_id,
        "options": {
            "header": dummy_data["columns"],
            "update_metadata": True,
        },
    }

    cumulio_client._push_batch_to_existing_dataset(dataset_id, dummy_data["data"], dummy_data["columns"], False, True)
    cumulio_client.client.create.assert_called_once_with("data", expected_request_properties)
    cumulio_client._remove_replace_tag_dataset_id_association.assert_not_called()


def test_push_batch_to_existing_dataset_first_batch_replace(cumulio_client: CumulioClient, dummy_data: Mapping[str, Any]):
    cumulio_client.client.create = MagicMock()
    cumulio_client._remove_replace_tag_dataset_id_association = MagicMock()  # type: ignore

    dataset_id = "dataset_id"

    expected_request_properties = {
        "type": "replace",
        "data": dummy_data["data"],
        "securable_id": dataset_id,
        "options": {
            "header": dummy_data["columns"],
            "update_metadata": True,
        },
    }

    cumulio_client._push_batch_to_existing_dataset(dataset_id, dummy_data["data"], dummy_data["columns"], True, True)
    cumulio_client.client.create.assert_called_once_with("data", expected_request_properties)
    cumulio_client._remove_replace_tag_dataset_id_association.assert_called_once_with(dataset_id)


# tests for _dataset_contains_replace_tag method


def test_get_dataset_and_columns_from_stream_name_no_dataset(
    cumulio_client: CumulioClient,
):
    cumulio_dataset_and_columns_result = {"count": 0, "rows": []}

    # Test when no dataset is found
    cumulio_client.client.get = MagicMock(return_value=cumulio_dataset_and_columns_result)
    result = cumulio_client.get_dataset_and_columns_from_stream_name("test_stream")
    assert result is None


def test_get_dataset_and_columns_from_stream_name_single_existing_dataset(
    cumulio_client: CumulioClient,
):
    cumulio_dataset_and_columns_result: Mapping[str, Any] = {
        "count": 1,
        "rows": [
            {
                "id": "dataset_id",
                "columns": [
                    {"source_name": "column1", "order": 2},
                    {"source_name": "column2", "order": 1},
                ],
            }
        ],
    }
    # Test when dataset is found
    cumulio_client.client.get = MagicMock(return_value=cumulio_dataset_and_columns_result)
    result = cumulio_client.get_dataset_and_columns_from_stream_name("test_stream")
    assert result["id"] == cumulio_dataset_and_columns_result["rows"][0]["id"]
    assert result["columns"] == cumulio_dataset_and_columns_result["rows"][0]["columns"]


def test_get_dataset_and_columns_from_stream_name_multiple_existing_datasets(
    cumulio_client: CumulioClient,
):
    """Tests whether an exception is thrown when multiple datasets are returned for a stream name"""
    cumulio_dataset_and_columns_result = {
        "count": 2,
        "rows": [
            {
                "id": "dataset_id_1",
                "columns": [
                    {"source_name": "column1", "order": 2},
                    {"source_name": "column2", "order": 1},
                ],
            },
            {
                "id": "dataset_id_2",
                "columns": [
                    {"source_name": "column1", "order": 1},
                    {"source_name": "column2", "order": 2},
                ],
            },
        ],
    }
    # Test when multiple datasets are found
    cumulio_client.client.get = MagicMock(return_value=cumulio_dataset_and_columns_result)
    with pytest.raises(Exception):
        cumulio_client.get_dataset_and_columns_from_stream_name("test_stream")


# tests for the set_replace_tag_on_dataset method


def test_set_replace_tag_on_dataset_no_dataset_found(cumulio_client: CumulioClient):
    cumulio_client._get_dataset_id_from_stream_name = MagicMock(return_value=None)  # type: ignore
    cumulio_client._associate_tag_dataset_id = MagicMock()  # type: ignore

    cumulio_client.set_replace_tag_on_dataset("stream_name")

    cumulio_client._get_dataset_id_from_stream_name.assert_called_once_with("stream_name")
    cumulio_client._associate_tag_dataset_id.assert_not_called()


def test_set_replace_tag_on_dataset_existing_dataset(cumulio_client: CumulioClient):
    cumulio_client._get_dataset_id_from_stream_name = MagicMock(return_value="dataset_id")  # type: ignore
    cumulio_client._associate_tag_dataset_id = MagicMock()  # type: ignore

    cumulio_client.set_replace_tag_on_dataset("stream_name")

    cumulio_client._get_dataset_id_from_stream_name.assert_called_once_with("stream_name")
    cumulio_client._associate_tag_dataset_id.assert_called_once_with(cumulio_client.REPLACE_TAG, "dataset_id")


# tests for _dataset_contains_replace_tag method


def test_dataset_contains_replace_tag(cumulio_client: CumulioClient):
    dataset_id = "123"
    cumulio_client.client.get = MagicMock(return_value={"count": 1})
    assert cumulio_client._dataset_contains_replace_tag(dataset_id) is True


def test_dataset_does_not_contain_replace_tag(cumulio_client: CumulioClient):
    dataset_id = "123"
    cumulio_client.client.get = MagicMock(return_value={"count": 0})
    assert cumulio_client._dataset_contains_replace_tag(dataset_id) is False


# tests for _get_dataset_id_from_stream_name method


def test_get_dataset_id_from_stream_name_no_dataset(cumulio_client: CumulioClient):
    cumulio_client.client.get.return_value = {"count": 0, "rows": []}
    dataset_id = cumulio_client._get_dataset_id_from_stream_name("test_stream")
    assert dataset_id is None


def test_get_dataset_id_from_stream_name_single_dataset(cumulio_client: CumulioClient):
    cumulio_client.client.get.return_value = {
        "count": 1,
        "rows": [{"id": "dataset_id", "name": "Test dataset"}],
    }
    dataset_id = cumulio_client._get_dataset_id_from_stream_name("test_stream")
    assert dataset_id == "dataset_id"


def test_get_dataset_id_from_stream_name_multiple_datasets(
    cumulio_client: CumulioClient,
):
    """Tests whether an exception is thrown when multiple datasets are returned for a stream name"""
    cumulio_client.client.get.return_value = {
        "count": 2,
        "rows": [
            {"id": "dataset_id_1", "name": "Test dataset 1"},
            {"id": "dataset_id_2", "name": "Test dataset 2"},
        ],
    }
    with pytest.raises(Exception):
        cumulio_client._get_dataset_id_from_stream_name("test_stream")


# tests for _associate_tag_dataset_id method


def test_associate_tag_dataset_id_no_tag_found(cumulio_client: CumulioClient):
    cumulio_client._get_tag_id = MagicMock(return_value=None)  # type: ignore
    cumulio_client._create_and_associate_stream_name_tag_with_dataset_id = MagicMock()  # type: ignore
    cumulio_client._associate_tag_with_dataset_id = MagicMock()  # type: ignore

    cumulio_client._associate_tag_dataset_id("test_stream", "test_dataset_id")

    cumulio_client._create_and_associate_stream_name_tag_with_dataset_id.assert_called_once_with("test_stream", "test_dataset_id")
    cumulio_client._associate_tag_with_dataset_id.assert_not_called()


def test_associate_tag_dataset_id_tag_found(cumulio_client: CumulioClient):
    cumulio_client._get_tag_id = MagicMock(return_value="tag_id")  # type: ignore
    cumulio_client._create_and_associate_stream_name_tag_with_dataset_id = MagicMock()  # type: ignore
    cumulio_client._associate_tag_with_dataset_id = MagicMock()  # type: ignore

    cumulio_client._associate_tag_dataset_id("test_stream", "test_dataset_id")

    cumulio_client._associate_tag_with_dataset_id.assert_called_once_with("tag_id", "test_dataset_id")
    cumulio_client._create_and_associate_stream_name_tag_with_dataset_id.assert_not_called()


# tests for _get_tag_id method


def test_get_tag_id_no_tag_found(cumulio_client: CumulioClient):
    tag_api_response = {"count": 0, "rows": []}
    cumulio_client.client.get = MagicMock(return_value=tag_api_response)

    result = cumulio_client._get_tag_id("test_stream")

    cumulio_client.client.get.assert_called_once_with("tag", ANY)
    assert result is None


def test_get_tag_id_tag_found(cumulio_client: CumulioClient):
    tag_api_response: Mapping[str, Any] = {"count": 1, "rows": [{"id": "test_tag_id"}]}
    cumulio_client.client.get = MagicMock(return_value=tag_api_response)

    result = cumulio_client._get_tag_id("test_stream")

    cumulio_client.client.get.assert_called_once_with("tag", ANY)
    assert result == tag_api_response["rows"][0]["id"]
