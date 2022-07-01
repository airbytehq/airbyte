#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

import pendulum
import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .streams import SurveyPages, SurveyQuestions, SurveyResponses, Surveys


class SourceSurveymonkey(AbstractSource):

    SCOPES = {"responses_read_detail", "surveys_read", "users_read"}

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        url = "https://api.surveymonkey.com/v3/users/me"
        authenticator = self.get_authenticator(config)
        try:
            response = requests.get(url=url, headers=authenticator.get_auth_header())
            response.raise_for_status()
            return self._check_scopes(response.json())
        except Exception as e:
            return False, repr(e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = self.get_authenticator(config)
        start_date = pendulum.parse(config["start_date"])
        survey_ids = config.get("survey_ids", [])
        args = {"authenticator": authenticator, "start_date": start_date, "survey_ids": survey_ids}
        return [Surveys(**args), SurveyPages(**args), SurveyQuestions(**args), SurveyResponses(**args)]

    @staticmethod
    def get_authenticator(config: Mapping[str, Any]):
        token = config["access_token"]
        return TokenAuthenticator(token=token)

    @classmethod
    def _check_scopes(cls, response_json):
        granted_scopes = response_json["scopes"]["granted"]
        missed_scopes = cls.SCOPES - set(granted_scopes)
        if missed_scopes:
            return False, "missed required scopes: " + ", ".join(missed_scopes)
        return True, None
