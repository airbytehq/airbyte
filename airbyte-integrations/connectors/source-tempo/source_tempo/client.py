#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from functools import partial
from json import JSONDecodeError
from typing import Mapping, Tuple

import requests
from base_python import BaseClient
from requests.exceptions import ConnectionError
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator


class Client(BaseClient):
    """
    Tempo API Reference: https://tempo-io.github.io/tempo-api-docs/
    """

    API_VERSION = 3
    DEFAULT_ITEMS_PER_PAGE = 100

    PARAMS = {"limit": DEFAULT_ITEMS_PER_PAGE, "offset": 0}
    ENTITIES_MAP = {
        "accounts": {"url": "/accounts", "func": lambda v: v["results"], "params": PARAMS},
        "customers": {"url": "/customers", "func": lambda v: v["results"], "params": PARAMS},
        "worklogs": {"url": "/worklogs", "func": lambda v: v["results"], "params": PARAMS},
        "workload-schemes": {"url": "/workload-schemes", "func": lambda v: v["results"], "params": PARAMS},
    }

    def __init__(self, authorization):
        self.auth = authorization
        self.base_api_url = f"https://api.tempo.io/core/{self.API_VERSION}"
        super().__init__()

    def lists(self, name, url, params, func, **kwargs):
        while True:
            response = requests.get(f"{self.base_api_url}{url}?limit={params['limit']}&offset={params['offset']}", headers=self.get_headers())
            data = func(response.json())
            yield from data
            if len(data) < self.DEFAULT_ITEMS_PER_PAGE:
                break
            params["offset"] += self.DEFAULT_ITEMS_PER_PAGE

    def get_headers(self):
        if self.auth.get("auth_type") == "Token":
            return {"Authorization": f"Bearer {self.auth.get('api_token')}"}
        else:
            return Oauth2Authenticator(
                token_refresh_endpoint="https://api.tempo.io/oauth/token/",
                client_id=self.auth.get("client_id"),
                client_secret=self.auth.get("client_secret"),
                refresh_token=self.auth.get("refresh_token"),
                scopes=[
                    "accounts:manage",
                    "accounts:view",
                    "activities:produce",
                    "approvals:manage",
                    "approvals:view",
                    "audit:view",
                    "periods:view",
                    "plans:manage",
                    "plans:view",
                    "projects:manage",
                    "projects:view",
                    "schemes:manage",
                    "schemes:view",
                    "teams:manage",
                    "teams:view",
                    "worklogs:manage",
                    "worklogs:view"
                ]
            ).get_auth_header()

    def _enumerate_methods(self) -> Mapping[str, callable]:
        return {entity: partial(self.lists, name=entity, **value) for entity, value in self.ENTITIES_MAP.items()}

    def health_check(self) -> Tuple[bool, str]:
        alive = True
        error_msg = None
        # must be implemented later

        try:
            next(self.lists(name="workload-schemes", **self.ENTITIES_MAP["workload-schemes"]))

        except ConnectionError as error:
            alive, error_msg = False, str(error)
        # If the input domain is incorrect or doesn't exist, then the response would be empty, resulting in a JSONDecodeError
        except JSONDecodeError:
            alive, error_msg = (
                False,
                "Unable to connect to the Tempo API with the provided credentials. Please make sure the input credentials and environment are correct.",
            )

        return alive, error_msg
