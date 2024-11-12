#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator
from .streams import Employees,Categories  # Import EmployeesStream from streams.py

def generate_token(config):
        url = f"https://{config['gtHost']}/uas/v1/oauth2/client-token"
        response = requests.post(url, auth=(config["username"], config["password"]))
        response.raise_for_status()
        return response.json().get("access_token")

class CustomHeadersAuthenticator(HttpAuthenticator):
    """
    A custom authenticator for injecting specific headers.
    """

    def __init__(self, custom_headers: Mapping[str, str]):
        """
        Initialize with a dictionary of custom headers.
        :param custom_headers: A dictionary containing header key-value pairs.
        """
        self.custom_headers = custom_headers

    def get_auth_header(self) -> str:
        """
        Return a placeholder or default authorization header.
        This is required but can be left empty or return a specific value based on your needs.
        """
        return self.custom_headers
    
    def get_headers(self) -> Mapping[str, str]:
        """
        Return the custom headers.
        """
        return self.custom_headers

# Source
class SourceGreythr(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            token = generate_token(config)
            return True, None
        except Exception as e:
            return False, str(e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        tokenGenrated = generate_token(config)
        custom_headers = {
            "ACCESS-TOKEN": tokenGenrated,
            "x-greythr-domain": config["gtHost"]
        }
        authenticator = CustomHeadersAuthenticator(custom_headers=custom_headers)
        return [Employees(config=config, authenticator=authenticator),Categories(config=config, authenticator=authenticator)]
