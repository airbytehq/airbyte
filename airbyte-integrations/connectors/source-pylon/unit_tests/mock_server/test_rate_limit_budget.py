# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest.mock import patch

import pytest
from freezegun import freeze_time

from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.helpers import NOW, error, fixture_record, list_request, page, run


@pytest.mark.parametrize("status", [429, 500])
@freeze_time(NOW)
def test_retryable_response_recovers(status):
    with patch("time.sleep"), patch("airbyte_cdk.sources.streams.call_rate.APIBudget.acquire_call"), HttpMocker() as mocker:
        request = list_request("tags")
        record = fixture_record("tags")
        mocker.get(request, [error(status, headers={"Retry-After": "7"}), page([record])])
        output = run("tags")
        mocker.assert_number_of_calls(request, 2)
    assert output.errors == []
    assert [message.record.data for message in output.records] == [record]
