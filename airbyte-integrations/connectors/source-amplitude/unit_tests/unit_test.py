#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import airbyte_cdk.models
import pytest
import requests
from source_amplitude.api import Events


class MockRequest:
    def __init__(self, status_code):
        self.status_code = status_code


def test_http_error_handler(mocker):
    stream = Events(start_date="2021-01-01T00:00:00Z")

    mock_response = MockRequest(404)
    send_request_mocker = mocker.patch.object(stream, "_send_request", side_effect=requests.HTTPError(**{"response": mock_response}))
    with pytest.raises(StopIteration):
        result = next(stream.read_records(sync_mode=airbyte_cdk.models.SyncMode.full_refresh))
        assert result == []

    mock_response = MockRequest(403)
    send_request_mocker.side_effect = requests.HTTPError(**{"response": mock_response})
    with pytest.raises(requests.exceptions.HTTPError):
        next(stream.read_records(sync_mode=airbyte_cdk.models.SyncMode.full_refresh))
