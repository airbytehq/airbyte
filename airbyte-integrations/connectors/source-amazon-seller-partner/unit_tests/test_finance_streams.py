#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from unittest import mock

import pendulum
import pytest
import requests
from airbyte_cdk.models import SyncMode
from source_amazon_seller_partner.streams import ListFinancialEventGroups, ListFinancialEvents, RestockInventoryReports

list_financial_event_groups_data = {
    "payload": {
        "FinancialEventGroupList": [
            {
                "FinancialEventGroupId": "id",
                "ProcessingStatus": "Closed",
                "FundTransferStatus": "Succeeded",
                "OriginalTotal": {"CurrencyCode": "CAD", "CurrencyAmount": 1.0},
                "ConvertedTotal": {"CurrencyCode": "USD", "CurrencyAmount": 2.0},
                "FundTransferDate": "2022-05-14T19:24:35Z",
                "TraceId": "1, 2",
                "AccountTail": "181",
                "BeginningBalance": {"CurrencyCode": "CAD", "CurrencyAmount": 0.0},
                "FinancialEventGroupStart": "2022-04-29T19:15:59Z",
                "FinancialEventGroupEnd": "2022-05-13T19:15:59Z",
            }
        ]
    }
}

list_financial_events_data = {
    "payload": {
        "FinancialEvents": {
            "ShipmentEventList": [
                {
                    "AmazonOrderId": "A_ORDER_ID",
                    "SellerOrderId": "S_ORDER_ID",
                    "MarketplaceName": "Amazon.com",
                    "PostedDate": "2022-05-01T01:32:42Z",
                    "ShipmentItemList": [],
                }
            ],
            "RefundEventList": [
                {
                    "AmazonOrderId": "A_ORDER_ID",
                    "SellerOrderId": "S_ORDER_ID",
                    "MarketplaceName": "Amazon.ca",
                    "PostedDate": "2022-05-01T03:05:36Z",
                    "ShipmentItemAdjustmentList": [],
                }
            ],
            "GuaranteeClaimEventList": [],
            "ChargebackEventList": [],
            "PayWithAmazonEventList": [],
            "ServiceProviderCreditEventList": [],
            "RetrochargeEventList": [],
            "RentalTransactionEventList": [],
            "PerformanceBondRefundEventList": [],
            "ProductAdsPaymentEventList": [],
            "ServiceFeeEventList": [],
            "SellerDealPaymentEventList": [],
            "DebtRecoveryEventList": [],
            "LoanServicingEventList": [],
            "AdjustmentEventList": [
                {
                    "AdjustmentType": "XXXX",
                    "PostedDate": "2022-05-01T15:08:00Z",
                    "AdjustmentAmount": {"CurrencyCode": "USD", "CurrencyAmount": 25.35},
                    "AdjustmentItemList": [],
                }
            ],
            "SAFETReimbursementEventList": [],
            "SellerReviewEnrollmentPaymentEventList": [],
            "FBALiquidationEventList": [],
            "CouponPaymentEventList": [],
            "ImagingServicesFeeEventList": [],
            "TaxWithholdingEventList": [],
            "NetworkComminglingTransactionEventList": [],
            "AffordabilityExpenseEventList": [],
            "AffordabilityExpenseReversalEventList": [],
            "RemovalShipmentAdjustmentEventList": [],
            "RemovalShipmentEventList": [],
        }
    }
}

DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

START_DATE_1 = "2022-05-25T00:00:00Z"
END_DATE_1 = "2022-05-26T00:00:00Z"

START_DATE_2 = "2021-01-01T00:00:00Z"
END_DATE_2 = "2022-07-31T00:00:00Z"


