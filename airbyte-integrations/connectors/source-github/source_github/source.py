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


from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .streams import (
    Assignees,
    Collaborators,
    Comments,
    CommitComments,
    Commits,
    Events,
    IssueEvents,
    IssueLabels,
    IssueMilestones,
    Issues,
    Projects,
    PullRequests,
    Releases,
    Reviews,
    Stargazers,
    Teams,
)


class SourceGithub(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            repositories = config["repository"].split(" ")
            for repository in repositories:
                url = f"https://api.github.com/repos/{repository}/collaborators"
                response = requests.get(url, headers={"Authorization": f"token {config['access_token']}"})

                if response.status_code != 200:
                    raise Exception(
                        f'Unable to connect with the provided credentials for "{repository}" repository. '
                        f"Status code = {response.status_code}"
                    )
        except Exception as e:
            return False, e

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = TokenAuthenticator(token=config["access_token"], auth_method="token")
        args = {"authenticator": authenticator, "repository": config["repository"]}
        return [
            Assignees(**args),
            Reviews(**args),
            Collaborators(**args),
            Releases(**args),
            Events(**args),
            Comments(**args),
            PullRequests(**args),
            CommitComments(**args),
            IssueMilestones(**args),
            Commits(**args),
            Stargazers(**args),
            Teams(**args),
            Projects(**args),
            IssueLabels(**args),
            Issues(**args),
            IssueEvents(**args),
        ]
