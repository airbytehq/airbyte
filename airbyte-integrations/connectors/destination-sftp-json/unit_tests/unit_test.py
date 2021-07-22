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

from destination_sftp_json.client import SftpClient


expected_paths = pytest.mark.parametrize(
    "config, expected_file_path",
    [
        ({"destination_path": "/destination"}, Path("/destination/data.jsonl")),
        (
            {"destination_path": "/destination", "filename": "new_filename"},
            Path("/destination/new_filename.jsonl"),
        ),
    ],
)


@expected_paths
def test_initialized_parameters(config, expected_file_path):
    sftp = SftpClient(host="sftp-host", username="me", password="supersecret", **config)
    assert sftp.file_path == expected_file_path


@pytest.mark.parametrize(
    "config, expected_uri",
    [
        # Using defaults
        (
            {
                "host": "sftp-host",
                "username": "me",
                "password": "supersecret",
                "destination_path": "/dest",
            },
            "sftp://me:supersecret@sftp-host:22//dest/data.jsonl",
        ),
        # Different filename
        (
            {
                "host": "sftp-host",
                "username": "me",
                "password": "supersecret",
                "destination_path": "/dest",
                "filename": "other-filename",
            },
            "sftp://me:supersecret@sftp-host:22//dest/other-filename.jsonl",
        ),
        # Different port
        (
            {
                "host": "sftp-host",
                "username": "me",
                "password": "supersecret",
                "destination_path": "/dest",
                "port": 33,
            },
            "sftp://me:supersecret@sftp-host:33//dest/data.jsonl",
        ),
    ],
)
def test_get_uri(config, expected_uri):
    sftp = SftpClient(**config)
    assert sftp._get_uri() == expected_uri


@expected_paths
def test_correct_file_deleted(config, expected_file_path):
    sftp = SftpClient(host="sftp-host", username="me", password="supersecret", **config)
    with mock.patch("paramiko.SSHClient") as SSHClient:
        sftp_mock = SSHClient.return_value.__enter__.return_value.open_sftp.return_value
        sftp.delete()
        sftp_mock.remove.assert_called_with(str(expected_file_path))
