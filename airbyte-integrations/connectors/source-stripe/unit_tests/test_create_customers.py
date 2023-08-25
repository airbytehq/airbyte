#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from unittest import TestCase
from unittest.mock import Mock

from tools.create_customers import (
    BankAccount,
    BankAccountCreateConfig,
    Customer,
    CustomerCreateConfig,
    HttpMethod,
    HttpRequest,
    StripeAPI,
    create_customer_and_bank_account,
    is_customer_already_created,
)

_BEARER_TOKEN = "secret"
_AUTHENTICATION_HEADER = {"Authorization": "Bearer secret"}


class StripeApiTestCase(TestCase):
    def setUp(self) -> None:
        self._requester = Mock()
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

        customer_create_config = CustomerCreateConfig.parse_obj(record)

        expected_request = HttpRequest(
            method=HttpMethod.POST,
            url="https://api.stripe.com/v1/customers",
            headers=_AUTHENTICATION_HEADER,
            body={
                "description": "A fake customer",
                "email": "fake@airbyte.io",
                "name": "First Last",
                "balance": "900001",
            },
        )

        self._requester.submit.return_value = {
            "id": "12345",
            "description": customer_create_config.description,
            "email": customer_create_config.email,
            "name": customer_create_config.name,
            "balance": customer_create_config.balance,
        }
        expected_customer = Customer(
            id="12345",
            description=customer_create_config.description,
            email=customer_create_config.email,
            name=customer_create_config.name,
            balance=customer_create_config.balance,
        )

        response = self._stripe_api.create_customer(customer_create_config)

        self._requester.submit.assert_called_with(expected_request)
        assert response == expected_customer

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
            method=HttpMethod.POST,
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

        customer_create_config = CustomerCreateConfig.parse_obj(record)
        customer = Customer(
            id="12345",
            description=customer_create_config.description,
            email=customer_create_config.email,
            name=customer_create_config.name,
            balance=customer_create_config.balance,
        )

        self._requester.submit.return_value = {
            "id": "456",
            "account_holder_name": customer_create_config.name,
            "account_holder_type": customer_create_config.bank_account.account_holder_type,
            "account_number": customer_create_config.bank_account.account_number,
            "routing_number": customer_create_config.bank_account.routing_number,
            "country": customer_create_config.bank_account.country,
            "currency": customer_create_config.bank_account.currency,
        }
        expected_bank_account = BankAccount(
            id="456",
            account_holder_name=customer_create_config.name,
            account_holder_type=customer_create_config.bank_account.account_holder_type,
            account_number=customer_create_config.bank_account.account_number,
            routing_number=customer_create_config.bank_account.routing_number,
            country=customer_create_config.bank_account.country,
            currency=customer_create_config.bank_account.currency,
        )
        response = self._stripe_api.create_bank_account(customer, customer_create_config.bank_account)

        self._requester.submit.assert_called_with(expected_request)
        assert response == expected_bank_account

    def test_prepare_search_customer_request_no_customer_found(self):
        customer_name = "First Last"

        expected_request = HttpRequest(
            method=HttpMethod.GET,
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
            method=HttpMethod.GET,
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


def test_create_customer_and_bank_account():
    stripe_api = Mock()

    customer_create_config = CustomerCreateConfig(
        name="A CUSTOMER",
        description="A fake customer",
        email="fake@airbyte.io",
        balance="12345",
        bank_account=BankAccountCreateConfig(
            country="US",
            currency="usd",
            account_holder_type="individual",
            routing_number="123445",
            account_number="67890",
        ),
    )

    expected_customer = Customer(
        id="12345",
        description=customer_create_config.description,
        email=customer_create_config.email,
        name=customer_create_config.name,
        balance=customer_create_config.balance,
    )
    expected_bank_account = BankAccount(
        id="456",
        account_holder_name=customer_create_config.name,
        account_holder_type=customer_create_config.bank_account.account_holder_type,
        account_number=customer_create_config.bank_account.account_number,
        routing_number=customer_create_config.bank_account.routing_number,
        country=customer_create_config.bank_account.country,
        currency=customer_create_config.bank_account.currency,
    )

    stripe_api.create_customer.return_value = expected_customer
    stripe_api.create_bank_account.return_value = expected_bank_account

    returned_customer, returned_bank_account = create_customer_and_bank_account(customer_create_config, stripe_api)

    assert returned_customer == expected_customer
    assert returned_bank_account == expected_bank_account


def test_create_customer_and_bank_account_without_a_bank_account():
    stripe_api = Mock()

    customer_create_config = CustomerCreateConfig(
        name="A CUSTOMER",
        description="A fake customer",
        email="fake@airbyte.io",
        balance="12345",
    )

    expected_customer = Customer(
        id="12345",
        description=customer_create_config.description,
        email=customer_create_config.email,
        name=customer_create_config.name,
        balance=customer_create_config.balance,
    )

    stripe_api.create_customer.return_value = expected_customer

    returned_customer, returned_bank_account = create_customer_and_bank_account(customer_create_config, stripe_api)

    assert returned_customer == expected_customer
    assert returned_bank_account is None
