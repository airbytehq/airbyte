#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from source_facebook_pages.source import SourceFacebookPages


@pytest.mark.parametrize("error_code", (400, 429, 500))
def test_retries(mocker, requests_mock, error_code):
    mocker.patch("time.sleep")
    requests_mock.get("https://graph.facebook.com/1?fields=access_token&access_token=token", json={"access_token": "access"})
    requests_mock.get("https://graph.facebook.com/v21.0/1", [{"status_code": error_code}, {"json": {"data": {}}}])
    source = SourceFacebookPages()
    stream = source.streams({"page_id": 1, "access_token": "token"})[0]
    for slice_ in stream.stream_slices(sync_mode="full_refresh"):
        list(stream.read_records(sync_mode="full_refresh", stream_slice=slice_))
    assert requests_mock.call_count == 3
