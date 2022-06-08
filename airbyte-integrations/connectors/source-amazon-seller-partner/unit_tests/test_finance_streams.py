#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
import requests
from source_amazon_seller_partner.auth import AWSSignature
from source_amazon_seller_partner.streams import ListFinancialEventGroups, ListFinancialEvents

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


@pytest.fixture
def list_financial_event_groups_stream():
    aws_signature = AWSSignature(
        service="execute-api",
        aws_access_key_id="AccessKeyId",
        aws_secret_access_key="SecretAccessKey",
        aws_session_token="SessionToken",
        region="US",
    )
    stream = ListFinancialEventGroups(
        url_base="https://test.url",
        aws_signature=aws_signature,
        replication_start_date="2022-05-25T00:00:00Z",
        replication_end_date="2022-05-26T00:00:00Z",
        marketplace_id="id",
        authenticator=None,
        period_in_days=0,
        report_options=None,
        max_wait_seconds=500,
    )
    return stream


@pytest.fixture
def list_financial_events_stream():
    aws_signature = AWSSignature(
        service="execute-api",
        aws_access_key_id="AccessKeyId",
        aws_secret_access_key="SecretAccessKey",
        aws_session_token="SessionToken",
        region="US",
    )
    stream = ListFinancialEvents(
        url_base="https://test.url",
        aws_signature=aws_signature,
        replication_start_date="2022-05-25T00:00:00Z",
        replication_end_date="2022-05-26T00:00:00Z",
        marketplace_id="id",
        authenticator=None,
        period_in_days=0,
        report_options=None,
        max_wait_seconds=500,
    )
    return stream


def test_finance_stream_next_token(mocker, list_financial_event_groups_stream):
    response = requests.Response()
    token = "aabbccddeeff"
    expected = {"NextToken": token}
    mocker.patch.object(response, "json", return_value={"payload": expected})
    assert expected == list_financial_event_groups_stream.next_page_token(response)

    mocker.patch.object(response, "json", return_value={"payload": {}})
    if list_financial_event_groups_stream.next_page_token(response) is not None:
        assert False


def test_financial_event_groups_stream_request_params(list_financial_event_groups_stream):
    params = {
        "FinancialEventGroupStartedAfter": "2022-05-25T00:00:00Z",
        "MaxResultsPerPage": 100,
        "FinancialEventGroupStartedBefore": "2022-05-26T00:00:00Z",
    }
    assert params == list_financial_event_groups_stream.request_params({}, None)

    token = "aabbccddeeff"
    params = {"NextToken": token}
    assert params == list_financial_event_groups_stream.request_params({}, {"NextToken": token})


def test_financial_event_groups_stream_parse_response(mocker, list_financial_event_groups_stream):
    response = requests.Response()
    mocker.patch.object(response, "json", return_value=list_financial_event_groups_data)

    for record in list_financial_event_groups_stream.parse_response(response, {}):
        assert record == list_financial_event_groups_data.get("payload").get("FinancialEventGroupList")[0]


def test_financial_events_stream_request_params(list_financial_events_stream):
    params = {"PostedAfter": "2022-05-25T00:00:00Z", "MaxResultsPerPage": 100, "PostedBefore": "2022-05-26T00:00:00Z"}
    assert params == list_financial_events_stream.request_params({}, None)

    token = "aabbccddeeff"
    params = {"NextToken": token}
    assert params == list_financial_events_stream.request_params({}, {"NextToken": token})


def test_financial_events_stream_parse_response(mocker, list_financial_events_stream):
    response = requests.Response()
    mocker.patch.object(response, "json", return_value=list_financial_events_data)

    for record in list_financial_events_stream.parse_response(response, {}):
        assert list_financial_events_data.get("payload").get("FinancialEvents").get("ShipmentEventList") == record.get("ShipmentEventList")
        assert list_financial_events_data.get("payload").get("FinancialEvents").get("RefundEventList") == record.get("RefundEventList")
        assert list_financial_events_data.get("payload").get("FinancialEvents").get("AdjustmentEventList") == record.get(
            "AdjustmentEventList"
        )
