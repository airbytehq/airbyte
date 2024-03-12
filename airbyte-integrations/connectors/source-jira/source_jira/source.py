#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, List, Mapping, Optional, Tuple

import pendulum
import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import FailureType
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import BasicHttpAuthenticator
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from pydantic.error_wrappers import ValidationError

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
    IssueCustomFieldOptions,
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
    IssueTransitions,
    IssueTypes,
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
    ProjectRoles,
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

logger = logging.getLogger("airbyte")


class SourceJira(AbstractSource):
    def _validate_and_transform(self, config: Mapping[str, Any]):
        start_date = config.get("start_date")
        if start_date:
            config["start_date"] = pendulum.parse(start_date)
        config["lookback_window_minutes"] = pendulum.duration(minutes=config.get("lookback_window_minutes", 0))
        config["projects"] = config.get("projects", [])
        return config

    @staticmethod
    def get_authenticator(config: Mapping[str, Any]):
        return BasicHttpAuthenticator(config["email"], config["api_token"])

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        try:
            original_config = config.copy()
            config = self._validate_and_transform(config)
            authenticator = self.get_authenticator(config)
            kwargs = {"authenticator": authenticator, "domain": config["domain"], "projects": config["projects"]}

            # check projects
            projects_stream = Projects(**kwargs)
            projects = {project["key"] for project in read_full_refresh(projects_stream)}
            unknown_projects = set(config["projects"]) - projects
            if unknown_projects:
                return False, "unknown project(s): " + ", ".join(unknown_projects)

            # Get streams to check access to any of them
            streams = self.streams(original_config)
            for stream in streams:
                try:
                    next(read_full_refresh(stream), None)
                except:
                    logger.warning("No access to stream: " + stream.name)
                else:
                    logger.info(f"API Token have access to stream: {stream.name}, so check is successful.")
                    return True, None
            return False, "This API Token does not have permission to read any of the resources."
        except ValidationError as validation_error:
            return False, validation_error
        except requests.exceptions.RequestException as request_error:
            has_response = request_error.response is not None
            is_invalid_domain = (
                isinstance(request_error, requests.exceptions.InvalidURL)
                or has_response
                and request_error.response.status_code == requests.codes.not_found
            )

            if is_invalid_domain:
                raise AirbyteTracedException(
                    message="Config validation error: please check that your domain is valid and does not include protocol (e.g: https://).",
                    internal_message=str(request_error),
                    failure_type=FailureType.config_error,
                ) from None

            # sometimes jira returns non json response
            if has_response and request_error.response.headers.get("content-type") == "application/json":
                message = " ".join(map(str, request_error.response.json().get("errorMessages", "")))
                return False, f"{message} {request_error}"

            # we don't know what this is, rethrow it
            raise request_error

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = self._validate_and_transform(config)
        authenticator = self.get_authenticator(config)
        args = {"authenticator": authenticator, "domain": config["domain"], "projects": config["projects"]}
        incremental_args = {
            **args,
            "start_date": config.get("start_date"),
            "lookback_window_minutes": config.get("lookback_window_minutes"),
        }
        issues_stream = Issues(**incremental_args)
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
            IssueCustomFieldOptions(**args),
            IssueLinkTypes(**args),
            IssueNavigatorSettings(**args),
            IssueNotificationSchemes(**args),
            IssuePriorities(**args),
            IssueProperties(**incremental_args),
            IssueRemoteLinks(**incremental_args),
            IssueResolutions(**args),
            IssueSecuritySchemes(**args),
            IssueTransitions(**args),
            IssueTypeSchemes(**args),
            IssueTypes(**args),
            IssueTypeScreenSchemes(**args),
            IssueVotes(**incremental_args),
            IssueWatchers(**incremental_args),
            IssueWorklogs(**incremental_args),
            JiraSettings(**args),
            Labels(**args),
            Permissions(**args),
            PermissionSchemes(**args),
            Projects(**args),
            ProjectRoles(**args),
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
