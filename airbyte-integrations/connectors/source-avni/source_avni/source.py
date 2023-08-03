#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import boto3
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import IncrementalMixin, Stream
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http import HttpStream


class AvniStream(HttpStream, ABC):

    url_base = "https://app.avniproject.org/api/"
    primary_key = "ID"
    cursor_value = None
    current_page = 0
    last_record = None

    def __init__(self, start_date: str, auth_token: str, **kwargs):
        super().__init__(**kwargs)

        self.start_date = start_date
        self.auth_token = auth_token

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        params = {"lastModifiedDateTime": self.state["last_modified_at"]}
        if next_page_token:
            params.update(next_page_token)
        return params

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:

        return {"auth-token": self.auth_token}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        data = response.json()["content"]
        if data:
            self.last_record = data[-1]

        yield from data

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[StreamData]:

        records = super().read_records(sync_mode, cursor_field, stream_slice, stream_state)
        for record in records:
            last_modified_at = record["audit"]["Last modified at"]
            record["last_modified_at"] = last_modified_at
            yield record

    def update_state(self) -> None:

        if self.last_record:
            updated_last_date = self.last_record["audit"]["Last modified at"]
            if updated_last_date > self.state["last_modified_at"]:
                self.state = {self.cursor_field: updated_last_date}
        self.last_record = None

        return None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:

        total_elements = int(response.json()["totalElements"])
        page_size = int(response.json()["pageSize"])

        if total_elements == page_size:
            self.current_page = self.current_page + 1
            return {"page": self.current_page}

        self.update_state()

        self.current_page = 0

        return None


class IncrementalAvniStream(AvniStream, IncrementalMixin, ABC):

    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        return "last_modified_at"

    @property
    def state(self) -> Mapping[str, Any]:

        if self.cursor_value:
            return {self.cursor_field: self.cursor_value}
        else:
            return {self.cursor_field: self.start_date}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self.cursor_value = value[self.cursor_field]
        self._state = value


class Subjects(IncrementalAvniStream):

    """
    This implement Subject Stream in Source Avni
    Api docs : https://avni.readme.io/docs/api-guide
    Api endpoints : https://app.swaggerhub.com/apis-docs/samanvay/avni-external/1.0.0
    """

    def path(self, **kwargs) -> str:
        return "subjects"


class ProgramEnrolments(IncrementalAvniStream):

    """
    This implement ProgramEnrolments Stream in Source Avni
    Api docs : https://avni.readme.io/docs/api-guide
    Api endpoints : https://app.swaggerhub.com/apis-docs/samanvay/avni-external/1.0.0
    """

    def path(self, **kwargs) -> str:
        return "programEnrolments"


class ProgramEncounters(IncrementalAvniStream):

    """
    This implement ProgramEncounters Stream in Source Avni
    Api docs : https://avni.readme.io/docs/api-guide
    Api endpoints : https://app.swaggerhub.com/apis-docs/samanvay/avni-external/1.0.0
    """

    def path(self, **kwargs) -> str:
        return "programEncounters"


class Encounters(IncrementalAvniStream):

    """
    This implement Encounters Stream in Source Avni
    Api docs : https://avni.readme.io/docs/api-guide
    Api endpoints : https://app.swaggerhub.com/apis-docs/samanvay/avni-external/1.0.0
    """

    def path(self, **kwargs) -> str:
        return "encounters"


class SourceAvni(AbstractSource):
    def get_client_id(self):

        url_client = "https://app.avniproject.org/idp-details"
        response = requests.get(url_client)
        response.raise_for_status()
        client = response.json()
        return client["cognito"]["clientId"]

    def get_token(self, username: str, password: str, app_client_id: str) -> str:

        """
        Avni Api Authentication : https://avni.readme.io/docs/api-guide#authentication
        AWS Cognito for authentication : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp/client/initiate_auth.html
        """

        client = boto3.client("cognito-idp", region_name="ap-south-1")
        response = client.initiate_auth(
            ClientId=app_client_id, AuthFlow="USER_PASSWORD_AUTH", AuthParameters={"USERNAME": username, "PASSWORD": password}
        )
        return response["AuthenticationResult"]["IdToken"]

    def check_connection(self, logger, config) -> Tuple[bool, any]:

        username = config["username"]
        password = config["password"]

        try:
            client_id = self.get_client_id()
        except Exception as error:
            return False, str(error) + ": Please connect With Avni Team"

        try:
            auth_token = self.get_token(username, password, client_id)
            stream_kwargs = {"auth_token": auth_token, "start_date": config["start_date"]}
            next(Subjects(**stream_kwargs).read_records(SyncMode.full_refresh))
            return True, None

        except Exception as error:
            return False, error

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        username = config["username"]
        password = config["password"]

        try:
            client_id = self.get_client_id()
        except Exception as error:
            print(str(error) + ": Please connect With Avni Team")
            raise error

        auth_token = self.get_token(username, password, client_id)

        stream_kwargs = {"auth_token": auth_token, "start_date": config["start_date"]}

        return [
            Subjects(**stream_kwargs),
            ProgramEnrolments(**stream_kwargs),
            ProgramEncounters(**stream_kwargs),
            Encounters(**stream_kwargs),
        ]
