#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import asyncio
import concurrent
import json
import urllib
from typing import Literal, Optional, Dict, Any

import aiohttp
import click
import requests
from pydantic import BaseModel, Field


class BankAccount(BaseModel):
    object: str = "bank_account"
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

def prepare_create_customer(headers: Dict[str, str], customer: Customer):
    url = "https://api.stripe.com/v1/customers"
    customer_data = customer.dict(exclude_none=True)
    customer_data.pop("bank_account")
    return HttpRequest(method="POST", url=url, headers=headers, body=customer_data)

def prepare_create_bank_account(headers: Dict[str, str], customer: Customer):
    if customer.id is None:
        raise ValueError(f"Cannot create bank account for uninitialized customer {customer}")
    if customer.bank_account is None:
        raise ValueError(f"Cannot create bank account for customer without bank account information: {customer}")

    url = f"https://api.stripe.com/v1/customers/{customer.id}/sources"
    bank_account_data = {"source": customer.bank_account.dict(exclude_none=True)}
    bank_account_data["source"]["account_holder_name"] = customer.name
    return HttpRequest(method="POST", url=url, headers=headers, body=bank_account_data)


@click.group()
def _main():
    pass


def dict_to_urlencoded(d):
    return kv_translation(d, "", "")


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


def fetch(url, headers, json_payload, method=requests.post):
    print(f"headers:{headers}")
    if json_payload:
        encoded_data = recursive_url_encode(json_payload)
        print(f"encoded data: {encoded_data}")
        return method(url, headers=headers, data=encoded_data).json()
    else:
        return method(url, headers=headers).json()

def submit(request: HttpRequest):
    method = requests.post if request.method == "POST" else requests.get
    if request.body:
        payload = recursive_url_encode(request.body)
        response = method(request.url, headers=request.headers, data=payload)
    else:
        response = method(request.url, headers=request.headers)
    return response.json()



def create_customer(headers, customer):
    request = prepare_create_customer(headers, customer)
    return submit(request)


def create_bank_account(headers, customer: Customer):
    if customer.id is None:
        raise ValueError(f"Cannot create bank account for uninitialized customer {customer}")
    request = prepare_create_bank_account(headers, customer)
    return submit(request)


def create_customer_and_bank_account(headers, customer: Customer):
    customer_output = create_customer(headers, customer)
    if "id" in customer_output:
        customer.id = customer_output["id"]
    else:
        raise RuntimeError(f"Failed to created customer {customer}. Response: {customer_output}")
    print(f"created customer: {customer}")
    if customer.bank_account:
        bank_account = create_bank_account(headers, customer)
        print(f"created bank account {bank_account}")
    else:
        bank_account = None
    return customer, bank_account


def search_customer(customer_name, headers):
    url = f"https://api.stripe.com/v1/customers/search"
    data = {"query": f"name: '{customer_name}'"}
    response = fetch(url, headers, data, requests.get)
    return response.get("data", [])


def _load_config(path_to_config):
    with open(path_to_config, "r") as f:
        return json.loads(f.read())


@_main.command()
@click.argument("path_to_config")
@click.argument("path_to_data")
def generate_records(path_to_config, path_to_data):
    config = _load_config(path_to_config)
    records = _load_config(path_to_data)
    CONCURRENCY = 1
    headers = {"Authorization": f"Bearer {config['client_secret']}"}
    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        for record in records:
            customer_data = record
            customer = Customer.parse_obj(customer_data)
            customer_exists = is_customer_already_created(customer.name, headers)
            if customer_exists:
                print(f"Customer {customer.name} already exists. Skipping...")
            else:
                f = executor.submit(create_customer_and_bank_account, headers, customer)
                futures.append(f)
    concurrent.futures.wait(futures)

    for f in futures:
        print(f"f: {f.result()}")


def is_customer_already_created(customer_name, headers):
    customer = search_customer(customer_name, headers)
    return len(customer) > 0


if __name__ == "__main__":
    _main()
