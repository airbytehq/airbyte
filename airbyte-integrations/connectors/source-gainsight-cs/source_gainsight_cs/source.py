#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .streams import (
    GainsightCsObjectStream
)
from .authenticator import GainsightCsAuthenticator

class SourceGainsightCs(AbstractSource):

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        authenticator = GainsightCsAuthenticator(config)
        logger.info(f"Checking connection to {authenticator.domain_url}")
        try:
            url = f"{authenticator.domain_url}/v1/meta/services/objects/Person/describe?idd=true"
            response = requests.get(url, auth=authenticator)
            if response.status_code == 200:
                return True, None
            else:
                return False, f"Failed to connect to API: {response.text}"
        except requests.exceptions.RequestException as e:
            return False, e

    def get_objects(self, config):
        authenticator = GainsightCsAuthenticator(config)
        url = f"{authenticator.domain_url}/v1/meta/services/objects"
        try:
            payload = {
                "externalUse": "true",
                "sortByLabel": "false"
            }
            session = requests.post(url, json=payload, auth=authenticator)
            body = session.json()
            data = body.get("data", [])
            return [obj["objectName"] for obj in data]
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = GainsightCsAuthenticator(config)
        all_objects = self.get_objects(config)
        result = []
        for object_name in all_objects:
            result.append(GainsightCsObjectStream(name=object_name, authenticator=authenticator))
        return result
