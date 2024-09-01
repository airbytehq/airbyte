#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import pathlib
from base64 import b64encode
from typing import Any, List, Mapping

from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from streams import (
    DashboardsGenerator,
    FiltersGenerator,
    FilterSharingGenerator,
    GroupsGenerator,
    IssueCommentsGenerator,
    IssueFieldsGenerator,
    IssueRemoteLinksGenerator,
    IssuesGenerator,
    IssueVotesGenerator,
    IssueWatchersGenerator,
    ProjectCategoriesGenerator,
    ProjectComponentsGenerator,
    ProjectsGenerator,
    ProjectVersionsGenerator,
    ScreensGenerator,
    UsersGenerator,
    WorkflowSchemesGenerator,
    WorkflowsGenerator,
)


class Generator:
    base_config_path = "secrets/config.json"

    def __init__(self):
        self.configs = None
        super(Generator, self).__init__()

    def _get_configs(self):
        if not self.configs:
            source_directory = pathlib.Path(__file__).resolve().parent.parent.parent.parent
            configs_path = source_directory.joinpath(self.base_config_path)
            with open(configs_path) as json_configs:
                self.configs = json.load(json_configs)
        return self.configs

    @staticmethod
    def _get_authenticator(config: Mapping[str, Any]):
        token = b64encode(bytes(config["email"] + ":" + config["api_token"], "utf-8")).decode("ascii")
        authenticator = TokenAuthenticator(token, auth_method="Basic")
        return authenticator

    def streams(self) -> List:
        config = self._get_configs()
        authenticator = self._get_authenticator(config)
        args = {"authenticator": authenticator, "domain": config["domain"]}
        return [
            DashboardsGenerator(**args),
            FiltersGenerator(**args),
            FilterSharingGenerator(**args),
            GroupsGenerator(**args),
            IssuesGenerator(**args),
            IssueCommentsGenerator(**args),
            IssueFieldsGenerator(**args),
            IssueRemoteLinksGenerator(**args),
            IssueVotesGenerator(**args),
            IssueWatchersGenerator(**args),
            ProjectsGenerator(**args),
            ProjectCategoriesGenerator(**args),
            ProjectComponentsGenerator(**args),
            ProjectVersionsGenerator(**args),
            ScreensGenerator(**args),
            UsersGenerator(**args),
            WorkflowsGenerator(**args),
            WorkflowSchemesGenerator(**args),
        ]

    def run(self):
        for stream in self.streams():
            stream.generate()


if __name__ == "__main__":
    generator = Generator()
    generator.run()
