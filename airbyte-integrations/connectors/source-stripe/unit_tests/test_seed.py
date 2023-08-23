from source_stripe.seed.seed import Customer, BankAccount, prepare_create_customer, HttpRequest


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
