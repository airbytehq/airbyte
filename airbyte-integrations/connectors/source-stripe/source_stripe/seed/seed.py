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

def fetch(url, headers, json_payload):
    encoded_data = urllib.parse.urlencode(json_payload)
    print(f"headers:{headers}")
    return requests.post(url, headers=headers, data=encoded_data).json()

def create_customer(headers, customer):
    url = "https://api.stripe.com/v1/customers"
    return fetch(url, headers, customer)

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
            f = executor.submit(create_customer, headers, record)
            futures.append(f)
    concurrent.futures.wait(futures)

    for f in futures:
        print(f"f: {f.result()}")


if __name__ == "__main__":
    _main()


