#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from functools import partial
from json import JSONDecodeError
from typing import Mapping, Tuple

import requests
from airbyte_cdk.sources.deprecated.client import BaseClient
from requests.exceptions import ConnectionError


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

    def __init__(self, api_token):
        self.headers = {"Authorization": "Bearer " + api_token}
        self.base_api_url = f"https://api.tempo.io/core/{self.API_VERSION}"
        super().__init__()

    def lists(self, name, url, params, func, **kwargs):
        while True:
            response = requests.get(f"{self.base_api_url}{url}?limit={params['limit']}&offset={params['offset']}", headers=self.headers)
            data = func(response.json())
            yield from data
            if len(data) < self.DEFAULT_ITEMS_PER_PAGE:
                break
            params["offset"] += self.DEFAULT_ITEMS_PER_PAGE

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