@pytest.fixture
def list_financial_event_groups_stream():
    def _internal(start_date: str = START_DATE_1, end_date: str = END_DATE_1):
        stream = ListFinancialEventGroups(
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


@pytest.fixture
def list_financial_events_stream():
    def _internal(start_date: str = START_DATE_1, end_date: str = END_DATE_1):
        stream = ListFinancialEvents(
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


def test_finance_stream_next_token(mocker, list_financial_event_groups_stream):
    response = requests.Response()
    token = "aabbccddeeff"
    expected = {"NextToken": token}
    mocker.patch.object(response, "json", return_value={"payload": expected})
    assert expected == list_financial_event_groups_stream().next_page_token(response)

    mocker.patch.object(response, "json", return_value={"payload": {}})
    if list_financial_event_groups_stream().next_page_token(response) is not None:
        assert False


def test_financial_event_groups_stream_request_params(list_financial_event_groups_stream):
    # test 1
    expected_params = {
        "FinancialEventGroupStartedAfter": START_DATE_1,
        "MaxResultsPerPage": 100,
        "FinancialEventGroupStartedBefore": END_DATE_1,
    }
    assert expected_params == list_financial_event_groups_stream().request_params({}, None)

    # test 2
    token = "aabbccddeeff"
    expected_params = {"NextToken": token}
    assert expected_params == list_financial_event_groups_stream().request_params({}, {"NextToken": token})

    # test 3 - for 180 days limit
    expected_params = {
        "FinancialEventGroupStartedAfter": pendulum.parse(END_DATE_2).subtract(days=180).strftime(DATE_TIME_FORMAT),
        "MaxResultsPerPage": 100,
        "FinancialEventGroupStartedBefore": END_DATE_2,
    }
    assert expected_params == list_financial_event_groups_stream(START_DATE_2, END_DATE_2).request_params({}, None)


def test_financial_event_groups_stream_parse_response(mocker, list_financial_event_groups_stream):
    response = requests.Response()
    mocker.patch.object(response, "json", return_value=list_financial_event_groups_data)

    for record in list_financial_event_groups_stream().parse_response(response, {}):
        assert record == list_financial_event_groups_data.get("payload").get("FinancialEventGroupList")[0]


def test_financial_events_stream_request_params(list_financial_events_stream):
    # test 1
    expected_params = {"PostedAfter": START_DATE_1, "MaxResultsPerPage": 100, "PostedBefore": END_DATE_1}
    assert expected_params == list_financial_events_stream().request_params({}, None)

    # test 2
    token = "aabbccddeeff"
    expected_params = {"NextToken": token}
    assert expected_params == list_financial_events_stream().request_params({}, {"NextToken": token})

    # test 3 - for 180 days limit
    expected_params = {
        "PostedAfter": pendulum.parse(END_DATE_2).subtract(days=180).strftime(DATE_TIME_FORMAT),
        "MaxResultsPerPage": 100,
        "PostedBefore": END_DATE_2,
    }
    assert expected_params == list_financial_events_stream(START_DATE_2, END_DATE_2).request_params({}, None)


def test_financial_events_stream_parse_response(mocker, list_financial_events_stream):
    response = requests.Response()
    mocker.patch.object(response, "json", return_value=list_financial_events_data)

    for record in list_financial_events_stream().parse_response(response, {}):
        assert list_financial_events_data.get("payload").get("FinancialEvents").get("ShipmentEventList") == record.get("ShipmentEventList")
        assert list_financial_events_data.get("payload").get("FinancialEvents").get("RefundEventList") == record.get("RefundEventList")
        assert list_financial_events_data.get("payload").get("FinancialEvents").get("AdjustmentEventList") == record.get(
            "AdjustmentEventList"
        )


def test_reports_read_records_exit_on_backoff(mocker, requests_mock, caplog):
    mocker.patch("time.sleep", lambda x: None)
    requests_mock.post("https://test.url/reports/2021-06-30/reports", status_code=429)

    stream = RestockInventoryReports(
        url_base="https://test.url",
        replication_start_date=START_DATE_1,
        replication_end_date=END_DATE_1,
        marketplace_id="id",
        authenticator=None,
        period_in_days=0,
        report_options=None,
    )
    assert list(stream.read_records(sync_mode=SyncMode.full_refresh)) == []
    assert (
        "The report for stream 'GET_RESTOCK_INVENTORY_RECOMMENDATIONS_REPORT' was cancelled due to several failed retry attempts."
    ) in caplog.messages[-1]


@pytest.mark.parametrize(
    ("response_headers", "expected_backoff_time"),
    (({"x-amzn-RateLimit-Limit": "2"}, 0.5), ({}, 60)),
)
def test_financial_events_stream_backoff_time(list_financial_events_stream, response_headers, expected_backoff_time):
    stream = list_financial_events_stream()
    response_mock = mock.MagicMock()
    response_mock.headers = response_headers
    assert stream.backoff_time(response_mock) == expected_backoff_time
