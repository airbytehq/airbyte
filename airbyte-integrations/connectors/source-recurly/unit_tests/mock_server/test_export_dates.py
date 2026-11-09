# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from freezegun import freeze_time

from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from mock_server.helpers import AUTH, BASE, NOW, run


@pytest.mark.parametrize(
    "body,expected",
    [
        (json.dumps({"object": "export_dates", "dates": ["2026-01-13", "2026-01-14"]}), ["2026-01-13", "2026-01-14"]),
        ("", []),
    ],
)
@freeze_time(NOW)
def test_export_dates_emits_one_record_with_available_dates(body, expected):
    with HttpMocker() as mocker:
        mocker.get(HttpRequest(f"{BASE}/export_dates", headers=AUTH), HttpResponse(body))
        output = run("export_dates")
    assert [message.record.data for message in output.records] == [{"dates": expected}]
