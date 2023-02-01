#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from itertools import groupby
from operator import itemgetter
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

    @classmethod
    def _check_credentials(cls, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        # check if the credentials are provided correctly, because for now these value are not required in spec
        if not config.get("access_token"):
            credentials = config.get("credentials", {})
            if not credentials:
                return False, "credentials fields are not provided"
            else:
                if not credentials.get("auth_method"):
                    return False, "auth_method in credentials is not provided"

                if not credentials.get("access_token"):
                    return False, "access_token in credentials is not provided"

                if not credentials.get("client_id"):
                    return False, "client_id in credentials is not provided"

                if not credentials.get("client_secret"):
                    return False, "client_secret in credentials is not provided"
        return True, None

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        is_valid_credentials, msg = self._check_credentials(config)
        if not is_valid_credentials:
            return is_valid_credentials, msg

        authenticator = self.get_authenticator(config)
        if "survey_ids" in config:
            # Check whether survey id exists and collect errors
            errors = []
            for survey_id in config["survey_ids"]:
                response = requests.head(
                    url=f"https://api.surveymonkey.com/v3/surveys/{survey_id}/details", headers=authenticator.get_auth_header()
                )
                try:
                    response.raise_for_status()
                except requests.exceptions.HTTPError:
                    errors.append((survey_id, f"{response.status_code} {response.reason}"))
            if errors:
                # Group survey ids by their error type
                survey_id_index, error_message_index = 0, 1
                msg = "; ".join(
                    [
                        f"{error_type}: {', '.join(list(map(itemgetter(survey_id_index), survey_ids)))}"
                        for error_type, survey_ids in groupby(errors, lambda x: x[error_message_index])
                    ]
                )
                return False, msg
        try:
            response = requests.get(url="https://api.surveymonkey.com/v3/users/me", headers=authenticator.get_auth_header())
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
        token = config.get("credentials", {}).get("access_token")
        if not token:
            token = config["access_token"]
        return TokenAuthenticator(token=token)

    @classmethod
    def _check_scopes(cls, response_json):
        granted_scopes = response_json["scopes"]["granted"]
        missed_scopes = cls.SCOPES - set(granted_scopes)
        if missed_scopes:
            return False, "missed required scopes: " + ", ".join(missed_scopes)
        return True, None
