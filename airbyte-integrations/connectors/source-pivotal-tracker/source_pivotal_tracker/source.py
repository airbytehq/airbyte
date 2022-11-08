#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator


class PivotalTrackerStream(HttpStream, ABC):

    url_base = "https://www.pivotaltracker.com/services/v5/"
    primary_key = "id"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:

        headers = response.headers
        if "X-Tracker-Pagination-Total" not in headers:
            return None  # not paginating

        page_size = int(headers["X-Tracker-Pagination-Limit"])
        records_returned = int(headers["X-Tracker-Pagination-Returned"])
        current_offset = int(headers["X-Tracker-Pagination-Offset"])

        if records_returned < page_size:
            return None  # no more

        return {"offset": current_offset + page_size}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params: MutableMapping[str, Any] = {}
        if next_page_token:
            params["offset"] = next_page_token["offset"]
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # print(response.json())
        for record in response.json():  # everything is in a list
            yield record


class Projects(PivotalTrackerStream):
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "projects"


class ProjectBasedStream(PivotalTrackerStream):
    @property
    @abstractmethod
    def subpath(self) -> str:
        """
        Within the project. For example, "stories" producing:
        https://www.pivotaltracker.com/services/v5/projects/{project_id}/stories
        """

    def __init__(self, project_ids: List[str], **kwargs):
        super().__init__(**kwargs)
        self.project_ids = project_ids

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"projects/{stream_slice['project_id']}/{self.subpath}"

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        for project_id in self.project_ids:
            yield {"project_id": project_id}


class Stories(ProjectBasedStream):
    subpath = "stories"


class ProjectMemberships(ProjectBasedStream):
    subpath = "memberships"


class Labels(ProjectBasedStream):
    subpath = "labels"


class Releases(ProjectBasedStream):
    subpath = "releases"


class Epics(ProjectBasedStream):
    subpath = "epics"


class Activity(ProjectBasedStream):
    subpath = "activity"
    primary_key = "guid"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for record in super().parse_response(response, **kwargs):
            if "project" in record:
                record["project_id"] = record["project"]["id"]
            yield record


# Custom token authenticator because no "Bearer"
class PivotalAuthenticator(HttpAuthenticator):
    def __init__(self, token: str):
        self._token = token

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"X-TrackerToken": self._token}


# Source
class SourcePivotalTracker(AbstractSource):
    @staticmethod
    def _get_authenticator(config: Mapping[str, Any]) -> HttpAuthenticator:
        token = config.get("api_token")
        return PivotalAuthenticator(token)

    @staticmethod
    def _generate_project_ids(auth: HttpAuthenticator) -> List[str]:
        """
        Args:
            config (dict): Dict representing connector's config
        Returns:
            List[str]: List of project ids accessible by the api_token
        """

        projects = Projects(authenticator=auth)
        records = projects.read_records(SyncMode.full_refresh)
        project_ids: List[str] = []
        for record in records:
            project_ids.append(record["id"])
        return project_ids

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        auth = SourcePivotalTracker._get_authenticator(config)
        self._generate_project_ids(auth)
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self._get_authenticator(config)
        project_ids = self._generate_project_ids(auth)
        project_args = {"project_ids": project_ids, "authenticator": auth}
        return [
            Projects(authenticator=auth),
            Stories(**project_args),
            ProjectMemberships(**project_args),
            Labels(**project_args),
            Releases(**project_args),
            Epics(**project_args),
            Activity(**project_args),
        ]
