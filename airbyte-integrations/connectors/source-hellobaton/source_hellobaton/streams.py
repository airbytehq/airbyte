#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional
from urllib.parse import parse_qs, urlparse

import requests
from airbyte_cdk.sources.streams.http import HttpStream


# Basic full refresh stream
class HellobatonStream(HttpStream, ABC):
    """
    This class represents a stream output by the connector.
    This is an abstract base class meant to contain all the common functionality at the API level e.g: the API base URL, pagination strategy,
    parsing responses etc..
    """

    page_size: int = 100
    primary_key: str = "id"

    def __init__(self, company: str, api_key: str, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self.company = company

    @property
    def url_base(self) -> str:
        """
        Using this method instead of class init to dynamically generate base url based on config
        """
        company = self.company
        return f"https://{company}.hellobaton.com/api/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Logic to generate next page token based on the response
        """

        payload = response.json()
        result_count = payload["count"]

        if result_count > self.page_size:
            query_string = urlparse(payload["next"]).query
            next_page_token = parse_qs(query_string).get("page", None)

        else:
            next_page_token = None

        return next_page_token

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        API request params which expect an api key for auth and any pagination is done using defined in the next_page_token method
        """

        params = {"api_key": self.api_key, "page_size": self.page_size, "page": next_page_token}

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        May want to add logic here to unpack foreign keys from urls but tbd
        For now each response record is accessed through the results key in the JSON payload
        """
        for results in response.json()["results"]:
            yield results


class Activity(HellobatonStream):
    """
    Activity stream class
    """

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:

        return "activity"


class Companies(HellobatonStream):
    """
    Companies stream class
    """

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:

        return "companies"


class Milestones(HellobatonStream):
    """
    Milestones stream class
    """

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:

        return "milestones"


class Phases(HellobatonStream):
    """
    Phases stream class
    """

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:

        return "phases"


class ProjectAttachments(HellobatonStream):
    """
    Project attachments stream class
    """

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:

        return "project_attachments"


class Projects(HellobatonStream):
    """
    Projects stream class
    """

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:

        return "projects"


class Tasks(HellobatonStream):
    """
    Tasks stream class
    """

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:

        return "tasks"


class TaskAttachments(HellobatonStream):
    """
    Task attachments stream class
    """

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:

        return "task_attachments"


class Templates(HellobatonStream):
    """
    Templates stream class
    """

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:

        return "templates"


class TimeEntries(HellobatonStream):
    """
    Time entries stream class
    """

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:

        return "time_entries"


class Users(HellobatonStream):
    """
    Users stream class
    """

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:

        return "users"
