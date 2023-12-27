#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator

from .streams import (
    GainsightCsStream,
    Person,
    Company,
    User,
    CompanyPerson,
    ActivityTimeline,
    CallToAction,
    SurveyParticipant,
    Playbook
)


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
        return [
            Person(domain_url=domain_url, authenticator=auth),
            Company(domain_url=domain_url, authenticator=auth),
            User(domain_url=domain_url, authenticator=auth),
            CompanyPerson(domain_url=domain_url, authenticator=auth),
            ActivityTimeline(domain_url=domain_url, authenticator=auth),
            CallToAction(domain_url=domain_url, authenticator=auth),
            SurveyParticipant(domain_url=domain_url, authenticator=auth),
            Playbook(domain_url=domain_url, authenticator=auth)
        ]
