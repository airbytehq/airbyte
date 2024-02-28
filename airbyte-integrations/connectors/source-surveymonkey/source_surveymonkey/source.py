#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping

import pendulum
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .streams import Surveys

"""
This file provides the necessary constructs to interpret a provided declarative YAML configuration file into
source connector.

WARNING: Do not modify this file.
"""


class SourceSurveymonkey(YamlDeclarativeSource):
    def __init__(self):
        super().__init__(**{"path_to_yaml": "manifest.yaml"})

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        streams = super().streams(config=config)

        token = config.get("credentials", {}).get("access_token")
        start_date = pendulum.parse(config["start_date"])
        survey_ids = config.get("survey_ids", [])
        args = {"authenticator": TokenAuthenticator(token=token), "start_date": start_date, "survey_ids": survey_ids}

        streams.append(Surveys(**args))
        return streams
