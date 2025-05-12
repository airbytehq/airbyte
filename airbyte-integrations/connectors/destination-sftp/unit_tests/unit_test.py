#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest
from destination_sftp.client import SftpClient


@pytest.fixture
def json_client() -> SftpClient:
    return SftpClient("sample-host", "sample-username", "sample-password", "/sample/path", file_format="json")


@pytest.fixture
def csv_client() -> SftpClient:
    return SftpClient("sample-host", "sample-username", "sample-password", "/sample/path", file_format="csv")


@pytest.fixture
def default_client() -> SftpClient:
    # Test backward compatibility - no file_format specified should default to JSON
    return SftpClient("sample-host", "sample-username", "sample-password", "/sample/path")


@pytest.fixture
def directory_pattern_client() -> SftpClient:
    return SftpClient(
        "sample-host",
        "sample-username",
        "sample-password",
        "/sample/path",
        file_format="json",
        file_name_pattern="{format}/{stream}/{date}",
    )


def test_json_get_path(json_client):
    path = json_client._get_path("mystream")
    assert path == "/sample/path/airbyte_json_mystream.jsonl"


def test_csv_get_path(csv_client):
    path = csv_client._get_path("mystream")
    assert path == "/sample/path/airbyte_csv_mystream.csv"


def test_default_format_is_json(default_client):
    path = default_client._get_path("mystream")
    assert path == "/sample/path/airbyte_json_mystream.jsonl"
    assert default_client.file_format == "json"


def test_json_get_uri(json_client):
    uri = json_client._get_uri("mystream2")
    assert uri == "sftp://sample-username:sample-password@sample-host:22/sample/path/airbyte_json_mystream2.jsonl"


def test_csv_get_uri(csv_client):
    uri = csv_client._get_uri("mystream2")
    assert uri == "sftp://sample-username:sample-password@sample-host:22/sample/path/airbyte_csv_mystream2.csv"


def test_directory_pattern():
    client = SftpClient(
        "sample-host",
        "sample-username",
        "sample-password",
        "/sample/path",
        file_format="json",
        file_name_pattern="{format}/{stream}/{date}",
    )

    import datetime

    current_date = datetime.datetime.now().strftime("%Y%m%d")

    path = client._get_path("mystream")
    assert path == f"/sample/path/json/mystream/{current_date}.jsonl"

    uri = client._get_uri("mystream")
    assert "sample-username" in uri
    assert "sample-password" in uri
    assert f"/sample/path/json/mystream/{current_date}.jsonl" in uri


def test_nested_directory_pattern():
    client = SftpClient(
        "sample-host",
        "sample-username",
        "sample-password",
        "/sample/path",
        file_format="csv",
        file_name_pattern="data/{format}/streams/{stream}",
    )

    path = client._get_path("mystream")
    assert path == "/sample/path/data/csv/streams/mystream.csv"


def test_extension_added_if_missing():
    # Test that the correct extension is added if not included in the pattern
    client = SftpClient(
        "sample-host", "sample-username", "sample-password", "/sample/path", file_format="csv", file_name_pattern="data_{stream}"
    )

    path = client._get_path("mystream")
    assert path == "/sample/path/data_mystream.csv"
