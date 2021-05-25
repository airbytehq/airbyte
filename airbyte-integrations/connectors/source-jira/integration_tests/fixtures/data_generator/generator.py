#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import json
import pathlib
from base64 import b64encode
from typing import Any, List, Mapping

from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
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
