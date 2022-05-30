#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
import socket
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from functools import partial
from typing import Any, Callable, Dict, Iterator, Mapping, Optional, Sequence

import backoff
import pendulum
import pytz
from airbyte_cdk.entrypoint import logger
from google.oauth2 import service_account
from googleapiclient.discovery import Resource, build
from googleapiclient.errors import HttpError as GoogleApiHttpError

from .utils import rate_limit_handling

SCOPES = ["https://www.googleapis.com/auth/admin.reports.audit.readonly", "https://www.googleapis.com/auth/admin.reports.usage.readonly"]


class API:
    def __init__(self, credentials_json: str, email: str, lookback: Optional[int] = None):
        self._creds = None
        self._credentials_json = credentials_json
        self._admin_email = email
        self._resource = None
        self.lookback = lookback

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
        service = build("admin", "reports_v1", credentials=self._creds)
        return service

    def _get_resource(self, name: str):
        service = self._construct_resource()
        return getattr(service, name)

    @backoff.on_exception(backoff.expo, (GoogleApiHttpError, socket.timeout), max_tries=7, giveup=rate_limit_handling)
    def get(self, name: str, params: Dict = None) -> Dict:
        if not self._resource:
            self._resource = self._get_resource(name)
        response = self._resource().list(**params).execute()
        return response


class StreamAPI(ABC):
    results_per_page = 100

    def __init__(self, api: API, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api = api
        self._start_time = None
        if self._api.lookback:
            base_start_time = datetime.utcnow() - timedelta(self._api.lookback)
            self._start_time = base_start_time.replace(tzinfo=pytz.UTC).isoformat()

    @property
    @abstractmethod
    def name(self):
        """Name of the stream"""

    def _api_get(self, resource: str, params: Dict = None):
        return self._api.get(resource, params=params)

    @abstractmethod
    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""

    @abstractmethod
    def process_response(self, response: Dict) -> Iterator[dict]:
        """Process Google Workspace Admin SDK Reports API response"""

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


class IncrementalStreamAPI(StreamAPI, ABC):
    """Stream that supports state and incremental read"""

    state_pk = "time"

    @property
    def state(self) -> Optional[Mapping[str, Any]]:
        """Current state, if wasn't set return None"""
        if self._state:
            return {self.state_pk: self._state.isoformat()}
        return None

    @state.setter
    def state(self, value):
        self._state = pendulum.parse(value[self.state_pk])
        self._start_time = self._state.to_iso8601_string()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._state = None

    def read(self, getter: Callable, params: Mapping[str, Any] = None) -> Iterator:
        """Update cursor(state)"""
        params = params or {}
        cursor = None
        for record in super().read(getter, params):
            "Report API return records from newest to oldest"
            if not cursor:
                cursor = pendulum.parse(record[self.state_pk])
            record[self.state_pk] = pendulum.parse(record[self.state_pk]).isoformat()
            yield record

        if cursor:
            new_state = max(cursor, self._state) if self._state else cursor
            if new_state != self._state:
                logger.info(f"Advancing bookmark for {self.name} stream from {self._state} to {new_state}")
                self._state = new_state


class ActivitiesAPI(IncrementalStreamAPI):
    application_name = None

    def get_params(self) -> Dict:
        params = {"userKey": "all", "applicationName": self.application_name}

        if self._start_time:
            params["startTime"] = self._start_time

        return params

    def process_response(self, response: Dict) -> Iterator[dict]:
        activities = response.get("items", [])
        for activity in activities:
            activity_id = activity.get("id", {})
            if "time" in activity_id:
                # place time property in top level
                activity["time"] = activity_id["time"]
            yield activity

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        params = self.get_params()
        yield from self.read(partial(self._api_get, resource="activities"), params=params)


class AdminAPI(ActivitiesAPI):
    name = "Admin"
    application_name = "admin"


class DriveAPI(ActivitiesAPI):
    name = "Drive"
    application_name = "drive"


class LoginsAPI(ActivitiesAPI):
    name = "Logins"
    application_name = "login"


class MeetAPI(ActivitiesAPI):
    name = "Meet"
    application_name = "meet"


class MobileAPI(ActivitiesAPI):
    name = "Mobile"
    application_name = "mobile"


class OAuthTokensAPI(ActivitiesAPI):
    name = "OAuth Tokens"
    application_name = "token"
