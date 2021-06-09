#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from datetime import date

from source_amazon_seller_partner.amazon import AmazonClient

SP_CREDENTIALS = {
    "refresh_token": "ABC",
    "lwa_app_id": "lwa_app_id",
    "lwa_client_secret": "lwa_client_secret",
    "aws_access_key": "aws_access_key",
    "aws_secret_key": "aws_secret_key",
    "role_arn": "role_arn",
}

GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL = "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL"
ORDERS = "Orders"
_ENTITIES = [GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL, ORDERS]

MARKETPLACE = "India"

order_response = [{"orderId", 12345}]
request_response = {"requestStatus", True}


class MockOrders:
    def __init__(self, credentials, marketplace):
        self.credentials = credentials
        self.marketplace = marketplace

    def get_orders(LastUpdatedAfter, MaxResultsPerPage, NextToken):
        return Response(data=order_response)


class MockReports:
    def __init__(self, credentials, marketplace):
        self.credentials = credentials
        self.marketplace = marketplace

    def create_report(reportType, dataStartTime, dataEndTime):
        return Response(data=request_response)

    def get_report(report_id):
        return Response(data=request_response)

    def get_report_document(report_id, decrypt):
        return Response(data=request_response)


class Response:
    def __init__(self, data):
        self.payload = data


def test_get_entities():
    _amazon_client = AmazonClient(credentials=SP_CREDENTIALS, marketplace=MARKETPLACE)

    assert _ENTITIES == _amazon_client.get_entities()


def test_is_report():
    _amazon_client = AmazonClient(credentials=SP_CREDENTIALS, marketplace=MARKETPLACE)
    assert _amazon_client.is_report(GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL)
    assert not _amazon_client.is_report(ORDERS)


def test_get_cursor_for_stream():
    _amazon_client = AmazonClient(credentials=SP_CREDENTIALS, marketplace=MARKETPLACE)
    Orders_cursor = "LastUpdateDate"
    GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL_cursor = "purchase-date"

    assert Orders_cursor == _amazon_client.get_cursor_for_stream(ORDERS)
    assert GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL_cursor == _amazon_client.get_cursor_for_stream(
        GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL
    )


def test_fetch_orders(mocker):

    get_order_spy = mocker.spy(MockOrders, "get_orders")
    mocker.patch("source_amazon_seller_partner.amazon.Orders", return_value=MockOrders)

    _amazon_client = AmazonClient(credentials=SP_CREDENTIALS, marketplace=MARKETPLACE)
    updated_after = date.today().isoformat()
    page_count = 100
    response = _amazon_client.fetch_orders(updated_after=updated_after, page_size=page_count, next_token=None)

    get_order_spy.assert_called_once_with(updated_after, page_count, None)
    assert response == order_response


def test_request_report(mocker):

    request_report_spy = mocker.spy(MockReports, "create_report")

    mocker.patch("source_amazon_seller_partner.amazon.Reports", return_value=MockReports)

    _amazon_client = AmazonClient(credentials=SP_CREDENTIALS, marketplace=MARKETPLACE)
    date_start = date.today().isoformat()
    response = _amazon_client.request_report(
        report_type=GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL, data_start_time=date_start, data_end_time=date_start
    )

    request_report_spy.assert_called_once_with(GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL, date_start, date_start)
    assert response == request_response


def test_get_report(mocker):
    get_report_spy = mocker.spy(MockReports, "get_report")

    mocker.patch("source_amazon_seller_partner.amazon.Reports", return_value=MockReports)

    _amazon_client = AmazonClient(credentials=SP_CREDENTIALS, marketplace=MARKETPLACE)
    report_id = 1
    response = _amazon_client.get_report(report_id=report_id)

    get_report_spy.assert_called_once_with(report_id)
    assert response == request_response


def test_get_report_document(mocker):
    get_report_document_spy = mocker.spy(MockReports, "get_report_document")

    mocker.patch("source_amazon_seller_partner.amazon.Reports", return_value=MockReports)

    _amazon_client = AmazonClient(credentials=SP_CREDENTIALS, marketplace=MARKETPLACE)
    report_document_id = 1
    response = _amazon_client.get_report_document(report_document_id=report_document_id)

    get_report_document_spy.assert_called_once_with(report_document_id, True)
    assert response == request_response
