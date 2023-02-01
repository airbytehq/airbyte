#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional, Tuple

import pendulum
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import BasicHttpAuthenticator

from .streams import (
    ApplicationRoles,
    Avatars,
    BoardIssues,
    Boards,
    Dashboards,
    Filters,
    FilterSharing,
    Groups,
    IssueComments,
    IssueCustomFieldContexts,
    IssueFieldConfigurations,
    IssueFields,
    IssueLinkTypes,
    IssueNavigatorSettings,
    IssueNotificationSchemes,
    IssuePriorities,
    IssueProperties,
    IssueRemoteLinks,
    IssueResolutions,
    Issues,
    IssueSecuritySchemes,
    IssueTypeSchemes,
    IssueTypeScreenSchemes,
    IssueVotes,
    IssueWatchers,
    IssueWorklogs,
    JiraSettings,
    Labels,
    Permissions,
    PermissionSchemes,
    ProjectAvatars,
    ProjectCategories,
    ProjectComponents,
    ProjectEmail,
    ProjectPermissionSchemes,
    Projects,
    ProjectTypes,
    ProjectVersions,
    PullRequests,
    Screens,
    ScreenSchemes,
    ScreenTabFields,
    ScreenTabs,
    SprintIssues,
    Sprints,
    TimeTracking,
    Users,
    UsersGroupsDetailed,
    Workflows,
    WorkflowSchemes,
    WorkflowStatusCategories,
    WorkflowStatuses,
)
from .utils import read_full_refresh


class SourceJira(AbstractSource):
    def _validate_and_transform(self, config: Mapping[str, Any]):
        start_date = config.get("start_date")
        if start_date:
            config["start_date"] = pendulum.parse(start_date)

        config["projects"] = config.get("projects", [])
        return config

    @staticmethod
    def get_authenticator(config: Mapping[str, Any]):
        return BasicHttpAuthenticator(config["email"], config["api_token"])

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        config = self._validate_and_transform(config)
        authenticator = self.get_authenticator(config)
        kwargs = {"authenticator": authenticator, "domain": config["domain"], "projects": config["projects"]}
        labels_stream = Labels(**kwargs)
        next(read_full_refresh(labels_stream), None)
        # check projects
        projects_stream = Projects(**kwargs)
        projects = {project["key"] for project in read_full_refresh(projects_stream)}
        unknown_projects = set(config["projects"]) - projects
        if unknown_projects:
            return False, "unknown project(s): " + ", ".join(unknown_projects)
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = self._validate_and_transform(config)
        authenticator = self.get_authenticator(config)
        args = {"authenticator": authenticator, "domain": config["domain"], "projects": config["projects"]}
        incremental_args = {**args, "start_date": config.get("start_date")}
        render_fields = config.get("render_fields", False)
        issues_stream = Issues(
            **incremental_args,
            expand_changelog=config.get("expand_issue_changelog", False),
            render_fields=render_fields,
        )
        issue_fields_stream = IssueFields(**args)
        experimental_streams = []
        if config.get("enable_experimental_streams", False):
            experimental_streams.append(
                PullRequests(issues_stream=issues_stream, issue_fields_stream=issue_fields_stream, **incremental_args)
            )
        return [
            ApplicationRoles(**args),
            Avatars(**args),
            Boards(**args),
            BoardIssues(**incremental_args),
            Dashboards(**args),
            Filters(**args),
            FilterSharing(**args),
            Groups(**args),
            issues_stream,
            IssueComments(**incremental_args),
            issue_fields_stream,
            IssueFieldConfigurations(**args),
            IssueCustomFieldContexts(**args),
            IssueLinkTypes(**args),
            IssueNavigatorSettings(**args),
            IssueNotificationSchemes(**args),
            IssuePriorities(**args),
            IssueProperties(**incremental_args),
            IssueRemoteLinks(**incremental_args),
            IssueResolutions(**args),
            IssueSecuritySchemes(**args),
            IssueTypeSchemes(**args),
            IssueTypeScreenSchemes(**args),
            IssueVotes(**incremental_args),
            IssueWatchers(**incremental_args),
            IssueWorklogs(**incremental_args),
            JiraSettings(**args),
            Labels(**args),
            Permissions(**args),
            PermissionSchemes(**args),
            Projects(**args),
            ProjectAvatars(**args),
            ProjectCategories(**args),
            ProjectComponents(**args),
            ProjectEmail(**args),
            ProjectPermissionSchemes(**args),
            ProjectTypes(**args),
            ProjectVersions(**args),
            Screens(**args),
            ScreenTabs(**args),
            ScreenTabFields(**args),
            ScreenSchemes(**args),
            Sprints(**args),
            SprintIssues(**incremental_args),
            TimeTracking(**args),
            Users(**args),
            UsersGroupsDetailed(**args),
            Workflows(**args),
            WorkflowSchemes(**args),
            WorkflowStatuses(**args),
            WorkflowStatusCategories(**args),
        ] + experimental_streams
