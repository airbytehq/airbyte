#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
import requests
from airbyte_cdk.models import SyncMode
from source_amplitude.api import Events


class MockRequest:
    def __init__(self, status_code):
        self.status_code = status_code


def test_incremental_http_error_handler(mocker):
    stream = Events(start_date="2021-01-01T00:00:00Z", data_region="Standard Server")
    stream_slice = stream.stream_slices()[0]

    mock_response = MockRequest(404)
    send_request_mocker = mocker.patch.object(stream, "_send_request", side_effect=requests.HTTPError(**{"response": mock_response}))
    with pytest.raises(StopIteration):
        result = next(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice))
        assert result == []

    mock_response = MockRequest(403)
    send_request_mocker.side_effect = requests.HTTPError(**{"response": mock_response})
    with pytest.raises(requests.exceptions.HTTPError):
        next(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice))

    mock_response = MockRequest(400)
    send_request_mocker.side_effect = requests.HTTPError(**{"response": mock_response})
    with pytest.raises(StopIteration):
        result = next(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice))
        assert result == []

    mock_response = MockRequest(504)
    send_request_mocker.side_effect = requests.HTTPError(**{"response": mock_response})
    with pytest.raises(StopIteration):
        result = next(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice))
        assert result == []
