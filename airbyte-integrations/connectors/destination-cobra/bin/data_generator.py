# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
import logging
import pathlib
from typing import List

from destination_salesforce import DestinationSalesforce


logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)

_API_BASE_URL = "https://airbyte--retl2.sandbox.my.salesforce.com/services/data/v61.0"


def _get_http_client():
    with open(pathlib.Path(__file__).parent.parent / "secrets" / "config.json", "r") as f:
        config = json.load(f)

    destination = DestinationSalesforce.create(config, _LOGGER)
    return destination._http_client


class AccountRepository:
    def __init__(self, http_client):
        self._http_client = http_client

    def create(self, name: str) -> str:
        """
        Returns account id
        """
        http_client = _get_http_client()
        _, response = http_client.send_request(
            "POST",
            url=f"{_API_BASE_URL}/sobjects/Account",
            json={
                "Name": name,
            },
            request_kwargs={},
        )

        if response.status_code != 201:
            raise Exception(f"Failed to create record: {response.json()}")
        return response.json()["id"]

    def fetch_all(self) -> List[dict]:
        """
        FIXME does not consider pagination for now
        """
        _, response = self._http_client.send_request(
            "GET",
            url=f"{_API_BASE_URL}/query?q=SELECT+Id%2C+Name+FROM+Account",
            request_kwargs={},
        )

        return response.json()["records"]


class ContactRepository:
    def __init__(self, http_client):
        self._http_client = http_client

    def create(self, last_name: str, account_id: str) -> str:
        """
        Returns contact id
        """
        http_client = _get_http_client()
        _, response = http_client.send_request(
            "POST",
            url=f"{_API_BASE_URL}/sobjects/Contact",
            json={
                "LastName": last_name,
                "AccountId": account_id,
            },
            request_kwargs={},
        )

        if response.status_code != 201:
            raise Exception(f"Failed to create record: {response.json()}")
        return response.json()["id"]

    def fetch_all(self) -> List[dict]:
        """
        FIXME does not consider pagination for now
        """
        _, response = self._http_client.send_request(
            "GET",
            url=f"{_API_BASE_URL}/query?q=SELECT+Id%2C+Name%2C+AccountId+FROM+Contact",
            request_kwargs={},
        )

        return response.json()["records"]


def _generate_record_names(record_type: str) -> set:
    return set(map(lambda i: f"{record_type} from data generator - {i}", range(10)))


def _find_account_id(accounts, account_name: str) -> str:
    for account in accounts:
        if account["Name"] == account_name:
            return account["Id"]
    raise Exception(f"Account {account_name} not found")


if __name__ == "__main__":
    http_client = _get_http_client()

    account_repository = AccountRepository(http_client)
    already_created_accounts = account_repository.fetch_all()
    to_be_created_accounts = _generate_record_names("Account") - set(map(lambda account: account["Name"], already_created_accounts))
    if to_be_created_accounts:
        for account_name in to_be_created_accounts:
            account_repository.create(account_name)
        accounts = account_repository.fetch_all()
    else:
        accounts = already_created_accounts

    contact_repository = ContactRepository(http_client)
    already_created_contacts = contact_repository.fetch_all()
    to_be_created_contacts = _generate_record_names("Contact") - set(map(lambda account: account["LastName"], already_created_contacts))
    if to_be_created_contacts:
        for contact_name in to_be_created_contacts:
            contact_repository.create(contact_name, _find_account_id(accounts, contact_name.replace("Contact", "Account")))
