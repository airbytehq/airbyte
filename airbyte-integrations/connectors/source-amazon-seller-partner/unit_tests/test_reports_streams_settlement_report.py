#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest
from airbyte_cdk.models import SyncMode
from source_amazon_seller_partner.streams import FlatFileSettlementV2Reports

START_DATE_1 = "2022-05-25T00:00:00Z"
END_DATE_1 = "2022-05-26T00:00:00Z"


@pytest.fixture
def settlement_reports_stream():
    def _internal(start_date: str = START_DATE_1, end_date: str = END_DATE_1):
        stream = FlatFileSettlementV2Reports(
            stream_name="FlatFileSettlementV2Reports",
            url_base="https://test.url",
            replication_start_date=start_date,
            replication_end_date=end_date,
            marketplace_id="id",
            authenticator=None,
            period_in_days=0,
            report_options=None,
        )
        return stream

    return _internal


def test_stream_slices(requests_mock, settlement_reports_stream):
    requests_mock.register_uri(
        "POST",
        "https://api.amazon.com/auth/o2/token",
        status_code=200,
        json={"access_token": "access_token", "expires_in": "3600"},
    )
    requests_mock.register_uri(
        "GET",
        "https://test.url/reports/2021-06-30/reports",
        status_code=200,
        json={"reports": [{"reportId": "reportId 1"}, {"reportId": "reportId 2"}]},
    )

    stream = settlement_reports_stream()
    assert list(stream.stream_slices(sync_mode=SyncMode.full_refresh)) == [{"report_id": "reportId 1"}, {"report_id": "reportId 2"}]
