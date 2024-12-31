#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
import json
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources.streams import IncrementalMixin
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.models.airbyte_protocol import (
    Type,
    AirbyteMessage,
    AirbyteStateMessage,
    AirbyteStateType,
    StreamDescriptor,
    AirbyteStreamState,
    SyncMode,
)
from googleapiclient.discovery import build
from google.oauth2 import service_account


# TODO: Add my_customer constant to the base class


class GooglePulseDirectoryStream(HttpStream, ABC):
    """Base stream for Google Directory API"""

    """
    This class represents a stream output by the connector.
    This is an abstract base class meant to contain all the common functionality at the API level e.g: the API base URL, pagination strategy,
    parsing responses etc..

    Each stream should extend this class (or another abstract subclass of it) to specify behavior unique to that stream.

    Typically for REST APIs each stream corresponds to a resource in the API. For example if the API
    contains the endpoints
        - GET v1/customers
        - GET v1/employees

    then you should have three classes:
    `class GoogleDirectoryV2Stream(HttpStream, ABC)` which is the current class
    `class Customers(GoogleDirectoryV2Stream)` contains behavior to pull data for customers using v1/customers
    `class Employees(GoogleDirectoryV2Stream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalGoogleDirectoryV2Stream((GoogleDirectoryV2Stream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    url_base = "https://admin.googleapis.com/admin/directory/v1/"

    def __init__(self, credentials: service_account.Credentials):
        super().__init__()
        self.service = build("admin", "directory_v1", credentials=credentials)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        This method should return a Mapping (e.g: dict) containing whatever information required to make paginated requests. This dict is passed
        to most other methods in this class to help you form headers, request bodies, query params, etc..

        For example, if the API accepts a 'page' parameter to determine which page of the result to return, and a response from the API contains a
        'page' number, then this method should probably return a dict {'page': response.json()['page'] + 1} to increment the page count by 1.
        The request_params method should then read the input next_page_token and set the 'page' param to next_page_token['page'].

        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """

        """
        In Airbyte's CDK, there are two main ways to handle pagination:

        Using HttpStream with requests.Response (the default approach)
        Custom pagination using your own logic (which we need for the Google API client)
        
        Since we're using the Google API client library and not making raw HTTP requests,
        we don't need to implement next_page_token with requests.Response
        """
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Required by HttpStream but not used since we're using Google API client
        """
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        We still need to implement this method from HttpStream,
        but since we're not using direct HTTP responses, we'll return empty
        """
        yield from []


