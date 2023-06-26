#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import os
from typing import Any, List, Mapping, MutableMapping, Optional, Tuple, Union

import pendulum
from airbyte_cdk.config_observation import emit_configuration_as_airbyte_control_message
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth.oauth import SingleUseRefreshTokenOauth2Authenticator
from airbyte_cdk.sources.streams.http.requests_native_auth.token import TokenAuthenticator
from requests.auth import AuthBase

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
    GroupsList,
    IncludeDescendantGroups,
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
from .utils import parse_url


class SingleUseRefreshTokenGitlabOAuth2Authenticator(SingleUseRefreshTokenOauth2Authenticator):
    def __init__(self, *args, created_at_name: str = "created_at", **kwargs):
        super().__init__(*args, **kwargs)
        self._created_at_name = created_at_name

    def get_created_at_name(self) -> str:
        return self._created_at_name

    def get_access_token(self) -> str:
        if self.token_has_expired():
            new_access_token, access_token_expires_in, access_token_created_at, new_refresh_token = self.refresh_access_token()
            new_token_expiry_date = self.get_new_token_expiry_date(access_token_expires_in, access_token_created_at)
            self.access_token = new_access_token
            self.set_refresh_token(new_refresh_token)
            self.set_token_expiry_date(new_token_expiry_date)
            emit_configuration_as_airbyte_control_message(self._connector_config)
        return self.access_token

    @staticmethod
    def get_new_token_expiry_date(access_token_expires_in: int, access_token_created_at: int) -> pendulum.DateTime:
        return pendulum.from_timestamp(access_token_created_at + access_token_expires_in)

    def refresh_access_token(self) -> Tuple[str, int, int, str]:
        response_json = self._get_refresh_access_token_response()
        return (
            response_json[self.get_access_token_name()],
            response_json[self.get_expires_in_name()],
            response_json[self.get_created_at_name()],
            response_json[self.get_refresh_token_name()],
        )


def get_authenticator(config: MutableMapping) -> AuthBase:
    if config["credentials"]["auth_type"] == "access_token":
        return TokenAuthenticator(token=config["credentials"]["access_token"])
    return SingleUseRefreshTokenGitlabOAuth2Authenticator(config, token_refresh_endpoint=f"https://{config['api_url']}/oauth/token")


class SourceGitlab(AbstractSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__auth_params: Mapping[str, Any] = {}
        self.__groups_stream: Optional[GitlabStream] = None
        self.__projects_stream: Optional[GitlabStream] = None

    @staticmethod
    def _ensure_default_values(config: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        config["api_url"] = config.get("api_url") or "gitlab.com"
        return config

    def _groups_stream(self, config: MutableMapping[str, Any]) -> Groups:
        if not self.__groups_stream:
            auth_params = self._auth_params(config)
            group_ids = list(map(lambda x: x["id"], self._get_group_list(config)))
            self.__groups_stream = Groups(group_ids=group_ids, **auth_params)
        return self.__groups_stream

    def _projects_stream(self, config: MutableMapping[str, Any]) -> Union[Projects, GroupProjects]:
        if not self.__projects_stream:
            auth_params = self._auth_params(config)
            project_ids = list(filter(None, config.get("projects", "").split(" ")))
            groups_stream = self._groups_stream(config)
            if groups_stream.group_ids:
                self.__projects_stream = GroupProjects(project_ids=project_ids, parent_stream=groups_stream, **auth_params)
                return self.__projects_stream
            self.__projects_stream = Projects(project_ids=project_ids, **auth_params)
        return self.__projects_stream

    def _auth_params(self, config: MutableMapping[str, Any]) -> Mapping[str, Any]:
        if not self.__auth_params:
            auth = get_authenticator(config)
            self.__auth_params = dict(authenticator=auth, api_url=config["api_url"])
        return self.__auth_params

    def _get_group_list(self, config: MutableMapping[str, Any]) -> List[str]:
        group_ids = list(filter(None, config.get("groups", "").split(" ")))
        # Gitlab exposes different APIs to get a list of groups.
        # We use https://docs.gitlab.com/ee/api/groups.html#list-groups in case there's no group IDs in the input config.
        # This API provides full information about all available groups, including subgroups.
        #
        # In case there is a definitive list of groups IDs in the input config, the above API can not be used since
        # it does not support filtering by group ID, so we use
        # https://docs.gitlab.com/ee/api/groups.html#details-of-a-group and
        # https: //docs.gitlab.com/ee/api/groups.html#list-a-groups-descendant-groups for each group ID. The latter one does not
        # provide full group info so can only be used to retrieve  alist of group IDs and pass it further to init a corresponding stream.
        auth_params = self._auth_params(config)
        stream = GroupsList(**auth_params) if not group_ids else IncludeDescendantGroups(group_ids=group_ids, **auth_params)
        for stream_slice in stream.stream_slices(sync_mode=SyncMode.full_refresh):
            yield from stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)

    @staticmethod
    def _is_http_allowed() -> bool:
        return os.environ.get("DEPLOYMENT_MODE", "").upper() != "CLOUD"

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        config = self._ensure_default_values(config)
        is_valid, scheme, _ = parse_url(config["api_url"])
        if not is_valid:
            return False, "Invalid API resource locator."
        if scheme == "http" and not self._is_http_allowed():
            return False, "Http scheme is not allowed in this environment. Please use `https` instead."
        try:
            projects = self._projects_stream(config)
            for stream_slice in projects.stream_slices(sync_mode=SyncMode.full_refresh):
                next(projects.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice))
                return True, None
            return True, None  # in case there's no projects
        except Exception as error:
            return False, f"Unable to connect to Gitlab API with the provided credentials - {repr(error)}"

    def streams(self, config: MutableMapping[str, Any]) -> List[Stream]:
        config = self._ensure_default_values(config)
        auth_params = self._auth_params(config)

        groups, projects = self._groups_stream(config), self._projects_stream(config)
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
