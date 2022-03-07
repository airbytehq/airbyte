#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
import requests
from source_chargify.source import ChargifyStream, Customers, Subscriptions


@pytest.fixture()
def ChargifyStreamInstance(mocker) -> ChargifyStream:

    mocker.patch.object(ChargifyStream, "path", "v0/example_endpoint")
    mocker.patch.object(ChargifyStream, "primary_key", "test_primary_key")
    mocker.patch.object(ChargifyStream, "__abstractmethods__", set())

    return ChargifyStream(
        authenticator=MagicMock(),
        subdomain="test",
        per_page=200,
        page=1
    )


@pytest.fixture()
def CustomerStreamInstance(mocker) -> Customers:

    mocker.patch.object(Customers, "path", "v0/example_endpoint")
    mocker.patch.object(Customers, "primary_key", "test_primary_key")
    mocker.patch.object(Customers, "__abstractmethods__", set())

    return Customers(
        authenticator=MagicMock(),
        subdomain="test",
        per_page=200,
        page=1
    )

@pytest.fixture()
def SubscriptionsStreamInstance(mocker) -> Subscriptions:

    mocker.patch.object(Subscriptions, "path", "v0/example_endpoint")
    mocker.patch.object(Subscriptions, "primary_key", "test_primary_key")
    mocker.patch.object(Subscriptions, "__abstractmethods__", set())

    return Subscriptions(
        authenticator=MagicMock(),
        subdomain="test",
        per_page=200,
        page=1
    )

@pytest.mark.parametrize("subdomain, page, per_page", [('test', 1, 200),('test1',2,200),('test2', 3,200)])
def test_stream_config(subdomain, page, per_page, mocker):

    mocker.patch.object(ChargifyStream, "path", "v0/example_endpoint")
    mocker.patch.object(ChargifyStream, "primary_key", "test_primary_key")
    mocker.patch.object(ChargifyStream, "__abstractmethods__", set())
    
    stream: ChargifyStream = ChargifyStream(
        subdomain=subdomain,
        per_page=per_page,
        page=page
    )
    assert stream._subdomain == subdomain
    assert stream._page == page
    assert stream._per_page == per_page
    assert stream.url_base == f'https://{subdomain}.chargify.com'
    assert stream.is_first_requests == True

    customers_stream: Customers = Customers(subdomain=subdomain, page=page, per_page=per_page)
    assert customers_stream.path() == f'customers.json'
    assert customers_stream.primary_key == 'id'
    assert stream.url_base == f'https://{subdomain}.chargify.com'
    assert stream.is_first_requests == True

    subscriptions_stream: Subscriptions = Subscriptions(subdomain=subdomain, page=page, per_page=per_page)
    assert subscriptions_stream.path() == f'subscriptions.json'
    assert subscriptions_stream.primary_key == 'id'
    assert stream.url_base == f'https://{subdomain}.chargify.com'
    assert stream.is_first_requests == True

def test_next_page_token(ChargifyStreamInstance: ChargifyStream):
    response = requests.Response()
    response.url = 'https://test.chargify.com/subscriptions.json?page=1&per_page=200'
    response.json = MagicMock()
    response.json.return_value = [{'id': 1}, {'id': 2}]

    token_params = ChargifyStreamInstance.next_page_token(response=response)

    assert token_params == {'page': 2, 'per_page': '200'}

    response = requests.Response()
    response.url = 'https://test.chargify.com/subscriptions.json?page=1&per_page=200'
    response.json = MagicMock()
    response.json.return_value = {}

    token_params = ChargifyStreamInstance.next_page_token(response=response)

    assert token_params == None


def test_requests_params(ChargifyStreamInstance: ChargifyStream):

    params = ChargifyStreamInstance.request_params(stream_state={},next_page_token=None)

    assert params == {'page': 1, 'per_page': 200}

    setattr(ChargifyStreamInstance.__class__, 'is_first_requests', False)
    
    params = ChargifyStreamInstance.request_params(stream_state={}, next_page_token=None)

    assert params == None

    params = ChargifyStreamInstance.request_params(stream_state={}, next_page_token={'page': 2, 'per_page': 200})

    assert params == {'page': 2, 'per_page': 200}

def test_parse_subscriptions_response(SubscriptionsStreamInstance: Subscriptions):

    response = MagicMock()
    response.json.return_value = [{"subscription": {"id": 0,"state": "string","balance_in_cents": 0}}, {"subscription": {"id":2,"state": "string","balance_in_cents": 1000}},{"subscription": {"id":3,"state": "string","balance_in_cents": 100}}]

    response = list(SubscriptionsStreamInstance.parse_response(response=response))

    assert len(response) == 3
    assert response[0] == {"id": 0,"state": "string","balance_in_cents": 0}
    assert response[1] == {"id":2,"state": "string","balance_in_cents": 1000}
    assert response[2] == {"id":3,"state": "string","balance_in_cents": 100}

def test_parse_customers_response(CustomerStreamInstance: Customers):

    response = MagicMock()
    response.json.return_value = [{"customer": {"id": 0,"state": "string","balance_in_cents": 0}}, {"customer": {"id":2,"state": "string","balance_in_cents": 1000}},{"customer": {"id":3,"state": "string","balance_in_cents": 100}}]

    response = list(CustomerStreamInstance.parse_response(response=response))

    assert len(response) == 3
    assert response[0] == {"id": 0,"state": "string","balance_in_cents": 0}
    assert response[1] == {"id":2,"state": "string","balance_in_cents": 1000}
    assert response[2] == {"id":3,"state": "string","balance_in_cents": 100}