class Users(GooglePulseDirectoryStream):
    """
    Stream for Google Workspace Directory Users
    """

    name = "users"
    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "users"  # Required by HttpStream but not actually used

    def read_records(
        self,
        sync_mode: str,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        page_token = None

        while True:
            users_request = self.service.users().list(
                customer="my_customer", maxResults=100, pageToken=page_token, orderBy="email", projection="full"
            )
            users_response = users_request.execute()

            for user in users_response.get("users", []):
                yield user

            page_token = users_response.get("nextPageToken")
            if not page_token:
                break


class Groups(GooglePulseDirectoryStream):
    """
    Stream for Google Workspace Groups
    """

    name = "groups"
    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "groups"  # Required by HttpStream but not actually used

    def read_records(
        self,
        sync_mode: str,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        page_token = None

        while True:
            groups_request = self.service.groups().list(customer="my_customer", maxResults=100, pageToken=page_token, orderBy="email")
            groups_response = groups_request.execute()

            for group in groups_response.get("groups", []):
                yield group

            page_token = groups_response.get("nextPageToken")
            if not page_token:
                break


class Roles(GooglePulseDirectoryStream):
    """
    Stream for Google Workspace Roles
    """

    name = "roles"
    primary_key = "roleId"

    def path(self, **kwargs) -> str:
        return "roles"  # Required by HttpStream but not actually used

    def read_records(
        self,
        sync_mode: str,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        page_token = None

        while True:
            roles_request = self.service.roles().list(customer="my_customer", maxResults=100, pageToken=page_token)
            roles_response = roles_request.execute()

            for group in roles_response.get("items", []):
                yield group

            page_token = roles_response.get("nextPageToken")
            if not page_token:
                break


class RoleAssignments(GooglePulseDirectoryStream):
    """
    Stream for Google Workspace RoleAssignments
    """

    name = "roleAssignments"
    primary_key = "roleAssignmentId"

    def path(self, **kwargs) -> str:
        return "roles"  # Required by HttpStream but not actually used

    def read_records(
        self,
        sync_mode: str,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        page_token = None

        while True:
            role_assignments_request = self.service.roleAssignments().list(customer="my_customer", maxResults=100, pageToken=page_token)
            role_assignments_response = role_assignments_request.execute()

            for group in role_assignments_response.get("items", []):
                yield group

            page_token = role_assignments_response.get("nextPageToken")
            if not page_token:
                break


class Tokens(GooglePulseDirectoryStream):
    """
    Stream for Google Workspace Tokens
    """

    name = "tokens"
    primary_key = "userKey"

    def __init__(self, parent: Users, **kwargs):
        super().__init__(**kwargs)
        self.parent = parent

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        for user in self.parent.read_records(sync_mode=SyncMode.full_refresh):
            yield {"user_id": user["id"]}

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        user_id = stream_slice["user_id"]
        return f"users/{user_id}/tokens"  # Required by HttpStream but not actually used

    def read_records(
        self,
        sync_mode: str,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        page_token = None
        user_id = stream_slice["user_id"]

        while True:
            tokes_request = self.service.tokens().list(userKey=user_id)
            tokens_response = tokes_request.execute()

            for group in tokens_response.get("items", []):
                yield group

            page_token = tokens_response.get("nextPageToken")
            if not page_token:
                break


class Asps(GooglePulseDirectoryStream):
    """
    Stream for Google Workspace Tokens
    """

    name = "asps"
    primary_key = "userKey"

    def __init__(self, parent: Users, **kwargs):
        super().__init__(**kwargs)
        self.parent = parent

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        for user in self.parent.read_records(sync_mode=SyncMode.full_refresh):
            yield {"user_id": user["id"]}

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        user_id = stream_slice["user_id"]
        return f"users/{user_id}/asps"  # Required by HttpStream but not actually used

    def read_records(
        self,
        sync_mode: str,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        page_token = None
        user_id = stream_slice["user_id"]

        while True:
            asps_request = self.service.asps().list(userKey=user_id)
            asps_response = asps_request.execute()

            for group in asps_response.get("items", []):
                yield group

            page_token = asps_response.get("nextPageToken")
            if not page_token:
                break


class SourcePulseGoogleDirectory(AbstractSource):
    """
    Google Directory API Source
    """

    @staticmethod
    def create_credentials(config: Mapping[str, Any]) -> service_account.Credentials:
        required_keys = ["credentials_json", "admin_email"]
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required configuration parameter: {key}")

        try:
            credentials_json = config.get("credentials_json")
            admin_email = config["admin_email"]
            account_info = json.loads(credentials_json)
            creds = service_account.Credentials.from_service_account_info(
                account_info,
                scopes=[
                    "https://www.googleapis.com/auth/admin.directory.user.readonly",
                    "https://www.googleapis.com/auth/admin.directory.group.readonly",
                    "https://www.googleapis.com/auth/admin.directory.user.security",
                    "https://www.googleapis.com/auth/admin.directory.rolemanagement.readonly",
                ],
            )
            creds = creds.with_subject(admin_email)
            return creds
        except ValueError as e:
            raise ValueError(f"Invalid configuration format: {str(e)}")

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            credentials = self.create_credentials(config)
            service = build("admin", "directory_v1", credentials=credentials)
            service.users().list(customer="my_customer", maxResults=1, orderBy="email").execute()

            return True, None

        except KeyError as e:
            return False, f"Missing required configuration parameter: {str(e)}"

        except ValueError as e:
            return False, f"Invalid configuration format: {str(e)}"

        except Exception as e:
            error_msg = str(e)
            if "invalid_grant" in error_msg.lower():
                return (
                    False,
                    "Invalid credentials or insufficient permissions. Make sure the service account has proper access and admin_email is correct.",
                )
            elif "access_denied" in error_msg.lower():
                return False, "Access denied. Check if the service account has the required permissions and admin_email is correct."
            elif "invalid_client" in error_msg.lower():
                return False, "Invalid client configuration. Check your service account credentials."
            else:
                return False, f"Unable to connect to Google Directory API: {error_msg}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        try:
            credentials = self.create_credentials(config)
        except ValueError as e:
            raise ValueError(f"Invalid configuration format: {str(e)}")

        users_stream = Users(credentials=credentials)

        return [
            # Regular full refresh streams
            Groups(credentials=credentials),
            Roles(credentials=credentials),
            RoleAssignments(credentials=credentials),
            OAuthAppsByUser(credentials=credentials),
            Tokens(credentials=credentials, parent=users_stream),
            Asps(credentials=credentials, parent=users_stream),
        ]
