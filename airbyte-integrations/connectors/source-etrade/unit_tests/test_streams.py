#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import pytest
import requests
import requests_mock as req_mock
from source_etrade.streams import (
    Accounts,
    AlertDetails,
    Alerts,
    Balances,
    Orders,
    Portfolio,
    ProductLookup,
    Quotes,
    TransactionDetails,
    Transactions,
)

from unit_tests.conftest import (
    MOCK_ACCOUNTS_RESPONSE,
    MOCK_ALERT_DETAILS_RESPONSE,
    MOCK_ALERTS_RESPONSE,
    MOCK_BALANCE_RESPONSE,
    MOCK_ORDERS_RESPONSE,
    MOCK_PORTFOLIO_RESPONSE,
    MOCK_PRODUCT_LOOKUP_RESPONSE,
    MOCK_QUOTES_RESPONSE,
    MOCK_TRANSACTIONS_RESPONSE,
)


class TestAccounts:
    def test_path(self, auth, base_url):
        stream = Accounts(auth=auth, base_url=base_url)
        assert stream.path() == "accounts/list"

    def test_primary_key(self, auth, base_url):
        stream = Accounts(auth=auth, base_url=base_url)
        assert stream.primary_key == "accountIdKey"

    def test_parse_response(self, auth, base_url):
        stream = Accounts(auth=auth, base_url=base_url)
        with req_mock.Mocker() as m:
            m.get(
                "https://apisb.etrade.com/v1/accounts/list",
                json=MOCK_ACCOUNTS_RESPONSE,
            )
            response = requests.get("https://apisb.etrade.com/v1/accounts/list")
            records = list(stream.parse_response(response))
            assert len(records) == 2
            assert records[0]["accountIdKey"] == "abc123"
            assert records[1]["accountIdKey"] == "def456"

    def test_get_json_schema(self, auth, base_url):
        stream = Accounts(auth=auth, base_url=base_url)
        schema = stream.get_json_schema()
        assert "properties" in schema
        assert "accountIdKey" in schema["properties"]
        assert "accountId" in schema["properties"]


class TestPortfolio:
    def test_path(self, auth, base_url, account_id_keys):
        stream = Portfolio(auth=auth, base_url=base_url, account_id_keys=account_id_keys)
        path = stream.path(stream_slice={"account_id_key": "abc123"})
        assert path == "accounts/abc123/portfolio"

    def test_stream_slices(self, auth, base_url, account_id_keys):
        stream = Portfolio(auth=auth, base_url=base_url, account_id_keys=account_id_keys)
        slices = list(stream.stream_slices())
        assert len(slices) == 2
        assert slices[0] == {"account_id_key": "abc123"}
        assert slices[1] == {"account_id_key": "def456"}

    def test_parse_response(self, auth, base_url, account_id_keys):
        stream = Portfolio(auth=auth, base_url=base_url, account_id_keys=account_id_keys)
        with req_mock.Mocker() as m:
            m.get(
                "https://apisb.etrade.com/v1/accounts/abc123/portfolio",
                json=MOCK_PORTFOLIO_RESPONSE,
            )
            response = requests.get("https://apisb.etrade.com/v1/accounts/abc123/portfolio")
            records = list(stream.parse_response(response, stream_slice={"account_id_key": "abc123"}))
            assert len(records) == 2
            assert records[0]["Product"]["symbol"] == "AAPL"
            assert records[1]["Product"]["symbol"] == "MSFT"
            # Verify accountIdKey is injected
            assert records[0]["accountIdKey"] == "abc123"

    def test_next_page_token_no_more_pages(self, auth, base_url, account_id_keys):
        stream = Portfolio(auth=auth, base_url=base_url, account_id_keys=account_id_keys)
        with req_mock.Mocker() as m:
            m.get(
                "https://apisb.etrade.com/v1/accounts/abc123/portfolio",
                json=MOCK_PORTFOLIO_RESPONSE,
            )
            response = requests.get("https://apisb.etrade.com/v1/accounts/abc123/portfolio")
            token = stream.next_page_token(response)
            assert token is None

    def test_next_page_token_has_more_pages(self, auth, base_url, account_id_keys):
        stream = Portfolio(auth=auth, base_url=base_url, account_id_keys=account_id_keys)
        multi_page_response = {
            "PortfolioResponse": {
                "AccountPortfolio": [{"Position": []}],
                "Totals": {"totalPages": 3, "pageNumber": 0},
            }
        }
        with req_mock.Mocker() as m:
            m.get(
                "https://apisb.etrade.com/v1/accounts/abc123/portfolio",
                json=multi_page_response,
            )
            response = requests.get("https://apisb.etrade.com/v1/accounts/abc123/portfolio")
            token = stream.next_page_token(response)
            assert token == {"pageNumber": 1}

    def test_request_params_with_pagination(self, auth, base_url, account_id_keys):
        stream = Portfolio(auth=auth, base_url=base_url, account_id_keys=account_id_keys)
        params = stream.request_params(next_page_token={"pageNumber": 2})
        assert params["pageNumber"] == 2
        assert params["count"] == 50


