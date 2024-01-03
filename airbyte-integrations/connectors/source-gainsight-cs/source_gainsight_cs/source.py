#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator

from .streams import (
    GainsightCsObjectStream
)

standard_objects = [
    "person",
    "company",
    "gsuser",
    "company_person",
    "playbook",
    "call_to_action",
    "survey_participant",
    "activity_timeline"
]

# TODO: It's hardcoded right now but we will need to implement a way to retrieve
# this info from our customers.
custom_objects = [
    "magnify_added__gc",
    "sf_1i0025dxe6kkg8jcv1zrb42nk97l9wbigcdp",
]


class GainsightCsAuthenticator(HttpAuthenticator):
    def __init__(self, token: str):
        self._token = token

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"AccessKey": self._token}


class SourceGainsightCs(AbstractSource):
    @staticmethod
    def _get_authenticator(config: Mapping[str, Any]) -> HttpAuthenticator:
        token = config.get("access_key")
        return GainsightCsAuthenticator(token)

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        domain_url = config.get("domain_url")
        url = f"{domain_url}/v1/meta/services/objects/Person/describe?idd=true"
        auth = SourceGainsightCs._get_authenticator(config)
        try:
            session = requests.get(url, headers=auth.get_auth_header())
            session.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self._get_authenticator(config)
        domain_url = config.get("domain_url")
        all_objects = standard_objects + custom_objects
        result = []
        for object_name in all_objects:
            result.append(GainsightCsObjectStream(name=object_name, domain_url=domain_url, authenticator=auth))
        return result
