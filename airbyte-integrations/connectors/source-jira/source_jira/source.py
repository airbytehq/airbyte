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
    Screens,
    ScreenSchemes,
    ScreenTabFields,
    ScreenTabs,
    TimeTracking,
    Users,
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
            args = {"authenticator": authenticator, "domain": config["domain"]}
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
        args = {"authenticator": authenticator, "domain": config["domain"]}
        return [
            ApplicationRoles(**args),
            Avatars(**args),
            Dashboards(**args),
            Filters(**args),
            FilterSharing(**args),
            Groups(**args),
            Issues(**args),
            IssueComments(**args),
            IssueFields(**args),
            IssueFieldConfigurations(**args),
            IssueCustomFieldContexts(**args),
            IssueLinkTypes(**args),
            IssueNavigatorSettings(**args),
            IssueNotificationSchemes(**args),
            IssuePriorities(**args),
            IssueProperties(**args),
            IssueRemoteLinks(**args),
            IssueResolutions(**args),
            IssueSecuritySchemes(**args),
            IssueTypeSchemes(**args),
            IssueTypeScreenSchemes(**args),
            IssueVotes(**args),
            IssueWatchers(**args),
            IssueWorklogs(**args),
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
            TimeTracking(**args),
            Users(**args),
            Workflows(**args),
            WorkflowSchemes(**args),
            WorkflowStatuses(**args),
            WorkflowStatusCategories(**args),
        ]