class TestBalances:
    def test_path(self, auth, base_url, account_id_keys):
        stream = Balances(auth=auth, base_url=base_url, account_id_keys=account_id_keys)
        path = stream.path(stream_slice={"account_id_key": "abc123"})
        assert path == "accounts/abc123/balance"

    def test_request_params(self, auth, base_url, account_id_keys):
        stream = Balances(auth=auth, base_url=base_url, account_id_keys=account_id_keys)
        params = stream.request_params()
        assert params["instType"] == "BROKERAGE"
        assert params["realTimeNAV"] == "true"

    def test_parse_response(self, auth, base_url, account_id_keys):
        stream = Balances(auth=auth, base_url=base_url, account_id_keys=account_id_keys)
        with req_mock.Mocker() as m:
            m.get(
                "https://apisb.etrade.com/v1/accounts/abc123/balance",
                json=MOCK_BALANCE_RESPONSE,
            )
            response = requests.get("https://apisb.etrade.com/v1/accounts/abc123/balance")
            records = list(stream.parse_response(response, stream_slice={"account_id_key": "abc123"}))
            assert len(records) == 1
            assert records[0]["accountId"] == "12345678"
            assert records[0]["accountIdKey"] == "abc123"
            assert records[0]["Computed"]["cashAvailableForInvestment"] == 10000.0


class TestTransactions:
    def test_path(self, auth, base_url, account_id_keys):
        stream = Transactions(auth=auth, base_url=base_url, account_id_keys=account_id_keys, start_date="2024-01-01")
        path = stream.path(stream_slice={"account_id_key": "abc123"})
        assert path == "accounts/abc123/transactions"

    def test_cursor_field(self, auth, base_url, account_id_keys):
        stream = Transactions(auth=auth, base_url=base_url, account_id_keys=account_id_keys, start_date="2024-01-01")
        assert stream.cursor_field == "transactionDate"

    def test_parse_response(self, auth, base_url, account_id_keys):
        stream = Transactions(auth=auth, base_url=base_url, account_id_keys=account_id_keys, start_date="2024-01-01")
        with req_mock.Mocker() as m:
            m.get(
                "https://apisb.etrade.com/v1/accounts/abc123/transactions",
                json=MOCK_TRANSACTIONS_RESPONSE,
            )
            response = requests.get("https://apisb.etrade.com/v1/accounts/abc123/transactions")
            records = list(stream.parse_response(response, stream_slice={"account_id_key": "abc123"}))
            assert len(records) == 2
            assert records[0]["transactionId"] == 2001
            assert records[0]["accountIdKey"] == "abc123"
            assert records[1]["transactionType"] == "DIVIDEND"

    def test_next_page_token_no_marker(self, auth, base_url, account_id_keys):
        stream = Transactions(auth=auth, base_url=base_url, account_id_keys=account_id_keys, start_date="2024-01-01")
        with req_mock.Mocker() as m:
            m.get(
                "https://apisb.etrade.com/v1/accounts/abc123/transactions",
                json=MOCK_TRANSACTIONS_RESPONSE,
            )
            response = requests.get("https://apisb.etrade.com/v1/accounts/abc123/transactions")
            token = stream.next_page_token(response)
            assert token is None

    def test_next_page_token_with_marker(self, auth, base_url, account_id_keys):
        stream = Transactions(auth=auth, base_url=base_url, account_id_keys=account_id_keys, start_date="2024-01-01")
        paginated_response = {
            "TransactionListResponse": {
                "Transaction": [{"transactionId": 1}],
                "marker": "next_page_marker",
            }
        }
        with req_mock.Mocker() as m:
            m.get(
                "https://apisb.etrade.com/v1/accounts/abc123/transactions",
                json=paginated_response,
            )
            response = requests.get("https://apisb.etrade.com/v1/accounts/abc123/transactions")
            token = stream.next_page_token(response)
            assert token == {"marker": "next_page_marker"}

    def test_request_params(self, auth, base_url, account_id_keys):
        stream = Transactions(auth=auth, base_url=base_url, account_id_keys=account_id_keys, start_date="2024-01-01")
        params = stream.request_params(stream_slice={"account_id_key": "abc123", "start_date": "2024-01-01"})
        assert params["startDate"] == "01012024"
        assert params["sortOrder"] == "ASC"
        assert params["count"] == 50

    def test_get_updated_state(self, auth, base_url, account_id_keys):
        stream = Transactions(auth=auth, base_url=base_url, account_id_keys=account_id_keys, start_date="2024-01-01")
        # Unix timestamp for 2024-01-01
        record = {"accountIdKey": "abc123", "transactionDate": 1704067200000}
        state = stream.get_updated_state({}, record)
        assert "abc123" in state
        assert state["abc123"]["transactionDate"] == "2024-01-01"

    def test_stream_slices(self, auth, base_url, account_id_keys):
        stream = Transactions(auth=auth, base_url=base_url, account_id_keys=account_id_keys, start_date="2024-01-01")
        slices = list(stream.stream_slices())
        assert len(slices) == 2
        assert slices[0]["account_id_key"] == "abc123"
        assert slices[0]["start_date"] == "2024-01-01"


