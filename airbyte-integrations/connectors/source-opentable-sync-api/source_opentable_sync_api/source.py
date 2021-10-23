#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from datetime import datetime, time
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator, Oauth2Authenticator


def get_endpoint(is_sandbox: bool = False) -> str:
    if is_sandbox:
        endpoint = "https://platform.otqa.com"
    else:
        endpoint = "https://platform.opentable.com"
    return endpoint


def get_oauth_endpoint(is_sandbox: bool = False) -> str:
    if is_sandbox:
        endpoint = "https://oauth-pp.opentable.com"
    else:
        endpoint = "https://oauth.opentable.com"
    return endpoint


# Basic full refresh stream
class OpentableSyncAPIStream(HttpStream, ABC):
    page_size = "1000"  # API limit

    def __init__(self, authenticator: HttpAuthenticator, rid_list: str, start_date: datetime, is_sandbox: bool = False, **kwargs):
        self.now = datetime.now().replace(microsecond=0)
        self.is_sandbox = is_sandbox
        self.rid_list = rid_list
        self.start_date = start_date
        super().__init__(authenticator=authenticator)

    @property
    def url_base(self) -> str:
        return f"{get_endpoint(self.is_sandbox)}/sync/v2/"

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {"Content-Type": "application/json"}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        decoded_response = response.json()
        nextPageUrl = decoded_response.get("nextPageUrl")
        hasNextPage = decoded_response.get("hasNextPage")
        if hasNextPage:
            return {"nextPageUrl": nextPageUrl}
        else:
            return None

    def stream_slices(self, stream_state: Mapping[str, Any], **kwargs):
        for rid in self.rid_list.split(","):
            yield {"rid": rid, "start_date": self.start_date}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        updated_after = stream_slice["start_date"].strftime("%Y-%m-%dT%H:%M:%SZ")
        if next_page_token:
            params = next_page_token["nextPageUrl"].split("?")
            list_of_params = params[1].split("&")
            for param in list_of_params:
                if "updated_after" in param:
                    updated_after = param.split("=")[1]

        return {"offset": 0, "limit": 1000, "rid": stream_slice["rid"], "updated_after": updated_after}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        print("Calling endpoint " + str(response.url))
        records = response.json()["items"]

        for record in records:
            yield record

        time.sleep(5.0)

    def validate_input_dates(self):
        # Validate input dates
        if datetime.strptime(self.start_date, "%Y-%m-%dT%H:%M:%SZ") > self.now:
            raise Exception(f"start_date {self.start_date} is greater than now.")

    def get_updated_state(
        self,
        current_stream_state: Mapping[str, Any],
        latest_record: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
    ) -> Mapping[str, any]:
        rid = str(latest_record["rid"])
        new_current_Stream_state = current_stream_state

        if current_stream_state is not None and rid in current_stream_state:
            current_parsed_date = datetime.strptime(str(current_stream_state[rid]), "%Y-%m-%d %H:%M:%S")
            latest_record_date = datetime.strptime(latest_record["updated_at_utc"], "%Y-%m-%dT%H:%M:%SZ")
            max_current_stream_last_record = max(current_parsed_date, latest_record_date).strftime("%Y-%m-%d %H:%M:%S")
            new_current_Stream_state[str(latest_record["rid"])] = max_current_stream_last_record
        elif current_stream_state is not None and rid not in current_stream_state.keys():
            new_current_Stream_state[rid] = self.start_date.strftime("%Y-%m-%d %H:%M:%S")
        else:
            new_current_Stream_state = {str(latest_record["rid"]): self.start_date.strftime("%Y-%m-%d %H:%M:%S")}

        return new_current_Stream_state


class Guests(OpentableSyncAPIStream):
    cursor_field = "updated_at_utc"
    primary_key = "id"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "guests"


class Reservations(OpentableSyncAPIStream):
    cursor_field = "updated_at_utc"
    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "reservations"


class OpentableSyncAPIAuthenticator(Oauth2Authenticator):
    """Request example for API token extraction:
    curl --user username:password -X POST \
       'https://oauth-pp.opentable.com/api/v2/oauth/token?grant_type=client_credentials'
    """

    def __init__(self, config):
        super().__init__(
            token_refresh_endpoint=f"{get_oauth_endpoint(config['is_sandbox'])}/api/v2/oauth/token?grant_type=client_credentials",
            client_id=config["username"],
            client_secret=config["password"],
            refresh_token="",
        )

    def get_refresh_request_body(self) -> Mapping[str, Any]:
        return {"grant_type": "client_credentialsZ"}

    def refresh_access_token(self) -> Tuple[str, int]:
        """
        returns a tuple of (access_token, expires_in)
        """
        try:
            auth = (self.client_id, self.client_secret)
            response = requests.request(method="POST", url=self.token_refresh_endpoint, auth=auth)

            response.raise_for_status()
            response_json = response.json()
            print(response_json["access_token"], response_json["expires_in"])
            return response_json["access_token"], response_json["expires_in"]
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e


# Source
class SourceOpentableSyncAPI(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        auth = OpentableSyncAPIAuthenticator(config)

        # Try to get API TOKEN
        token = auth.get_access_token()
        if not token:
            return False, "Unable to fetch Paypal API token due to incorrect client_id or secret"

        # Try to initiate a stream and validate input date params
        if isinstance(config["start_date"], int):
            start_date = datetime.strptime(config["start_date"], "%Y-%m-%dT%H:%M:%SZ")  # 2021-10-14 00:00:00
        else:
            start_date = config["start_date"]

        rid_list = config["rid_list"]
        is_sandbox = config["is_sandbox"]
        try:
            Reservations(authenticator=auth, start_date=start_date, rid_list=rid_list, is_sandbox=is_sandbox).validate_input_dates()
        except Exception as e:
            return False, e

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = OpentableSyncAPIAuthenticator(config)
        start_date = datetime.strptime(config["start_date"], "%Y-%m-%dT%H:%M:%SZ")  # 2021-10-14 00:00:00
        rid_list = config["rid_list"]
        is_sandbox = config["is_sandbox"]
        return [
            Guests(authenticator=auth, start_date=start_date, rid_list=rid_list, is_sandbox=is_sandbox),
            Reservations(authenticator=auth, start_date=start_date, rid_list=rid_list, is_sandbox=is_sandbox),
        ]
