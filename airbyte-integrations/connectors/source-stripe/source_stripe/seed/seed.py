#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import concurrent.futures
import json
from typing import Any, Dict, Optional

import click
import requests
from pydantic import BaseModel, Field


class BankAccount(BaseModel):
    object: str = "bank_account"
    id: Optional[str]
    country: str = Field()
    currency: str = Field()
    account_holder_type: str = Field()
    routing_number: str = Field()
    account_number: str = Field()


class Customer(BaseModel):
    id: Optional[str]
    description: str
    email: str
    name: str
    balance: str
    bank_account: Optional[BankAccount]


class HttpRequest(BaseModel):
    method: str
    url: str
    headers: Dict[str, str]
    body: Optional[Dict[str, Any]]


class Requester:
    def submit(self, request: HttpRequest):
        method = requests.post if request.method == "POST" else requests.get
        if request.body:
            payload = recursive_url_encode(request.body)
            response = method(request.url, headers=request.headers, data=payload)
        else:
            response = method(request.url, headers=request.headers)
        return response.json()


class StripeAPI:
    def __init__(self, secret_key: str, requester: Requester):
        self._authentication_header = {"Authorization": f"Bearer {secret_key}"}
        self._requester = requester

    def create_customer(self, customer):
        request = self.prepare_create_customer(customer)
        return self._requester.submit(request)

    def create_bank_account(self, customer: Customer):
        if customer.id is None:
            raise ValueError(f"Cannot create bank account for uninitialized customer {customer}")
        request = self.prepare_create_bank_account(customer)
        return self._requester.submit(request)

    def prepare_create_customer(self, customer: Customer):
        url = "https://api.stripe.com/v1/customers"
        customer_data = customer.dict(exclude_none=True)
        customer_data.pop("bank_account", {})
        return HttpRequest(method="POST", url=url, headers=self._authentication_header, body=customer_data)

    def search_customer(self, customer_name):
        request = self.prepare_search_customer(customer_name)
        response = self._requester.submit(request)
        return response.get("data", [])

    def prepare_create_bank_account(self, customer: Customer):
        if customer.id is None:
            raise ValueError(f"Cannot create bank account for uninitialized customer {customer}")
        if customer.bank_account is None:
            raise ValueError(f"Cannot create bank account for customer without bank account information: {customer}")

        url = f"https://api.stripe.com/v1/customers/{customer.id}/sources"
        bank_account_data = {"source": customer.bank_account.dict(exclude_none=True)}
        bank_account_data["source"]["account_holder_name"] = customer.name
        return HttpRequest(method="POST", url=url, headers=self._authentication_header, body=bank_account_data)

    def prepare_search_customer(self, customer_name: str) -> HttpRequest:
        url = "https://api.stripe.com/v1/customers/search"
        data = {"query": f"name: '{customer_name}'"}
        return HttpRequest(method="GET", url=url, headers=self._authentication_header, body=data)


@click.group()
def _main():
    pass


def kv_translation(d, line, final_str):
    for key in d:
        key_str = key if not line else "[{}]".format(key)
        if type(d[key]) is not dict:
            final_str = "{}{}{}={}\n".format(final_str, line, key_str, d[key])
        else:
            final_str = kv_translation(d[key], line + key_str, final_str)
    return final_str


def recursive_url_encode(data, parent_key=None):
    items = []
    for key, value in data.items():
        if parent_key is not None:
            new_key = f"{parent_key}[{key}]"
        else:
            new_key = key

        if isinstance(value, dict):
            items.extend(recursive_url_encode(value, new_key))
        else:
            items.append((new_key, value))

    return items


def is_customer_already_created(customer_name: str, stripe_api: StripeAPI):
    customer = stripe_api.search_customer(customer_name)
    return len(customer) > 0


def create_customer_and_bank_account(customer: Customer, stripe_api: StripeAPI):
    if customer.id is not None:
        raise ValueError(f"Cannot create customer {customer} because it already has an ID")
    if customer.bank_account and customer.bank_account.id is not None:
        raise ValueError(f"Cannot create bank account for {customer} because it already has an ID")
    customer_output = stripe_api.create_customer(customer)
    if "id" in customer_output:
        customer.id = customer_output["id"]
    else:
        raise RuntimeError(f"Failed to created customer {customer}. Response: {customer_output}")
    print(f"created customer: {customer}")
    if customer.bank_account:
        bank_account_output = stripe_api.create_bank_account(customer)
        if "id" in bank_account_output:
            customer.bank_account.id = bank_account_output["id"]
        else:
            raise RuntimeError(f"Failed to created bank account for customer {customer}. Response: {bank_account_output}")
        print(f"created bank account {bank_account_output}")
    return customer


def _load_config(path_to_config):
    with open(path_to_config, "r") as f:
        return json.loads(f.read())


def populate_customer(customer: Customer, stripe_api: StripeAPI):
    customer_exists = is_customer_already_created(customer.name, stripe_api)
    if customer_exists:
        print(f"Customer {customer.name} already exists. Skipping...")
        return None
    else:
        return create_customer_and_bank_account(customer, stripe_api)


@_main.command()
@click.argument("path_to_config")
@click.argument("path_to_data")
def generate_records(path_to_config, path_to_data):
    config = _load_config(path_to_config)
    records = _load_config(path_to_data)
    CONCURRENCY = 1
    futures = []
    requester = Requester()
    stripe_api = StripeAPI(config["client_secret"], requester)
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        for record in records:
            customer_data = record
            customer = Customer.parse_obj(customer_data)
            f = executor.submit(populate_customer, customer, stripe_api)
            futures.append(f)
        concurrent.futures.wait(futures)

    for f in futures:
        print(f"f: {f.result()}")


if __name__ == "__main__":
    _main()
