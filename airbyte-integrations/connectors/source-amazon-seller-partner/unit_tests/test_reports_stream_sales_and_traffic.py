#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from source_amazon_seller_partner.streams import SellerAnalyticsSalesAndTrafficReports

START_DATE_1 = "2023-02-05T00:00:00Z"
END_DATE_1 = "2023-02-07T00:00:00Z"


def test_stream_uses_advanced_options():
    stream = SellerAnalyticsSalesAndTrafficReports(
        url_base="https://test.url",
        replication_start_date=START_DATE_1,
        replication_end_date=END_DATE_1,
        marketplace_id="id",
        authenticator=None,
        period_in_days=0,
        report_options=None,
        advanced_stream_options='{"GET_SALES_AND_TRAFFIC_REPORT":{"availability_sla_days": 3}}',
    )

    assert stream.availability_sla_days == 3
