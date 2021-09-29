#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import patch
import requests

import airbyte_cdk.models
from airbyte_cdk.sources.streams.http import HttpStream

from source_amplitude.api import Events


@patch.object(HttpStream, "read_records")
def raise_error():
    raise requests.exceptions.HTTPError


def test_http_error_handler():
    stream = Events(start_date="2021-01-01T00:00:00Z")
    result = next(stream.read_records(sync_mode=airbyte_cdk.models.SyncMode.full_refresh))
    assert result == []
