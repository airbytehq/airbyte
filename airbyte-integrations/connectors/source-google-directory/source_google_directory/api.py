#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
from abc import ABC, abstractmethod
from functools import partial
from typing import Any, Callable, Dict, Iterator, Mapping, Sequence

import backoff
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError as GoogleApiHttpError

from .utils import rate_limit_handling

SCOPES = ["https://www.googleapis.com/auth/admin.directory.user.readonly", "https://www.googleapis.com/auth/admin.directory.group.readonly"]


class API:
    def __init__(self, credentials: Mapping[str, Any]):
        self._creds = None
        self._raw_credentials = credentials
        self._service = None

    @staticmethod
    def _load_account_info(credentials_json: str) -> Dict:
        account_info = json.loads(credentials_json)
        return account_info

    def _obtain_service_account_creds(self) -> service_account.Credentials:
        """Obtaining creds based on Service account scenario"""
        credentials_json = self._raw_credentials.get("credentials_json")
        admin_email = self._raw_credentials.get("email")
        account_info = self._load_account_info(credentials_json)
        creds = service_account.Credentials.from_service_account_info(account_info, scopes=SCOPES)
        self._creds = creds.with_subject(admin_email)

    def _obtain_web_app_creds(self) -> Credentials:
        """Obtaining creds based on Web server application scenario"""
        info = {
            "client_id": self._raw_credentials.get("client_id"),
            "client_secret": self._raw_credentials.get("client_secret"),
            "refresh_token": self._raw_credentials.get("refresh_token"),
        }
        creds = Credentials.from_authorized_user_info(info)
        if creds.expired:
            creds.refresh(Request())
        self._creds = creds

    def _obtain_creds(self):
        if "credentials_json" in self._raw_credentials:
            self._obtain_service_account_creds()
        elif "client_id" and "client_secret" in self._raw_credentials:
            self._obtain_web_app_creds()

    def _construct_resource(self):
        if not self._creds:
            self._obtain_creds()
        if not self._service:
            self._service = build("admin", "directory_v1", credentials=self._creds)

    def _get_resource(self, name: str):
        self._construct_resource()
        return getattr(self._service, name)

    @backoff.on_exception(backoff.expo, GoogleApiHttpError, max_tries=7, giveup=rate_limit_handling)
    def get(self, name: str, params: Dict = None) -> Dict:
        resource = self._get_resource(name)
        response = resource().list(**params).execute()
        return response


class StreamAPI(ABC):
    results_per_page = 100

    def __init__(self, api: API, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api = api

    def _api_get(self, resource: str, params: Dict = None):
        return self._api.get(resource, params=params)

    @abstractmethod
    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""

    @abstractmethod
    def process_response(self, response: Dict) -> Iterator[dict]:
        """Process Google Directory API response"""

    def read(self, getter: Callable, params: Dict = None) -> Iterator:
        """Read using getter"""
        params = params or {}
        params["maxResults"] = self.results_per_page
        while True:
            batch = getter(params={**params})
            yield from self.process_response(batch)

            if "nextPageToken" in batch:
                params["pageToken"] = batch["nextPageToken"]
            else:
                break


class UsersAPI(StreamAPI):
    def process_response(self, response: Dict) -> Iterator[dict]:
        return response["users"]

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        params = {"customer": "my_customer"}
        yield from self.read(partial(self._api_get, resource="users"), params=params)


class GroupsAPI(StreamAPI):
    def process_response(self, response: Dict) -> Iterator[dict]:
        return response["groups"]

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        params = {"customer": "my_customer"}
        yield from self.read(partial(self._api_get, resource="groups"), params=params)


class GroupMembersAPI(StreamAPI):
    def process_response(self, response: Dict) -> Iterator[dict]:
        return response.get("members", [])

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        groups = GroupsAPI(self._api)
        for group in groups.list():
            params = {"groupKey": group["id"]}
            yield from self.read(partial(self._api_get, resource="members"), params=params)
