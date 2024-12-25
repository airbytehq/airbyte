from http import HTTPStatus
from unittest.mock import MagicMock
import pytest
from source_pulse_aws_iam.streams import BaseIamStream, UsersStream, AccessKeysStream


@pytest.fixture
def config():
    return {
        "provider": {
            "auth_type": "credentials",
            "aws_access_key_id": "test_key",
            "aws_secret_access_key": "test_secret",
            "region": "us-east-1"
        }
    }


def test_request_params(config):
    stream = UsersStream(config)
    inputs = {
        "stream_slice": None,
        "stream_state": None,
        "next_page_token": None
    }
    expected_params = {"MaxItems": stream.max_items_per_page}
    assert stream.request_params(**inputs) == expected_params


def test_request_params_with_marker(config):
    stream = UsersStream(config)
    inputs = {
        "stream_slice": None,
        "stream_state": None,
        "next_page_token": {"Marker": "next-token"}
    }
    expected_params = {
        "MaxItems": stream.max_items_per_page,
        "Marker": "next-token"
    }
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(config):
    stream = UsersStream(config)
    response = {"Marker": None}
    assert stream.next_page_token(response) is None

    response = {"Marker": "next-page"}
    assert stream.next_page_token(response) == {"Marker": "next-page"}


def test_extract_records(config):
    stream = UsersStream(config)
    response = {
        "Users": [
            {"UserName": "test-user", "UserId": "AIDAXXXXXXXXXXXXX"}
        ]
    }
    assert list(stream.extract_records(response)) == response["Users"]


def test_read_records_error_handling(mocker, config):
    stream = UsersStream(config)
    mock_client = mocker.MagicMock()
    mock_client.list_users.side_effect = Exception("Test error")
    stream.client = mock_client

    records = list(stream.read_records(sync_mode="full_refresh"))
    assert len(records) == 0


def test_read_records_success(mocker, config):
    stream = UsersStream(config)
    mock_client = mocker.MagicMock()
    mock_client.list_users.return_value = {
        "Users": [
            {"UserName": "test-user", "UserId": "AIDAXXXXXXXXXXXXX"}
        ]
    }
    stream.client = mock_client

    records = list(stream.read_records(sync_mode="full_refresh"))
    assert len(records) == 1
    assert records[0]["UserName"] == "test-user"


def test_parent_child_stream_slice(mocker, config):
    parent_stream = UsersStream(config)
    child_stream = AccessKeysStream(config)

    mock_client = mocker.MagicMock()
    mock_client.list_users.return_value = {
        "Users": [
            {"UserName": "test-user", "UserId": "AIDAXXXXXXXXXXXXX"}
        ]
    }
    parent_stream.client = mock_client

    child_stream.parent_stream_class = lambda config: parent_stream

    slices = list(child_stream.stream_slices(sync_mode="full_refresh"))

    assert len(slices) > 0
    assert all("parent_id" in slice for slice in slices)
    assert slices[0]["parent_id"] == "test-user"


def test_parent_child_read_records(mocker, config):
    child_stream = AccessKeysStream(config)
    mock_client = mocker.MagicMock()
    mock_client.list_access_keys.return_value = {
        "AccessKeyMetadata": [
            {
                "AccessKeyId": "AKIAXXXXXXXXXXXXX",
                "Status": "Active"
            }
        ]
    }
    child_stream.client = mock_client

    slice = {"parent_id": "test-user"}
    records = list(child_stream.read_records(sync_mode="full_refresh", stream_slice=slice))
    assert len(records) == 1
    assert records[0]["AccessKeyId"] == "AKIAXXXXXXXXXXXXX"
    assert records[0]["UserName"] == "test-user"
