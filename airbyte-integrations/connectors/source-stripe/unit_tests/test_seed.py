#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from unittest import TestCase
from unittest.mock import Mock

import pytest
from source_stripe.seed.seed import Customer, HttpRequest, StripeAPI

_MOCK_RESPONSE = {"key": "value"}
_BEARER_TOKEN = "secret"
_AUTHENTICATION_HEADER = {"Authorization": "Bearer secret"}


class StripeApiTestCase(TestCase):
    def setUp(self) -> None:
        self._requester = Mock()
        self._requester.submit.return_value = _MOCK_RESPONSE
        self._stripe_api = StripeAPI("secret", self._requester)

    def test_prepare_create_customer_request(self):
        record = {
            "description": "A fake customer",
            "email": "fake@airbyte.io",
            "name": "First Last",
            "balance": "900001",
            "bank_account": {
                "object": "bank_account",
                "country": "US",
                "currency": "usd",
                "account_holder_type": "individual",
                "routing_number": "110000000",
                "account_number": "000123456789",
            },
        }

        customer = Customer.parse_obj(record)

        expected_request = HttpRequest(
            method="POST",
            url="https://api.stripe.com/v1/customers",
            headers=_AUTHENTICATION_HEADER,
            body={
                "description": "A fake customer",
                "email": "fake@airbyte.io",
                "name": "First Last",
                "balance": "900001",
            },
        )

        response = self._stripe_api.create_customer(customer)

        self._requester.submit.assert_called_with(expected_request)
        assert response == _MOCK_RESPONSE

    def test_prepare_create_bank_account_request(self):
        record = {
            "id": "12345",
            "description": "A fake customer",
            "email": "fake@airbyte.io",
            "name": "First Last",
            "balance": "900001",
            "bank_account": {
                "object": "bank_account",
                "country": "US",
                "currency": "usd",
                "account_holder_type": "individual",
                "routing_number": "110000000",
                "account_number": "000123456789",
            },
        }
        expected_request = HttpRequest(
            method="POST",
            url="https://api.stripe.com/v1/customers/12345/sources",
            headers=_AUTHENTICATION_HEADER,
            body={
                "source": {
                    "object": "bank_account",
                    "country": "US",
                    "currency": "usd",
                    "account_holder_type": "individual",
                    "account_holder_name": "First Last",
                    "routing_number": "110000000",
                    "account_number": "000123456789",
                }
            },
        )

        customer = Customer.parse_obj(record)
        response = self._stripe_api.create_bank_account(customer)

        self._requester.submit.assert_called_with(expected_request)
        assert response == _MOCK_RESPONSE

    def test_prepare_create_bank_account_request_fails_if_customer_has_no_bank_account(self):
        record = {
            "id": "12345",
            "description": "A fake customer",
            "email": "fake@airbyte.io",
            "name": "First Last",
            "balance": "900001",
        }

        customer = Customer.parse_obj(record)
        with pytest.raises(ValueError):
            self._stripe_api.create_bank_account(customer)

    def test_prepare_create_bank_account_request_fails_if_user_has_no_id(self):
        record = {
            "description": "A fake customer",
            "email": "fake@airbyte.io",
            "name": "First Last",
            "balance": "900001",
            "bank_account": {
                "object": "bank_account",
                "country": "US",
                "currency": "usd",
                "account_holder_type": "individual",
                "routing_number": "110000000",
                "account_number": "000123456789",
            },
        }

        customer = Customer.parse_obj(record)
        with pytest.raises(ValueError):
            self._stripe_api.create_bank_account(customer)

    def test_prepare_search_customer_request_no_customer_found(self):
        customer_name = "First Last"

        expected_request = HttpRequest(
            method="GET",
            url="https://api.stripe.com/v1/customers/search",
            headers=_AUTHENTICATION_HEADER,
            body={"query": "name: 'First Last'"},
        )

        self._requester.submit.return_value = {"data": []}

        response = self._stripe_api.search_customer(customer_name)

        self._requester.submit.assert_called_with(expected_request)
        assert response == []

    def test_prepare_search_customer_request_found_a_customer(self):
        customer_name = "First Last"

        expected_request = HttpRequest(
            method="GET",
            url="https://api.stripe.com/v1/customers/search",
            headers=_AUTHENTICATION_HEADER,
            body={"query": "name: 'First Last'"},
        )

        self._requester.submit.return_value = {"data": [{"id": "123"}]}

        response = self._stripe_api.search_customer(customer_name)

        self._requester.submit.assert_called_with(expected_request)
        assert response == [{"id": "123"}]
