#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import asyncio
import concurrent
import json
import urllib

import aiohttp
import click
import requests


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


def create_customer(headers, customer):
    url = "https://api.stripe.com/v1/customers"
    return fetch(url, headers, customer)


def create_bank_account(headers, customer, bank_account_data):
    customer_id = customer["id"]
    customer_name = customer["name"]
    bank_account_data["source"]["account_holder_name"] = customer_name
    print(f"bank_account:\n{bank_account_data}")
    url = f"https://api.stripe.com/v1/customers/{customer_id}/sources"
    #url = f"https://api.stripe.com/v1/tokens"
    return fetch(url, headers, bank_account_data)


def create_customer_and_bank_account(headers, customer_data, bank_account_data):
    customer = create_customer(headers, customer_data)
    print(f"created customer: {customer}")
    if bank_account_data:
        bank_account = create_bank_account(headers, customer, bank_account_data)
        print(f"created bank account {bank_account}")
    else:
        bank_account = None
    return customer, bank_account

def search_customer(customer_name, headers):
    url = f"https://api.stripe.com/v1/customers/search"
    data = {
        "query": f"name: '{customer_name}'"
    }
    response =  fetch(url, headers, data, requests.get)
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
            customer_name = customer_data["name"]
            customer_exists = is_customer_already_created(customer_name, headers)
            if customer_exists:
                print(f"Customer {customer_name} already exists. Skipping...")
            else:
                bank_account_data = customer_data.pop("bank_account")
                f = executor.submit(create_customer_and_bank_account, headers, customer_data, bank_account_data)
                futures.append(f)
    concurrent.futures.wait(futures)

    for f in futures:
        print(f"f: {f.result()}")

def is_customer_already_created(customer_name, headers):
    customer = search_customer(customer_name, headers)
    return len(customer) > 0

@_main.command()
@click.argument("path_to_config")
@click.argument("customer_id")
def get_customer(path_to_config, customer_id):
    config = _load_config(path_to_config)
    headers = {"Authorization": f"Bearer {config['client_secret']}"}
    customer = customer_exists(customer_id, headers)
    print(customer)


if __name__ == "__main__":
    _main()
