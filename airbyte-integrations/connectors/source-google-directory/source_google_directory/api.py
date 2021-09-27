#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
from abc import ABC, abstractmethod
from functools import partial
from typing import Callable, Dict, Iterator, Sequence

import backoff
from google.oauth2 import service_account
from googleapiclient.discovery import Resource, build
from googleapiclient.errors import HttpError as GoogleApiHttpError

from .utils import rate_limit_handling

SCOPES = ["https://www.googleapis.com/auth/admin.directory.user.readonly", "https://www.googleapis.com/auth/admin.directory.group.readonly"]


class API:
    def __init__(self, credentials_json: str, email: str):
        self._creds = None
        self._credentials_json = credentials_json
        self._admin_email = email

    def _load_account_info(self) -> Dict:
        account_info = json.loads(self._credentials_json)
        return account_info

    def _obtain_creds(self) -> service_account.Credentials:
        account_info = self._load_account_info()
        creds = service_account.Credentials.from_service_account_info(account_info, scopes=SCOPES)
        self._creds = creds.with_subject(self._admin_email)

    def _construct_resource(self) -> Resource:
        if not self._creds:
            self._obtain_creds()
        service = build("admin", "directory_v1", credentials=self._creds)
        return service

    def _get_resource(self, name: str):
        service = self._construct_resource()
        return getattr(service, name)

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
        return response["members"]

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        groups = GroupsAPI(self._api)
        for group in groups.list():
            params = {"groupKey": group["id"]}
            yield from self.read(partial(self._api_get, resource="members"), params=params)
