#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator, Oauth2Authenticator

from .streams import (
    Branches,
    Commits,
    EpicIssues,
    Epics,
    GitlabStream,
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
        gids = list(filter(None, config["groups"].split(" ")))
        pids = list(filter(None, config["projects"].split(" ")))

        if not pids and not gids:
            raise Exception("Either groups or projects need to be provided for connect to Gitlab API")

        auth_params = self.get_auth_kwargs(config)
        groups = Groups(group_ids=gids, **auth_params)
        if gids:
            projects = GroupProjects(project_ids=pids, parent_stream=groups, **auth_params)
        else:
            projects = Projects(project_ids=pids, **auth_params)

        return groups, projects

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            groups, projects = self._generate_main_streams(config)
            for stream in projects.stream_slices(sync_mode=SyncMode.full_refresh):
                next(projects.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream))
            return True, None
        except Exception as error:
            return False, f"Unable to connect to Gitlab API with the provided credentials - {repr(error)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth_params = self.get_auth_kwargs(config)

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

    @staticmethod
    def get_auth_kwargs(config: Mapping[str, Any]) -> Mapping[str, Any]:
        authorization = config.get("authentication", {})

        stream_kwargs = {
            "api_url": config.get("api_url"),
        }

        auth_type = authorization.get("auth_type")
        if auth_type == "Client":
            stream_kwargs["authenticator"] = Oauth2Authenticator(
                scopes=["api"],
                token_refresh_endpoint=f"https://{stream_kwargs.get('api_url')}/oauth/token",
                client_secret=authorization.get("client_secret"),
                client_id=authorization.get("client_id"),
                refresh_token=authorization.get("refresh_token")
            )
        elif auth_type == "Token":
            stream_kwargs["authenticator"] = TokenAuthenticator(token=auth_type.get("private_token"))
        else:
            raise Exception(f"Invalid auth type: {auth_type}")

        return stream_kwargs