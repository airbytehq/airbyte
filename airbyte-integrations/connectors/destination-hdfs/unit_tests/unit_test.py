# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from pathlib import Path
from unittest import mock

import pytest

from destination_hdfs.client import HDFSClient
from hdfs import InsecureClient


@pytest.mark.parametrize(
    "config, expected_client",
    [
        # Using defaults
        (
            {
                "host": "hdfs-host",
                "user": "me",
            },
            InsecureClient("http://hdfs-host:50070", user="me"),
        ),
        # Different port
        (
            {
                "host": "hdfs-host",
                "user": "me",
                "port": 33,
            },
            InsecureClient("http://hdfs-host:33", user="me"),
        ),
    ],
)
def test_get_uri(config, expected_client):
    hdfs_client = HDFSClient(
        **config, destination_path="/foo", stream="bar"
    ).get_client()
    assert hdfs_client.url == expected_client.url
    assert (
        hdfs_client._session.params["user.name"]
        == expected_client._session.params["user.name"]
    )


def test_path():
    hdfs_client = HDFSClient(
        host="hdfs-host", user="me", destination_path="/path/to/hdfs", stream="mystream"
    )
    assert hdfs_client.path == "/path/to/hdfs/airbyte_json_mystream.jsonl"


@pytest.mark.parametrize("overwrite", [True, False], ids=["overwrite", "append"])
@pytest.mark.parametrize(
    "exists", [True, False], ids=["exists-already", "does-not-exist"]
)
def test_write(overwrite, exists):
    hdfs_client = HDFSClient(
        host="hdfs-host", user="me", destination_path="/foo", stream="bar"
    )

    with mock.patch("destination_hdfs.client.InsecureClient") as InsecureClientMock:
        hdfs_mock = InsecureClientMock.return_value
        hdfs_mock.status.return_value = exists
        hdfs_client.write("sample-data", overwrite)

        # Check that the path is unconditionally made
        hdfs_mock.makedirs.assert_called_with(hdfs_client.destination_path)
        # Check that the file was deleted if it was supposed to exist, but only if the
        # mode was set to overwrite
        if overwrite and exists:
            assert hdfs_mock.delete.called
        else:
            hdfs_mock.delete.assert_not_called()
        # Check that a new empty file was made if it didn't exist, or if overwrite was
        # specified
        if overwrite or not exists:
            hdfs_mock.write.assert_any_call(hdfs_client.path, encoding="utf-8", data="")
        # Lastly, check that a write of the passed data was made!
        hdfs_mock.write.assert_called_with(
            hdfs_client.path, encoding="utf-8", data="sample-data", append=True
        )
