#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import concurrent.futures
import json
from copy import deepcopy
from enum import Enum
from typing import Any, Dict, Optional

import click
import requests
from pydantic import BaseModel, Field


class BankAccountCreateConfig(BaseModel):
    object: str = "bank_account"
    country: str = Field()
    currency: str = Field()
    account_holder_type: str = Field()
    routing_number: str = Field()
    account_number: str = Field()


class CustomerCreateConfig(BaseModel):
    description: str
    email: str
    name: str
    balance: str
    bank_account: Optional[BankAccountCreateConfig]


class BankAccount(BaseModel):
    object: str = "bank_account"
    id: str
    country: str
    currency: str
    account_holder_name: str
    account_holder_type: str
    routing_number: str
    account_number: str


class Customer(BaseModel):
    id: str
    description: str
    email: str
    name: str
    balance: str


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"


class HttpRequest(BaseModel):
    method: HttpMethod
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

    def create_customer(self, customer: CustomerCreateConfig) -> Customer:
        request = self.prepare_create_customer(customer)
        return Customer.parse_obj(self._requester.submit(request))

    def create_bank_account(self, customer: Customer, bank_account_create_config: BankAccountCreateConfig) -> BankAccount:
        request = self.prepare_create_bank_account(customer, bank_account_create_config)
        return BankAccount.parse_obj(self._requester.submit(request))

    def prepare_create_customer(self, customer: CustomerCreateConfig):
        if customer.bank_account is None:
            raise ValueError(f"Cannot create bank account for customer without bank account information: {customer}")
        url = "https://api.stripe.com/v1/customers"
        customer_data = customer.dict(exclude_none=True)
        customer_data.pop("bank_account", {})
        return HttpRequest(method=HttpMethod.POST, url=url, headers=self._authentication_header, body=customer_data)

    def search_customer(self, customer_name):
        request = self.prepare_search_customer(customer_name)
        response = self._requester.submit(request)
        return response.get("data", [])

    def prepare_create_bank_account(self, customer: Customer, bank_account: BankAccountCreateConfig):
        url = f"https://api.stripe.com/v1/customers/{customer.id}/sources"
        bank_account_data = {"source": bank_account.dict(exclude_none=True)}
        bank_account_data["source"]["account_holder_name"] = customer.name
        return HttpRequest(method=HttpMethod.POST, url=url, headers=self._authentication_header, body=bank_account_data)

    def prepare_search_customer(self, customer_name: str) -> HttpRequest:
        url = "https://api.stripe.com/v1/customers/search"
        data = {"query": f"name: '{customer_name}'"}
        return HttpRequest(method=HttpMethod.GET, url=url, headers=self._authentication_header, body=data)


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


def is_customer_already_created(customer_name: str, stripe_api: StripeAPI) -> bool:
    customer = stripe_api.search_customer(customer_name)
    return len(customer) > 0


def create_customer_and_bank_account(
    customer_create_config: CustomerCreateConfig, stripe_api: StripeAPI
) -> (Customer, Optional[BankAccount]):
    customer = stripe_api.create_customer(customer_create_config)
    print(f"created customer: {customer_create_config}")
    if customer_create_config.bank_account:
        bank_account = stripe_api.create_bank_account(customer, customer_create_config.bank_account)
        return customer, bank_account
    else:
        return customer, None


def _load_json_file(path_to_config):
    with open(path_to_config, "r") as f:
        return json.loads(f.read())


def populate_customer(customer: CustomerCreateConfig, stripe_api: StripeAPI):
    customer_exists = is_customer_already_created(customer.name, stripe_api)
    if customer_exists:
        print(f"Customer {customer.name} already exists. Skipping...")
        return None
    else:
        return create_customer_and_bank_account(customer, stripe_api)


@_main.command()
@click.option("--config-path")
@click.option("--data-path")
@click.option("--concurrency", default=1, type=int)
def populate_customers(config_path, data_path, concurrency):
    config = _load_json_file(config_path)
    records = _load_json_file(data_path)
    futures = []
    requester = Requester()
    stripe_api = StripeAPI(config["client_secret"], requester)
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        for record in records:
            customer_data = record
            customer = CustomerCreateConfig.parse_obj(customer_data)
            f = executor.submit(populate_customer, customer, stripe_api)
            futures.append(f)
        concurrent.futures.wait(futures)


@_main.command()
@click.argument("path_to_template")
@click.option("--tag")
@click.option("--iterations", type=int)
@click.option("--output-path")
def generate_customers(path_to_template, tag, iterations, output_path):
    template = _load_json_file(path_to_template)
    all_records = []
    for iteration in range(iterations):
        output = deepcopy(template)
        for record in output:
            record["name"] = record["name"].replace("{TAG}", tag).replace("{ITERATION}", str(iteration))
            if "email" not in record:
                record["email"] = f"{record['name'].split('__')[0]}@fakenews.io".lower()
            all_records.append(record)
    with open(output_path, "w") as f:
        f.write(json.dumps(all_records, indent=2))


if __name__ == "__main__":
    _main()
