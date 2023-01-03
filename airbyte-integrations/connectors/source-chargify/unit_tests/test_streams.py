#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
        domain="test",
    )


@pytest.fixture()
def CustomerStreamInstance(mocker) -> Customers:

    mocker.patch.object(Customers, "path", "v0/example_endpoint")
    mocker.patch.object(Customers, "primary_key", "test_primary_key")
    mocker.patch.object(Customers, "__abstractmethods__", set())

    return Customers(authenticator=MagicMock(), domain="test")


@pytest.fixture()
def SubscriptionsStreamInstance(mocker) -> Subscriptions:

    mocker.patch.object(Subscriptions, "path", "v0/example_endpoint")
    mocker.patch.object(Subscriptions, "primary_key", "test_primary_key")
    mocker.patch.object(Subscriptions, "__abstractmethods__", set())

    return Subscriptions(
        authenticator=MagicMock(),
        domain="test",
    )


@pytest.mark.parametrize("domain", [("test"), ("test1"), ("test2")])
def test_stream_config(domain, mocker):

    mocker.patch.object(ChargifyStream, "path", "v0/example_endpoint")
    mocker.patch.object(ChargifyStream, "primary_key", "test_primary_key")
    mocker.patch.object(ChargifyStream, "__abstractmethods__", set())

    stream: ChargifyStream = ChargifyStream(
        domain=domain,
    )
    assert stream._domain == domain

    customers_stream: Customers = Customers(domain=domain)
    assert customers_stream.path() == "customers.json"
    assert customers_stream.primary_key == "id"

    subscriptions_stream: Subscriptions = Subscriptions(domain=domain)
    assert subscriptions_stream.path() == "subscriptions.json"
    assert subscriptions_stream.primary_key == "id"


def test_next_page_token(ChargifyStreamInstance: ChargifyStream):
    response = requests.Response()
    response.url = "https://test.chargify.com/subscriptions.json?page=1&per_page=2"
    response.json = MagicMock()
    response.json.return_value = [{"id": 1}, {"id": 2}]

    ChargifyStream.PER_PAGE = 2

    token_params = ChargifyStreamInstance.next_page_token(response=response)

    assert token_params == {"page": 2, "per_page": "2"}

    response = requests.Response()
    response.url = "https://test.chargify.com/subscriptions.json?page=1&per_page=2"
    response.json = MagicMock()
    response.json.return_value = {}

    token_params = ChargifyStreamInstance.next_page_token(response=response)

    assert token_params is None


def test_requests_params(ChargifyStreamInstance: ChargifyStream):

    ChargifyStream.PER_PAGE = 200

    params = ChargifyStreamInstance.request_params(stream_state={}, next_page_token=None)

    assert params == {"page": 1, "per_page": 200}

    params = ChargifyStreamInstance.request_params(stream_state={}, next_page_token={"page": 2, "per_page": 200})

    assert params == {"page": 2, "per_page": 200}


def test_parse_subscriptions_response(SubscriptionsStreamInstance: Subscriptions):

    response = MagicMock()
    response.json.return_value = [
        {"subscription": {"id": 0, "state": "string", "balance_in_cents": 0}},
        {"subscription": {"id": 2, "state": "string", "balance_in_cents": 1000}},
        {"subscription": {"id": 3, "state": "string", "balance_in_cents": 100}},
    ]

    response = list(SubscriptionsStreamInstance.parse_response(response=response))

    assert len(response) == 3
    assert response[0] == {"id": 0, "state": "string", "balance_in_cents": 0}
    assert response[1] == {"id": 2, "state": "string", "balance_in_cents": 1000}
    assert response[2] == {"id": 3, "state": "string", "balance_in_cents": 100}


def test_parse_customers_response(CustomerStreamInstance: Customers):

    response = MagicMock()
    response.json.return_value = [
        {"customer": {"id": 0, "state": "string", "balance_in_cents": 0}},
        {"customer": {"id": 2, "state": "string", "balance_in_cents": 1000}},
        {"customer": {"id": 3, "state": "string", "balance_in_cents": 100}},
    ]

    response = list(CustomerStreamInstance.parse_response(response=response))

    assert len(response) == 3
    assert response[0] == {"id": 0, "state": "string", "balance_in_cents": 0}
    assert response[1] == {"id": 2, "state": "string", "balance_in_cents": 1000}
    assert response[2] == {"id": 3, "state": "string", "balance_in_cents": 100}