class TestOrders:
    def test_path(self, auth, base_url, account_id_keys):
        stream = Orders(auth=auth, base_url=base_url, account_id_keys=account_id_keys, start_date="2024-01-01")
        path = stream.path(stream_slice={"account_id_key": "abc123"})
        assert path == "accounts/abc123/orders"

    def test_cursor_field(self, auth, base_url, account_id_keys):
        stream = Orders(auth=auth, base_url=base_url, account_id_keys=account_id_keys, start_date="2024-01-01")
        assert stream.cursor_field == "orderPlacedTime"

    def test_parse_response(self, auth, base_url, account_id_keys):
        stream = Orders(auth=auth, base_url=base_url, account_id_keys=account_id_keys, start_date="2024-01-01")
        with req_mock.Mocker() as m:
            m.get(
                "https://apisb.etrade.com/v1/accounts/abc123/orders",
                json=MOCK_ORDERS_RESPONSE,
            )
            response = requests.get("https://apisb.etrade.com/v1/accounts/abc123/orders")
            records = list(stream.parse_response(response, stream_slice={"account_id_key": "abc123"}))
            assert len(records) == 1
            assert records[0]["orderId"] == 3001
            assert records[0]["accountIdKey"] == "abc123"

    def test_request_params(self, auth, base_url, account_id_keys):
        stream = Orders(auth=auth, base_url=base_url, account_id_keys=account_id_keys, start_date="2024-01-01")
        params = stream.request_params(stream_slice={"account_id_key": "abc123", "start_date": "2024-01-01"})
        assert params["fromDate"] == "01012024"
        assert params["count"] == 100


class TestQuotes:
    def test_path(self, auth, base_url, account_id_keys):
        stream = Quotes(auth=auth, base_url=base_url, account_id_keys=account_id_keys)
        path = stream.path(stream_slice={"symbols": "AAPL,MSFT"})
        assert path == "market/quote/AAPL,MSFT"

    def test_parse_response(self, auth, base_url, account_id_keys):
        stream = Quotes(auth=auth, base_url=base_url, account_id_keys=account_id_keys)
        with req_mock.Mocker() as m:
            m.get(
                "https://apisb.etrade.com/v1/market/quote/AAPL",
                json=MOCK_QUOTES_RESPONSE,
            )
            response = requests.get("https://apisb.etrade.com/v1/market/quote/AAPL")
            records = list(stream.parse_response(response))
            assert len(records) == 1
            assert records[0]["Product"]["symbol"] == "AAPL"
            assert records[0]["All"]["lastTrade"] == 175.45


