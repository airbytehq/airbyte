#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
import requests
from airbyte_cdk.models import SyncMode
from source_amazon_seller_partner.auth import AWSSignature
from source_amazon_seller_partner.streams import FlatFileSettlementV2Reports

START_DATE_1 = "2022-05-25T00:00:00Z"
END_DATE_1 = "2022-05-26T00:00:00Z"

generated_reports_from_amazon = {
    "payload": [
        {
            "createdTime": "2022-07-08T10:39:31+00:00",
            "dataEndTime": "2022-07-08T09:59:21+00:00",
            "dataStartTime": "2022-06-27T08:01:32+00:00",
            "marketplaceIds": [
                "A1F83G8C2ARO7P",
                "A1PA6795UKMFR9",
                "A13V1IB3VIYZZH",
                "AZMDEXL2RVFNN",
                "A38D8NSA03LJTC",
                "A1ZFFQZ3HTUKT9",
                "APJ6JRA9NG5V4",
                "A1RKKUPIHCS9HS",
                "A62U237T8HV6N",
                "AFQLKURYRPEL8",
                "A1NYP31CE519TD",
                "A1805IZSGTT6HS",
                "A33AVAJ2PDY3EV",
                "AMEN7PMS3EDWL",
                "A2NODRKZP88ZB9",
                "A1C3SOZRARQ6R3",
            ],
            "processingEndTime": "2022-07-08T10:39:31+00:00",
            "processingStartTime": "2022-07-08T10:39:31+00:00",
            "processingStatus": "DONE",
            "reportDocumentId": "amzn1.spdoc.1.3.0fcde1b1-a35e-4fe1-b077-38e0e9f65d63.T1SN9707N5X5IQ.0000",
            "reportId": "85968019100",
            "reportType": "GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE",
        },
        {
            "createdTime": "2022-07-06T09:12:07+00:00",
            "dataEndTime": "2022-07-06T08:38:16+00:00",
            "dataStartTime": "2022-06-22T08:38:16+00:00",
            "marketplaceIds": [
                "A1F83G8C2ARO7P",
                "A1PA6795UKMFR9",
                "A13V1IB3VIYZZH",
                "AZMDEXL2RVFNN",
                "A38D8NSA03LJTC",
                "A1ZFFQZ3HTUKT9",
                "APJ6JRA9NG5V4",
                "A1RKKUPIHCS9HS",
                "A62U237T8HV6N",
                "AFQLKURYRPEL8",
                "A1NYP31CE519TD",
                "A1805IZSGTT6HS",
                "A33AVAJ2PDY3EV",
                "AMEN7PMS3EDWL",
                "A2NODRKZP88ZB9",
                "A1C3SOZRARQ6R3",
            ],
            "processingEndTime": "2022-07-06T09:12:07+00:00",
            "processingStartTime": "2022-07-06T09:12:07+00:00",
            "processingStatus": "DONE",
            "reportDocumentId": "amzn1.spdoc.1.3.f7f43990-7c58-40f2-a93f-565b79a88269.T3OS2416I1AAXM.0000",
            "reportId": "85948019111",
            "reportType": "GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE",
        },
    ]
}


@pytest.fixture
def settlement_reports_stream():
    def _internal(start_date: str = START_DATE_1, end_date: str = END_DATE_1):
        aws_signature = AWSSignature(
            service="execute-api",
            aws_access_key_id="AccessKeyId",
            aws_secret_access_key="SecretAccessKey",
            aws_session_token="SessionToken",
            region="US",
        )
        stream = FlatFileSettlementV2Reports(
            url_base="https://test.url",
            aws_signature=aws_signature,
            replication_start_date=start_date,
            replication_end_date=end_date,
            marketplace_id="id",
            authenticator=None,
            period_in_days=0,
            report_options=None,
            max_wait_seconds=500,
        )
        return stream

    return _internal


def test_stream_slices_method(mocker, settlement_reports_stream):
    response = requests.Response()
    mocker.patch.object(response, "json", return_value=generated_reports_from_amazon)

    data = response.json().get("payload", list())

    slices = [{"report_id": e.get("reportId")} for e in data]

    for i in range(len(slices)):
        report = settlement_reports_stream()._create_report(sync_mode=SyncMode.full_refresh, stream_slice=slices[i])
        assert report.get("reportId") == generated_reports_from_amazon.get("payload")[i].get("reportId")
