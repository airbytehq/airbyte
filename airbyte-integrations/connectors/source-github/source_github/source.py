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


import re
from typing import Any, List, Mapping, Tuple

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
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
    Repositories,
    Reviews,
    Stargazers,
    Teams,
)


class SourceGithub(AbstractSource):
    def _generate_repositories(self, config: Mapping[str, Any], authenticator: TokenAuthenticator) -> List[str]:
        repositories = list(filter(None, config["repository"].split(" ")))

        if not repositories:
            raise Exception("Field `repository` required to be provided for connect to Github API")

        repositories_list = [repo for repo in repositories if not re.match("^.*/\\*$", repo)]
        organizations = [org.split("/")[0] for org in repositories if org not in repositories_list]
        if organizations:
            repos = Repositories(authenticator=authenticator, organizations=organizations)
            for stream in repos.stream_slices(sync_mode=SyncMode.full_refresh):
                repositories_list += [
                    repository["full_name"] for repository in repos.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream)
                ]

        return list(set(repositories_list))

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            authenticator = TokenAuthenticator(token=config["access_token"], auth_method="token")
            repositories = self._generate_repositories(config=config, authenticator=authenticator)

            # We should use the most poorly filled stream to use the `list` method, because when using the `next` method, we can get the `StopIteration` error.
            projects_stream = Projects(authenticator=authenticator, repositories=repositories, start_date=config["start_date"])
            for stream in projects_stream.stream_slices(sync_mode=SyncMode.full_refresh):
                list(projects_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream))
            return True, None
        except Exception as e:
            return False, repr(e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = TokenAuthenticator(token=config["access_token"], auth_method="token")
        repositories = self._generate_repositories(config=config, authenticator=authenticator)
        full_refresh_args = {"authenticator": authenticator, "repositories": repositories}
        incremental_args = {**full_refresh_args, "start_date": config["start_date"]}

        return [
            Assignees(**full_refresh_args),
            Collaborators(**full_refresh_args),
            Comments(**incremental_args),
            CommitComments(**incremental_args),
            Commits(**incremental_args),
            Events(**incremental_args),
            IssueEvents(**incremental_args),
            IssueLabels(**full_refresh_args),
            IssueMilestones(**incremental_args),
            Issues(**incremental_args),
            Projects(**incremental_args),
            PullRequests(**incremental_args),
            Releases(**incremental_args),
            Reviews(**full_refresh_args),
            Stargazers(**incremental_args),
            Teams(**full_refresh_args),
        ]
