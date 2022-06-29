#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .streams import (
    Branches,
    Commits,
    EpicIssues,
    Epics,
    GitlabStream,
    GroupIssueBoards,
    GroupLabels,
    GroupMembers,
    GroupMilestones,
    GroupProjects,
    Groups,
    Issues,
    Jobs,
    MergeRequestCommits,
    MergeRequests,
    Pipelines,
    PipelinesExtended,
    ProjectLabels,
    ProjectMembers,
    ProjectMilestones,
    Projects,
    Releases,
    Tags,
    Users,
)


class SourceGitlab(AbstractSource):
    def _generate_main_streams(self, config: Mapping[str, Any]) -> Tuple[GitlabStream, GitlabStream]:
        auth = TokenAuthenticator(token=config["private_token"])
        auth_params = dict(authenticator=auth, api_url=config["api_url"])

        pids = list(filter(None, config.get("projects", "").split(" ")))
        gids = config.get("groups")

        if gids:
            gids = list(filter(None, gids.split(" ")))
        else:
            gids = self._get_group_list(**auth_params)

        groups = Groups(group_ids=gids, **auth_params)
        if gids:
            projects = GroupProjects(project_ids=pids, parent_stream=groups, **auth_params)
        else:
            projects = Projects(project_ids=pids, **auth_params)

        return groups, projects

    def _get_group_list(self, **kwargs):
        headers = kwargs["authenticator"].get_auth_header()

        ids = []
        has_next = True
        # First request params
        per_page = 50
        next_page = 1

        while has_next:
            response = requests.get(f'https://{kwargs["api_url"]}/api/v4/groups?page={next_page}&per_page={per_page}', headers=headers)
            next_page = response.headers.get("X-Next-Page")
            per_page = response.headers.get("X-Per-Page")
            results = response.json()

            items = map(lambda i: i["full_path"].replace("/", "%2f"), results)
            ids.extend(items)
            has_next = "X-Next-Page" in response.headers and response.headers["X-Next-Page"] != ""

        return ids

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            groups, projects = self._generate_main_streams(config)
            for stream in projects.stream_slices(sync_mode=SyncMode.full_refresh):
                next(projects.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream))
            return True, None
        except Exception as error:
            return False, f"Unable to connect to Gitlab API with the provided credentials - {repr(error)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = TokenAuthenticator(token=config["private_token"])
        auth_params = dict(authenticator=auth, api_url=config["api_url"])

        groups, projects = self._generate_main_streams(config)
        pipelines = Pipelines(parent_stream=projects, start_date=config["start_date"], **auth_params)
        merge_requests = MergeRequests(parent_stream=projects, start_date=config["start_date"], **auth_params)
        epics = Epics(parent_stream=groups, **auth_params)

        streams = [
            groups,
            projects,
            Branches(parent_stream=projects, repository_part=True, **auth_params),
            Commits(parent_stream=projects, repository_part=True, start_date=config["start_date"], **auth_params),
            epics,
            EpicIssues(parent_stream=epics, **auth_params),
            GroupIssueBoards(parent_stream=groups, **auth_params),
            Issues(parent_stream=projects, start_date=config["start_date"], **auth_params),
            Jobs(parent_stream=pipelines, **auth_params),
            ProjectMilestones(parent_stream=projects, **auth_params),
            GroupMilestones(parent_stream=groups, **auth_params),
            ProjectMembers(parent_stream=projects, **auth_params),
            GroupMembers(parent_stream=groups, **auth_params),
            ProjectLabels(parent_stream=projects, **auth_params),
            GroupLabels(parent_stream=groups, **auth_params),
            merge_requests,
            MergeRequestCommits(parent_stream=merge_requests, **auth_params),
            Releases(parent_stream=projects, **auth_params),
            Tags(parent_stream=projects, repository_part=True, **auth_params),
            pipelines,
            PipelinesExtended(parent_stream=pipelines, **auth_params),
            Users(parent_stream=projects, **auth_params),
        ]

        return streams
