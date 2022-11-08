#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
from enum import IntEnum
from functools import partial
from typing import Iterator, List

import requests

from .common import _parsed_response, cursor_paginator, next_url_paginator


class APIClient:
    USER_AGENT = "Airbyte contact@airbyte.io"
    BASE_URL = "https://driftapi.com"

    def __init__(self, access_token: str):
        self._token = access_token
        self._headers = {
            "Authorization": f"Bearer {self._token}",
            "User-Agent": self.USER_AGENT,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        self.accounts = Account(client=self)
        self.contacts = Contact(client=self)
        self.conversations = Conversation(client=self)
        self.messages = Message(client=self)
        self.users = User(client=self)

    @_parsed_response
    def post(self, url, data, **kwargs):
        return requests.post(self.full_url(url), data=json.dumps(data), headers=self._headers, **kwargs)

    @_parsed_response
    def patch(self, url, data, **kwargs):
        """Used in fixtures.py only"""
        return requests.patch(self.full_url(url), data=json.dumps(data), headers=self._headers, **kwargs)

    @_parsed_response
    def get(self, url, **kwargs):
        return requests.get(self.full_url(url), headers=self._headers, **kwargs)

    def full_url(self, url):
        return f"{self.BASE_URL}/{url}"

    def check_token(self, token: str):
        return self.post("app/token_info", data={"accessToken": token})


class User:
    def __init__(self, client: APIClient):
        self.client = client

    def get(self, pk) -> dict:
        return self.client.get(f"users/{pk}")["data"]

    def list(self) -> Iterator[dict]:
        """Doesn't support pagination and return all users at once"""
        yield from self.client.get("users/list")["data"]

    def update(self, pk, **attributes) -> dict:
        params = {"userId": pk}
        return self.client.patch("users/update", data=attributes, params=params)


class Conversation:
    pagination = partial(cursor_paginator, per_page=50)

    class Status(IntEnum):
        OPEN = 1
        CLOSED = 2
        PENDING = 3

    def __init__(self, client: APIClient):
        self.client = client

    def get(self, pk: int) -> dict:
        return self.client.get(f"conversations/{pk}")

    def list(self, statuses: List[Status] = None) -> Iterator[dict]:
        """Conversations returned will be ordered by their updatedAt time with the most recently updated at the top of the list."""
        statuses = list(map(int, statuses or []))
        params = {"statusId": statuses}
        request = partial(self.client.get, url="conversations/list")
        return self.pagination(request, params=params)

    def create(self, **attributes) -> dict:
        return self.client.post("conversations/new", data=attributes)

    def update(self, pk: int, **attributes) -> dict:
        params = {"userId": pk}
        return self.client.patch("conversations/update", data=attributes, params=params)


class Message:
    pagination = partial(cursor_paginator, per_page=50)

    def __init__(self, client: APIClient):
        self.client = client

    def list(self, conversation_id: int) -> Iterator[dict]:
        """You have to provide conversation ID to get list of messages"""
        request = partial(self.client.get, url=f"conversations/{conversation_id}/messages")
        for data in self.pagination(request):
            yield from data.get("messages", [])

    def create(self, conversation_id: int, **attributes) -> dict:
        return self.client.post(f"conversations/{conversation_id}/messages", data=attributes).get("data")


class Account:
    pagination = partial(next_url_paginator, per_page=100)

    def __init__(self, client: APIClient):
        self.client = client

    def get(self, pk: int) -> dict:
        return self.client.get(f"accounts/{pk}")

    def list(self) -> Iterator[dict]:
        request = partial(self.client.get, url="accounts")
        for data in self.pagination(request):
            yield from data.get("accounts", [])

    def create(self, **attributes) -> dict:
        return self.client.post("accounts/create", data=attributes).get("data")

    def update(self, pk: int, **attributes) -> dict:
        params = {"userId": pk}
        return self.client.patch("accounts/update", data=attributes, params=params)


class Contact:
    def __init__(self, client: APIClient):
        self.client = client

    def get(self, pk: int) -> dict:
        return self.client.get(f"contacts/{pk}")["data"]

    def list(self, email: str) -> Iterator[dict]:
        """List contacts only possible with exact email filter"""
        yield from self.client.get("contacts", params={"email": email})["data"]

    def create(self, **attributes) -> dict:
        return self.client.post("contacts", data=attributes).get("data")

    def update(self, pk: int, **attributes) -> dict:
        params = {"userId": pk}
        return self.client.patch("contacts/update", data=attributes, params=params)
