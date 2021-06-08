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

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .auth import GitlabAuthenticator
from .streams import Groups, Projects, Milestones, Members, Labels, Branches, Commits, Issues, Users, MergeRequests, \
    Releases, Tags, Pipelines, PipelinesExtended, Jobs, Epics


class SourceGitlab(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = GitlabAuthenticator(token=config["private_token"])

        gids = list(filter(None, config["groups"].split(" ")))
        pids = list(filter(None, config["projects"].split(" ")))

        groups = Groups(authenticator=auth, api_url=config["api_url"], group_ids=gids)
        if pids:
            projects = Projects(authenticator=auth, api_url=config["api_url"], project_ids=pids, parent_stream=groups)
        else:
            projects = Projects(authenticator=auth, api_url=config["api_url"], project_ids=pids)

        pipelines = Pipelines(authenticator=auth, api_url=config["api_url"], parent_stream=projects)

        streams = [
            groups,
            projects,
            Branches(authenticator=auth, api_url=config["api_url"], parent_stream=projects, repo_url=True),
            Commits(authenticator=auth, api_url=config["api_url"], parent_stream=projects, repo_url=True),
            Issues(authenticator=auth, api_url=config["api_url"], parent_stream=projects),
            Epics(authenticator=auth, api_url=config["api_url"], parent_stream=groups),
            Jobs(authenticator=auth, api_url=config["api_url"], parent_stream=pipelines),
            Milestones(authenticator=auth, api_url=config["api_url"], parent_stream=projects, parent_similar=True),
            Milestones(authenticator=auth, api_url=config["api_url"], parent_stream=groups, parent_similar=True),
            Members(authenticator=auth, api_url=config["api_url"], parent_stream=projects, parent_similar=True),
            Members(authenticator=auth, api_url=config["api_url"], parent_stream=groups, parent_similar=True),
            Labels(authenticator=auth, api_url=config["api_url"], parent_stream=projects, parent_similar=True),
            Labels(authenticator=auth, api_url=config["api_url"], parent_stream=groups, parent_similar=True),
            MergeRequests(authenticator=auth, api_url=config["api_url"], parent_stream=projects),
            Releases(authenticator=auth, api_url=config["api_url"], parent_stream=projects),
            Tags(authenticator=auth, api_url=config["api_url"], parent_stream=projects, repo_url=True),
            pipelines,
            PipelinesExtended(authenticator=auth, api_url=config["api_url"], parent_stream=pipelines),
            Users(authenticator=auth, api_url=config["api_url"], parent_stream=projects),
        ]

        return streams
