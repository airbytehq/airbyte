#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from unittest import TestCase
from unittest.mock import Mock

import pytest
from tools.create_customers import (
    BankAccount,
    Customer,
    HttpRequest,
    StripeAPI,
    create_customer_and_bank_account,
    is_customer_already_created,
)

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


def test_is_customer_already_created_returns_false_if_no_customers():
    stripe_api = Mock()
    stripe_api.search_customer.return_value = []

    customer_name = "A CUSTOMER"

    customer_is_already_created = is_customer_already_created(customer_name, stripe_api)
    assert not customer_is_already_created


def test_is_customer_already_created_returns_true_if_there_is_at_least_one_customer():
    stripe_api = Mock()
    customer_name = "A CUSTOMER"

    stripe_api.search_customer.return_value = [{"id": "1", "name": customer_name}]

    customer_is_already_created = is_customer_already_created(customer_name, stripe_api)
    assert customer_is_already_created


def test_create_customer_and_bank_account_fails_if_customer_already_has_an_id():
    stripe_api = Mock()

    customer = Customer(
        name="A CUSTOMER",
        id="12345",
        description="A fake customer",
        email="fake@airbyte.io",
        balance="12345",
        bank_account=BankAccount(
            country="US",
            currency="usd",
            account_holder_type="individual",
            routing_number="123445",
            account_number="67890",
        ),
    )

    stripe_api.create_customer.return_value = customer.dict(exclude_none=True)

    with pytest.raises(ValueError):
        create_customer_and_bank_account(customer, stripe_api)


def test_create_customer_and_bank_account_fails_if_bank_account_already_has_an_id():
    stripe_api = Mock()

    customer = Customer(
        name="A CUSTOMER",
        description="A fake customer",
        email="fake@airbyte.io",
        balance="12345",
        bank_account=BankAccount(
            id="12345",
            country="US",
            currency="usd",
            account_holder_type="individual",
            routing_number="123445",
            account_number="67890",
        ),
    )

    stripe_api.create_customer.return_value = customer.dict(exclude_none=True)

    with pytest.raises(ValueError):
        create_customer_and_bank_account(customer, stripe_api)


def test_create_customer_and_bank_account():
    stripe_api = Mock()

    customer = Customer(
        name="A CUSTOMER",
        description="A fake customer",
        email="fake@airbyte.io",
        balance="12345",
        bank_account=BankAccount(
            country="US",
            currency="usd",
            account_holder_type="individual",
            routing_number="123445",
            account_number="67890",
        ),
    )

    create_customer_response = customer.dict(exclude_none=True)
    create_customer_response["id"] = "121345"
    create_bank_account_response = customer.bank_account.dict(exclude_none=True)
    create_bank_account_response["id"] = "6789"

    stripe_api.create_customer.return_value = create_customer_response
    stripe_api.create_bank_account.return_value = create_bank_account_response

    expected_customer = Customer(
        id=create_customer_response["id"],
        name="A CUSTOMER",
        description="A fake customer",
        email="fake@airbyte.io",
        balance="12345",
        bank_account=BankAccount(
            id=create_bank_account_response["id"],
            country="US",
            currency="usd",
            account_holder_type="individual",
            routing_number="123445",
            account_number="67890",
        ),
    )
    returned_customer = create_customer_and_bank_account(customer, stripe_api)

    assert returned_customer == expected_customer


def test_create_customer_and_bank_account_fails_if_no_customer_id_is_returned():
    stripe_api = Mock()

    customer = Customer(
        name="A CUSTOMER",
        description="A fake customer",
        email="fake@airbyte.io",
        balance="12345",
        bank_account=BankAccount(
            country="US",
            currency="usd",
            account_holder_type="individual",
            routing_number="123445",
            account_number="67890",
        ),
    )

    create_customer_response = customer.dict(exclude_none=True)
    stripe_api.create_customer.return_value = create_customer_response

    with pytest.raises(RuntimeError):
        create_customer_and_bank_account(customer, stripe_api)


def test_create_customer_and_bank_acount_fails_if_no_bank_account_id_is_returned():
    stripe_api = Mock()

    customer = Customer(
        name="A CUSTOMER",
        description="A fake customer",
        email="fake@airbyte.io",
        balance="12345",
        bank_account=BankAccount(
            country="US",
            currency="usd",
            account_holder_type="individual",
            routing_number="123445",
            account_number="67890",
        ),
    )

    create_customer_response = customer.dict(exclude_none=True)
    create_customer_response["id"] = "121345"
    create_bank_account_response = customer.bank_account.dict(exclude_none=True)

    stripe_api.create_customer.return_value = create_customer_response
    stripe_api.create_bank_account.return_value = create_bank_account_response

    with pytest.raises(RuntimeError):
        create_customer_and_bank_account(customer, stripe_api)
