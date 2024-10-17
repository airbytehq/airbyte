#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, List, Mapping, Tuple

import pendulum
import requests
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

from .streams import Surveys

"""
This file provides the necessary constructs to interpret a provided declarative YAML configuration file into
source connector.

WARNING: Do not modify this file.
"""


class SourceSurveymonkey(YamlDeclarativeSource):
    SCOPES = {"responses_read_detail", "surveys_read", "users_read"}

    def __init__(self):
        super().__init__(**{"path_to_yaml": "manifest.yaml"})

    @classmethod
    def _check_scopes(cls, response_json):
        granted_scopes = response_json["scopes"]["granted"]
        missed_scopes = cls.SCOPES - set(granted_scopes)
        if missed_scopes:
            return False, "missed required scopes: " + ", ".join(missed_scopes)
        return True, None

    @staticmethod
    def get_authenticator(config: Mapping[str, Any]):
        token = config.get("credentials", {}).get("access_token")
        if not token:
            token = config["access_token"]
        return TokenAuthenticator(token=token)

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        # Check scopes
        try:
            authenticator = self.get_authenticator(config)
            response = requests.get(url="https://api.surveymonkey.com/v3/users/me", headers=authenticator.get_auth_header())
            response.raise_for_status()
            return self._check_scopes(response.json())
        except Exception as e:
            return False, repr(e)

        return super().check_connection(logger, config)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        streams = super().streams(config=config)

        authenticator = self.get_authenticator(config)
        start_date = pendulum.parse(config["start_date"])
        survey_ids = config.get("survey_ids", [])
        args = {"authenticator": authenticator, "start_date": start_date, "survey_ids": survey_ids}

        streams.append(Surveys(**args))
        return streams
