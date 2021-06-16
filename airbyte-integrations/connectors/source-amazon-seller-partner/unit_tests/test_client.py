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

import abc
from datetime import datetime
from typing import Mapping

from airbyte_cdk.logger import AirbyteLogger
from dateutil.relativedelta import relativedelta
from source_amazon_seller_partner.client import BaseClient

SP_CREDENTIALS = {
    "refresh_token": "ABC",
    "lwa_app_id": "lwa_app_id",
    "lwa_client_secret": "lwa_client_secret",
    "aws_access_key": "aws_access_key",
    "aws_secret_key": "aws_secret_key",
    "role_arn": "role_arn",
    "start_date": "start_date",
    "marketplace": "USA",
}

GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL = "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL"
ORDERS = "Orders"
_ENTITIES = [GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL, ORDERS]

MARKETPLACE = "India"
ORDERS_RESPONSE = [{"orderId": 1}]


class MockAmazonClient:
    COUNT = 1

    def __init__(self, credentials, marketplace):
        self.credentials = credentials
        self.marketplace = marketplace

    def fetch_orders(updated_after, page_count, next_token=None):
        return ORDERS_RESPONSE

    @abc.abstractmethod
    def get_report(self, reportId):
        return


class AmazonSuccess(MockAmazonClient):
    def get_report(self, reportId):
        if self.COUNT == 3:
            return {"processingStatus": "DONE", "reportDocumentId": 1}
        else:
            self.COUNT = self.COUNT + 1
            return {"processingStatus": "IN_PROGRESS"}


class AmazonCancelled(MockAmazonClient):
    def get_report(self, reportId):
        if self.COUNT == 3:
            return {"processingStatus": "CANCELLED"}
        else:
            self.COUNT = self.COUNT + 1
            return {"processingStatus": "IN_PROGRESS"}


def get_base_client(config: Mapping):
    return BaseClient(**config)


def test_wait_for_report(mocker):
    reportId = "123"

    amazon_client = AmazonCancelled(credentials={}, marketplace="USA")
    wait_response = BaseClient._wait_for_report(AirbyteLogger(), amazon_client, reportId)

    assert wait_response == (False, None)

    amazon_client = AmazonSuccess(credentials={}, marketplace="USA")

    wait_response = BaseClient._wait_for_report(AirbyteLogger(), amazon_client, reportId)
    assert wait_response == (True, 1)


def test_check_connection(mocker):
    mocker.patch("source_amazon_seller_partner.client.AmazonClient", return_value=MockAmazonClient)
    base_client = get_base_client(SP_CREDENTIALS)

    assert ORDERS_RESPONSE == base_client.check_connection()


def test_get_records():
    data = {"document": "name\ttest\nairbyte\t1"}
    base_client = get_base_client(SP_CREDENTIALS)

    assert [{"name": "airbyte", "test": "1"}] == base_client._get_records(data)


def test_apply_conversion_window():
    current_date = "2021-03-04"
    base_client = get_base_client(SP_CREDENTIALS)

    assert "2021-02-18" == base_client._apply_conversion_window(current_date)


def test_convert_array_into_dict():
    headers = ["name", "test"]
    records = ["airbyte\t1"]
    assert [{"name": "airbyte", "test": "1"}] == BaseClient._convert_array_into_dict(headers, records)


def test_increase_date_by_month():
    current_date = "2021-03-04"
    assert "2021-04-04" == BaseClient._increase_date_by_month(current_date)


def fmt_date(date):
    return datetime.strftime(date, "%Y-%m-%d")


def test_get_date_parameters():
    # If the start date is more than one month ago then we expect a full 30 day increment
    now = datetime.today()
    two_months_ago = fmt_date(now - relativedelta(months=2))
    one_month_ago = fmt_date(now - relativedelta(months=1))
    assert (two_months_ago, one_month_ago) == BaseClient._get_date_parameters(two_months_ago)

    # If the start date is less than one month ago we expect to advance no later than today
    one_week_ago = fmt_date(now - relativedelta(weeks=1))
    yesterday = fmt_date(now - relativedelta(days=1))
    assert (one_week_ago, yesterday) == BaseClient._get_date_parameters(one_week_ago)


def test_get_cursor_or_none():
    state = {"stream_name": {"update-date": "2021-03-04"}}
    stream_name = "stream_name"
    cursor_name = "update-date"
    assert "2021-03-04" == BaseClient._get_cursor_or_none(state, stream_name, cursor_name)
    state = {"stream_name-2": {"update-date": "2021-03-04"}}
    assert None is BaseClient._get_cursor_or_none(state, stream_name, cursor_name)