class TestAlerts:
    def test_path(self, auth, base_url):
        stream = Alerts(auth=auth, base_url=base_url)
        assert stream.path() == "user/alerts"

    def test_primary_key(self, auth, base_url):
        stream = Alerts(auth=auth, base_url=base_url)
        assert stream.primary_key == "id"

    def test_request_params(self, auth, base_url):
        stream = Alerts(auth=auth, base_url=base_url)
        params = stream.request_params()
        assert params["count"] == 300
        assert params["direction"] == "DESC"

    def test_parse_response(self, auth, base_url):
        stream = Alerts(auth=auth, base_url=base_url)
        with req_mock.Mocker() as m:
            m.get(
                "https://apisb.etrade.com/v1/user/alerts",
                json=MOCK_ALERTS_RESPONSE,
            )
            response = requests.get("https://apisb.etrade.com/v1/user/alerts")
            records = list(stream.parse_response(response))
            assert len(records) == 2
            assert records[0]["id"] == 4001
            assert records[1]["category"] == "ACCOUNT"


class TestAlertDetails:
    def test_path(self, auth, base_url):
        stream = AlertDetails(auth=auth, base_url=base_url)
        path = stream.path(stream_slice={"alert_id": 4001})
        assert path == "user/alerts/4001"

    def test_parse_response(self, auth, base_url):
        stream = AlertDetails(auth=auth, base_url=base_url)
        with req_mock.Mocker() as m:
            m.get(
                "https://apisb.etrade.com/v1/user/alerts/4001",
                json=MOCK_ALERT_DETAILS_RESPONSE,
            )
            response = requests.get("https://apisb.etrade.com/v1/user/alerts/4001")
            records = list(stream.parse_response(response, stream_slice={"alert_id": 4001}))
            assert len(records) == 1
            assert records[0]["id"] == 4001
            assert "AAPL" in records[0]["msgText"]


class TestProductLookup:
    def test_path(self, auth, base_url):
        stream = ProductLookup(auth=auth, base_url=base_url)
        assert stream.path() == "market/lookup/A"

    def test_parse_response(self, auth, base_url):
        stream = ProductLookup(auth=auth, base_url=base_url)
        with req_mock.Mocker() as m:
            m.get(
                "https://apisb.etrade.com/v1/market/lookup/A",
                json=MOCK_PRODUCT_LOOKUP_RESPONSE,
            )
            response = requests.get("https://apisb.etrade.com/v1/market/lookup/A")
            records = list(stream.parse_response(response))
            assert len(records) == 2
            assert records[0]["symbol"] == "AAPL"
            assert records[1]["symbol"] == "AMZN"


class TestEtradeStreamBase:
    """Test common stream behavior."""

    def test_url_base_sandbox(self, auth):
        stream = Accounts(auth=auth, base_url="https://apisb.etrade.com")
        assert stream.url_base == "https://apisb.etrade.com/v1/"

    def test_url_base_live(self, auth):
        stream = Accounts(auth=auth, base_url="https://api.etrade.com")
        assert stream.url_base == "https://api.etrade.com/v1/"

    def test_request_headers(self, auth, base_url):
        stream = Accounts(auth=auth, base_url=base_url)
        headers = stream.request_headers()
        assert headers["Accept"] == "application/json"

    def test_should_retry_429(self, auth, base_url):
        stream = Accounts(auth=auth, base_url=base_url)
        response = requests.Response()
        response.status_code = 429
        assert stream.should_retry(response) is True

    def test_should_retry_500(self, auth, base_url):
        stream = Accounts(auth=auth, base_url=base_url)
        response = requests.Response()
        response.status_code = 500
        assert stream.should_retry(response) is True

    def test_should_not_retry_400(self, auth, base_url):
        stream = Accounts(auth=auth, base_url=base_url)
        response = requests.Response()
        response.status_code = 400
        assert stream.should_retry(response) is False

    def test_should_not_retry_200(self, auth, base_url):
        stream = Accounts(auth=auth, base_url=base_url)
        response = requests.Response()
        response.status_code = 200
        assert stream.should_retry(response) is False
