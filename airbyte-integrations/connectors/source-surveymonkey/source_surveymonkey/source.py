#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

import pendulum
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .streams import SurveyPages, SurveyQuestions, SurveyResponses, Surveys


class SourceSurveymonkey(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            authenticator = TokenAuthenticator(token=config["access_token"])
            start_date = pendulum.parse(config["start_date"])
            stream = Surveys(authenticator=authenticator, start_date=start_date)
            records = stream.read_records(sync_mode=SyncMode.full_refresh)
            next(records)
            return True, None
        except Exception as e:
            return False, repr(e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = TokenAuthenticator(token=config["access_token"])
        start_date = pendulum.parse(config["start_date"])
        args = {"authenticator": authenticator, "start_date": start_date}
        return [Surveys(**args), SurveyPages(**args), SurveyQuestions(**args), SurveyResponses(**args)]
