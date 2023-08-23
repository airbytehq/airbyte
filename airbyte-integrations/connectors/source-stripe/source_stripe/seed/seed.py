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


def fetch(url, headers, json_payload):
    encoded_data = recursive_url_encode(json_payload)
    print(f"headers:{headers}")
    print(f"encoded data: {encoded_data}")
    return requests.post(url, headers=headers, data=encoded_data).json()


def create_customer(headers, customer):
    url = "https://api.stripe.com/v1/customers"
    return fetch(url, headers, customer)


def create_bank_account(headers, customer, bank_account_data):
    customer_id = customer["id"]
    customer_name = customer["name"]
    bank_account_data["bank_account"]["account_holder_name"] = customer_name
    print(f"bank_account:\n{bank_account_data}")
    # url = f"https://api.stripe.com/v1/customers/{customer_id}/sources"
    url = f"https://api.stripe.com/v1/tokens"
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


@_main.command()
@click.argument("path_to_config")
@click.argument("path_to_data")
def generate_records(path_to_config, path_to_data):
    with open(path_to_config, "r") as f:
        config = json.loads(f.read())
    with open(path_to_data, "r") as f:
        records = json.loads(f.read())
    CONCURRENCY = 1
    headers = {"Authorization": f"Bearer {config['client_secret']}"}
    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        for record in records:
            customer_data = record
            bank_account_data = {"bank_account": customer_data.pop("bank_account")}
            print(f"customer_data: {customer_data}")
            print(f"bank_account_data: {bank_account_data}")
            f = executor.submit(create_customer_and_bank_account, headers, customer_data, bank_account_data)
            futures.append(f)
    concurrent.futures.wait(futures)

    for f in futures:
        print(f"f: {f.result()}")


if __name__ == "__main__":
    _main()
