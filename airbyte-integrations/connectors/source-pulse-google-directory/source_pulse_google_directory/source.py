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
from airbyte_cdk.models import Type
from airbyte_cdk.models.airbyte_protocol import (
    AirbyteMessage,
    AirbyteStateMessage,
    AirbyteStateType,
    StreamDescriptor,
    AirbyteStreamState
)
from airbyte_cdk.models import SyncMode
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
        self.service = build('admin', 'directory_v1', credentials=credentials)

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
                customer='my_customer',
                maxResults=100,
                pageToken=page_token,
                orderBy='email',
                projection='full'
            )
            users_response = users_request.execute()

            for user in users_response.get('users', []):
                yield user

            page_token = users_response.get('nextPageToken')
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
            groups_request = self.service.groups().list(
                customer='my_customer',
                maxResults=100,
                pageToken=page_token,
                orderBy='email',
                projection='full'
            )
            groups_response = groups_request.execute()

            for group in groups_response.get('groups', []):
                yield group

            page_token = groups_response.get('nextPageToken')
            if not page_token:
                break


class OAuthAppsByUser(GooglePulseDirectoryStream):
    """
    Stream for OAuth Apps by User and the respective scopes
    """

    name = "oauth_apps_by_user"
    primary_key = "userId"

    def path(self, **kwargs) -> str:
        return f"users/{kwargs['userId']}/tokens"

    def read_records(
        self,
        sync_mode: str,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:

        self.logger.info(f"read_records: Reading OAuth apps for user: {stream_slice.get('userEmail')}")

        user_email = stream_slice.get("userEmail")
        if not user_email:
            self.logger.warning("userEmail is missing from the stream_slice. Skipping this stream_slice.")
            return

        next_page_token = stream_state.get("nextPageToken", None) if stream_state else None

        while True:
            self.logger.info(f"Fetching OAuth apps for user: {user_email}, page_token: {next_page_token}")
            tokens_request = self.service.tokens().list(userKey=user_email)
            if next_page_token:
                tokens_request.pageToken = next_page_token
            tokens_response = tokens_request.execute()

            oauth_apps = []
            for token in tokens_response.get("items", []):
                app_info = {
                    "appId": token.get("clientId", ""),
                    "appName": token.get("displayText", ""),
                    "scopes": token.get("scopes", []),
                    "anonymous": token.get("anonymous", False),
                    "nativeApp": token.get("nativeApp", False),
                    "issuedTime": token.get("issued", ""),
                    "lastAccessTime": token.get("lastAccessTime", "Never"),
                    "installationType": "user-specific",
                    "appType": "oauth",
                    "status": None,
                    "etag": None,
                }
                oauth_apps.append(app_info)

            if oauth_apps:
                self.logger.info(f"Yielding {len(oauth_apps)} OAuth apps for user: {user_email}")
                yield {
                    "userId": stream_slice.get("userId"),
                    "userEmail": stream_slice.get("userEmail"),
                    "oauthApps": oauth_apps,
                }
            else:
                self.logger.info(f"No OAuth apps found for user: {user_email}")

            next_page_token = tokens_response.get("nextPageToken")
            if not next_page_token:
                self.logger.info(f"Reached the end of the OAuth apps for user: {user_email}")
                break

    def stream_slices(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        page_token = None
        total_users = 0

        while True:
            users_request = self.service.users().list(
                customer='my_customer',
                maxResults=100,
                pageToken=page_token,
                orderBy='email'
            )
            users_response = users_request.execute()
            self.logger.info(f"stream_slices: Found {len(users_response.get('users', []))} users")
            total_users += len(users_response.get('users', []))

            for user in users_response.get('users', []):
                user_email = user.get("primaryEmail")
                if user_email:
                    self.logger.info(f"stream_slices: Yielding user: {user_email}")
                    yield {
                        "userId": user["id"],
                        "userEmail": user_email,
                        "nextPageToken": page_token
                    }
                else:
                    self.logger.warning(f"Skipping user with missing primaryEmail: {user}")

            page_token = users_response.get("nextPageToken")
            if not page_token:
                self.logger.info(f"stream_slices: Total users found: {total_users}")
                break


class IncrementalGooglePulseDirectoryStream(GooglePulseDirectoryStream, IncrementalMixin, ABC):
    """Base class for incremental streams in Google Directory"""

    state_checkpoint_interval = 100  # Save state every 100 records

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state[self.cursor_field] = value[self.cursor_field]

    @staticmethod
    def _emit_state_message(stream_name: str, state: Mapping[str, Any]) -> AirbyteMessage:
        """Create proper per-stream state message for Airbyte protocol"""
        return AirbyteMessage(
            type=Type.STATE,
            state=AirbyteStateMessage(
                type=AirbyteStateType.STREAM,
                stream=AirbyteStreamState(
                    stream_descriptor=StreamDescriptor(
                        name=stream_name
                    ),
                    stream_state=state
                )
            )
        )

    # @abstractmethod
    # def get_updated_state(
    #         self,
    #         current_stream_state: MutableMapping[str, Any],
    #         latest_record: Mapping[str, Any]
    # ) -> Mapping[str, Any]:
    #     """
    #     Abstract method to be implemented by concrete classes
    #     to define their own state update logic
    #     """
    #     pass


class IncrementalUsers(IncrementalGooglePulseDirectoryStream):
    """Incremental stream for Users based on etags"""

    name = "users_incremental"
    primary_key = "id"
    cursor_field = "etag"

    @property
    def state_checkpoint_interval(self) -> int:
        return 100

    @property
    def supported_sync_modes(self) -> List[SyncMode]:
        from airbyte_cdk.models import SyncMode
        return [SyncMode.full_refresh, SyncMode.incremental]

    def path(self, **kwargs) -> str:
        return "users"

    def _should_emit(self, record: Mapping[str, Any], stream_state: Mapping[str, Any]) -> bool:
        """Determine if the record should be emitted based on etag comparison"""
        if not stream_state or 'user_etags' not in stream_state:
            return True

        user_id = record.get('id')
        current_etag = record.get('etag')
        previous_etag = stream_state.get('user_etags', {}).get(user_id)

        should_emit = previous_etag is None or previous_etag != current_etag
        self.logger.info(f"Comparing etags for user {user_id}: {previous_etag} vs {current_etag} -> {should_emit}")

        return should_emit

    # def get_updated_state(
    #         self,
    #         current_stream_state: MutableMapping[str, Any],
    #         latest_record: Mapping[str, Any]
    # ) -> Mapping[str, Any]:
    #     """Calculate new state based on latest record without modifying current state"""
    #     new_state = {
    #         # TODO: Optimize this to avoid copying the entire state
    #         'user_etags': current_stream_state.get('user_etags', {}).copy()
    #     }
    #
    #     user_id = latest_record.get('id')
    #     latest_etag = latest_record.get('etag')
    #
    #     if user_id and latest_etag:
    #         new_state['user_etags'][user_id] = latest_etag
    #
    #     return new_state

    def read_records(
            self,
            sync_mode: str,
            cursor_field: List[str] = None,
            stream_slice: Mapping[str, Any] = None,
            stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        self.logger.info(f"Starting read_records with sync_mode={sync_mode}, cursor_field={cursor_field}, stream_state={stream_state}")

        # Extract state from the incoming state message format
        if isinstance(stream_state, dict):
            if "data" in stream_state:
                stream_state = stream_state.get("data", {}).get("stream", {}).get("stream_state", {})
            elif "stream" in stream_state:
                stream_state = stream_state.get("stream", {}).get("stream_state", {})

        current_state = stream_state or {}
        self.logger.info(f"Initial state: {current_state}")

        page_token = None
        records_processed = 0

        while True:
            try:
                request = self.service.users().list(
                    customer='my_customer',
                    maxResults=100,
                    pageToken=page_token,
                    orderBy='email'
                )
                response = request.execute()
                users = response.get('users', [])
                self.logger.info(f"Fetched {len(users)} users")

                for user in users:
                    # Always update state for every user we see
                    current_state = self.get_updated_state(current_state, user)

                    if sync_mode == "incremental":
                        if self._should_emit(user, stream_state):  # Note: comparing against original state
                            records_processed += 1

                            if records_processed % self.state_checkpoint_interval == 0:
                                state_msg = self._emit_state_message(self.name, current_state)
                                self.logger.info(f"Emitting state checkpoint: {current_state}")
                                yield state_msg

                            yield user
                    else:
                        yield user

                page_token = response.get('nextPageToken')
                if not page_token:
                    if sync_mode == "incremental":
                        self.logger.info(f"Emitting final state with {len(current_state.get('user_etags', {}))} users: {current_state}")
                        yield self._emit_state_message(self.name, current_state)
                    break

            except Exception as e:
                self.logger.error(f"Error in read_records loop: {str(e)}")
                raise


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
            creds = service_account.Credentials.from_service_account_info(account_info, scopes=[
                    'https://www.googleapis.com/auth/admin.directory.user.readonly',
                    'https://www.googleapis.com/auth/admin.directory.group.readonly',
                    'https://www.googleapis.com/auth/admin.directory.user.security'
                ])
            creds = creds.with_subject(admin_email)
            return creds
        except ValueError as e:
            raise ValueError(f"Invalid configuration format: {str(e)}")

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            credentials = self.create_credentials(config)
            service = build('admin', 'directory_v1', credentials=credentials)
            service.users().list(customer='my_customer', maxResults=1, orderBy='email').execute()

            return True, None

        except KeyError as e:
            return False, f"Missing required configuration parameter: {str(e)}"

        except ValueError as e:
            return False, f"Invalid configuration format: {str(e)}"

        except Exception as e:
            error_msg = str(e)
            if "invalid_grant" in error_msg.lower():
                return False, "Invalid credentials or insufficient permissions. Make sure the service account has proper access and admin_email is correct."
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

        return [
            # Regular full refresh streams
            Groups(credentials=credentials),
            Users(credentials=credentials),
            OAuthAppsByUser(credentials=credentials),
            # Incremental streams
            # IncrementalGroups(credentials=credentials),
            IncrementalUsers(credentials=credentials)
        ]
