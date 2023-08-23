from source_stripe.seed.seed import Customer, BankAccount, prepare_create_customer, HttpRequest, prepare_create_bank_account, \
    prepare_search_customer

import pytest

def test_prepare_create_customer_request():
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
            "account_number": "000123456789"
        }
    }

    customer = Customer.parse_obj(record)
    headers = {"header_key": "header_value"}
    http_request = prepare_create_customer(headers, customer)

    expected_request = HttpRequest(
        method="POST",
        url="https://api.stripe.com/v1/customers",
        headers=headers,
        body={
            "description": "A fake customer",
            "email": "fake@airbyte.io",
            "name": "First Last",
            "balance": "900001",
        }
    )

    assert http_request == expected_request

def test_prepare_create_bank_account_request():
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
            "account_number": "000123456789"
        }
    }

    customer = Customer.parse_obj(record)
    headers = {"header_key": "header_value"}
    http_request = prepare_create_bank_account(headers, customer)

    expected_request = HttpRequest(
        method="POST",
        url="https://api.stripe.com/v1/customers/12345/sources",
        headers=headers,
        body={
            "source": {
                "object": "bank_account",
                "country": "US",
                "currency": "usd",
                "account_holder_type": "individual",
                "account_holder_name": "First Last",
                "routing_number": "110000000",
                "account_number": "000123456789"
            }
        }
    )

    assert http_request == expected_request

def test_prepare_create_bank_account_request_fails_if_customer_has_no_bank_account():
    record = {
        "id": "12345",
        "description": "A fake customer",
        "email": "fake@airbyte.io",
        "name": "First Last",
        "balance": "900001",
    }

    customer = Customer.parse_obj(record)
    headers = {"header_key": "header_value"}
    with pytest.raises(ValueError):
        prepare_create_bank_account(headers, customer)

def test_prepare_create_bank_account_request_fails_if_user_has_no_id():
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
            "account_number": "000123456789"
        }
    }

    customer = Customer.parse_obj(record)
    headers = {"header_key": "header_value"}
    with pytest.raises(ValueError):
        prepare_create_bank_account(headers, customer)

def test_prepare_search_customer_request():
    customer_name = "First Last"

    headers = {"header_key": "header_value"}

    expected_request = HttpRequest(
        method="GET",
        url="https://api.stripe.com/v1/customers/search",
        headers=headers,
        body={
            "query": "name: 'First Last'"
        }
    )

    http_request = prepare_search_customer(headers, customer_name)

    assert http_request == expected_request
