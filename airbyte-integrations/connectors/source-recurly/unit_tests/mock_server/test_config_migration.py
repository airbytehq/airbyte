# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from freezegun import freeze_time

from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.helpers import API_KEY, NOW, list_request, page, record, run


@freeze_time(NOW)
def test_dates_saved_before_the_utc_suffix_was_required_are_still_accepted():
    legacy_config = {"api_key": API_KEY, "begin_time": "2026-01-01T00:00:00", "end_time": "2026-01-10T00:00:00"}
    with HttpMocker() as mocker:
        request = list_request("plans", begin="2026-01-01T00:00:00Z", end="2026-01-10T00:00:00Z")
        mocker.get(request, page([record("plan-1", "2026-01-02T00:00:00Z")]))
        output = run("plans", cfg=legacy_config)
        mocker.assert_number_of_calls(request, 1)
    assert [message.record.data["id"] for message in output.records] == ["plan-1"]
    assert output.errors == []
