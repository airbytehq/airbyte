#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator
from airbyte_cdk.models import SyncMode


class PivotalTrackerStream(HttpStream, ABC):

    url_base = "https://www.pivotaltracker.com/services/v5/"
    primary_key = "id"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        TODO: Override this method to define a pagination strategy. If you will not be using pagination, no action is required - just return None.

        This method should return a Mapping (e.g: dict) containing whatever information required to make paginated requests. This dict is passed
        to most other methods in this class to help you form headers, request bodies, query params, etc..

        For example, if the API accepts a 'page' parameter to determine which page of the result to return, and a response from the API contains a
        'page' number, then this method should probably return a dict {'page': response.json()['page'] + 1} to increment the page count by 1.
        The request_params method should then read the input next_page_token and set the 'page' param to next_page_token['page'].

        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        TODO: Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """
        return {}

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

    # TODO: cursor_field = "updated_at"
    # TODO: get_updated_state
    subpath = "stories"


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
        return [Projects(authenticator=auth), Stories(project_ids, authenticator=auth)]
