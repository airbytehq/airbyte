#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from base64 import b64encode
from json.decoder import JSONDecodeError
from typing import Any, List, Mapping, Optional, Tuple

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .streams import (
    ApplicationRoles,
    Avatars,
    BoardIssues,
    Boards,
    Dashboards,
    Epics,
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


class SourceJira(AbstractSource):
    @staticmethod
    def get_authenticator(config: Mapping[str, Any]):
        token = b64encode(bytes(config["email"] + ":" + config["api_token"], "utf-8")).decode("ascii")
        authenticator = TokenAuthenticator(token, auth_method="Basic")
        return authenticator

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        alive = True
        error_msg = None

        try:
            authenticator = self.get_authenticator(config)
            args = {"authenticator": authenticator, "domain": config["domain"], "projects": config["projects"]}
            issue_resolutions = IssueResolutions(**args)
            for item in issue_resolutions.read_records(sync_mode=SyncMode.full_refresh):
                continue
        except ConnectionError as error:
            alive, error_msg = False, repr(error)
        # If the input domain is incorrect or doesn't exist, then the response would be empty, resulting in a
        # JSONDecodeError
        except JSONDecodeError:
            alive, error_msg = (
                False,
                "Unable to connect to the Jira API with the provided credentials. Please make sure the input "
                "credentials and environment are correct.",
            )

        return alive, error_msg

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = self.get_authenticator(config)
        args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
        incremental_args = {**args, "start_date": config.get("start_date", "")}
        render_fields = config.get("render_fields", False)
        issues_stream = Issues(
            **incremental_args,
            additional_fields=config.get("additional_fields", []),
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
            Epics(render_fields=render_fields, **incremental_args),
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
