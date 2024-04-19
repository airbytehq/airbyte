#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
from typing import Any, List, Mapping

import pendulum
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams.core import Stream
from airbyte_cdk.sources.streams.http.auth import BasicHttpAuthenticator

from .streams import IssueFields, Issues, PullRequests


class SourceJira(YamlDeclarativeSource):
    def __init__(self):
        super().__init__(**{"path_to_yaml": "manifest.yaml"})

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        streams = super().streams(config)
        return streams + self.get_experimental_streams(config=config)

    def _validate_and_transform_config(self, config: Mapping[str, Any]):
        start_date = config.get("start_date")
        if start_date:
            config["start_date"] = pendulum.parse(start_date)
        config["lookback_window_minutes"] = pendulum.duration(minutes=config.get("lookback_window_minutes", 0))
        config["projects"] = config.get("projects", [])
        return config

    @staticmethod
    def get_authenticator(config: Mapping[str, Any]):
        return BasicHttpAuthenticator(config["email"], config["api_token"])

    def get_experimental_streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = self._validate_and_transform_config(config.copy())
        authenticator = self.get_authenticator(config)
        args = {"authenticator": authenticator, "domain": config["domain"], "projects": config["projects"]}
        incremental_args = {
            **args,
            "start_date": config.get("start_date"),
            "lookback_window_minutes": config.get("lookback_window_minutes"),
        }
        issues_stream = Issues(**incremental_args)
        issue_fields_stream = IssueFields(**args)

        experimental_streams = []
        if config.get("enable_experimental_streams", False):
            experimental_streams.append(
                PullRequests(issues_stream=issues_stream, issue_fields_stream=issue_fields_stream, **incremental_args)
            )
        return experimental_streams
