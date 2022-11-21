#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from destination_sftp_csv.client import SFTPClient

def client() -> SFTPClient:
    return SFTPClient(host="sample,host", username="sample-username", password="sample-password", destination_path="/sample/path", port=22)

def test_get_path():
    path = client()._get_path("mystream")
    assert path == "/sample/path/airbyte_mystream.csv"
