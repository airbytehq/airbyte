#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest
from destination_sftp_json.client import SftpClient
from smart_open.ssh import parse_uri


@pytest.fixture
def client() -> SftpClient:
    return SftpClient("sample-host", "sample-username", "sample-password", "/sample/path")


def test_get_path(client):
    path = client._get_path("mystream")
    assert path == "/sample/path/airbyte_json_mystream.jsonl"


def test_get_uri(client):
    uri = client._get_uri("mystream2")
    assert uri == "sftp://sample-username:sample-password@sample-host:22//sample/path/airbyte_json_mystream2.jsonl"


def test_get_uri_escapes_reserved_characters():
    client = SftpClient("sample-host", "sample-username", "sample#password", "/sample/path", port=2222)

    uri = client._get_uri("mystream")

    assert uri == "sftp://sample-username:sample%23password@sample-host:2222//sample/path/airbyte_json_mystream.jsonl"
    assert parse_uri(uri)["password"] == "sample#password"
    assert parse_uri(uri)["port"] == 2222
