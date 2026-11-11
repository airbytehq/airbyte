# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from freezegun import freeze_time

from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.helpers import NOW, list_request, page, record, run


@freeze_time(NOW)
def test_reads_billing_infos_for_every_parent_account():
    with HttpMocker() as mocker:
        mocker.get(
            list_request("accounts"),
            page([record("account-1", "2026-01-02T00:00:00Z"), record("account-2", "2026-01-03T00:00:00Z")]),
        )
        mocker.get(
            list_request("accounts/account-1/billing_infos"),
            page([record("billing-1", "2026-01-02T00:00:00Z", account_id="account-1")]),
        )
        empty_partition = list_request("accounts/account-2/billing_infos")
        mocker.get(empty_partition, page([]))
        output = run("billing_infos")
        mocker.assert_number_of_calls(empty_partition, 1)
    assert [message.record.data["id"] for message in output.records] == ["billing-1"]
    assert output.errors == []
