#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import base64
import requests
import re
import decimal
import pendulum
import dpath.util
from requests import HTTPError
from typing import Any, List, Mapping, Dict, Union
from dataclasses import InitVar, dataclass
from typing import Any, Mapping, MutableMapping, Optional
from http import HTTPStatus
from datetime import date, datetime, time, timedelta, timezone
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState
from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import NoAuth
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.types import Config

@dataclass
class CustomExtractor(RecordExtractor):
    field_path: List[Union[InterpolatedString, str]]
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    decoder: Decoder = JsonDecoder(parameters={})

    def __post_init__(self, parameters: Mapping[str, Any]):
        for path_index in range(len(self.field_path)):
            if isinstance(self.field_path[path_index], str):
                self.field_path[path_index] = InterpolatedString.create(self.field_path[path_index], parameters=parameters)

    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
        def parse_date(value):
            # Xero datetimes can be .NET JSON date strings which look like
            # "/Date(1419937200000+0000)/"
            # https://developer.xero.com/documentation/api/requests-and-responses
            pattern = r"Date\((\-?\d+)([-+])?(\d+)?\)"
            match = re.search(pattern, value)
            iso8601pattern = r"((\d{4})-([0-2]\d)-0?([0-3]\d)T([0-5]\d):([0-5]\d):([0-6]\d))"
            if not match:
                iso8601match = re.search(iso8601pattern, value)
                if iso8601match:
                    try:
                        return datetime.strptime(value)
                    except Exception:
                        return None
                else:
                    return None

            millis_timestamp, offset_sign, offset = match.groups()
            if offset:
                if offset_sign == "+":
                    offset_sign = 1
                else:
                    offset_sign = -1
                offset_hours = offset_sign * int(offset[:2])
                offset_minutes = offset_sign * int(offset[2:])
            else:
                offset_hours = 0
                offset_minutes = 0

            return datetime.fromtimestamp((int(millis_timestamp) / 1000), tz=timezone.utc) + timedelta(hours=offset_hours, minutes=offset_minutes)
        
        response_body = self.decoder.decode(response)
        if len(self.field_path) == 0:
            extracted = response_body
        else:
            path = [path.eval(self.config) for path in self.field_path]
            if "*" in path:
                extracted = dpath.util.values(response_body, path)
            else:
                extracted = dpath.util.get(response_body, path, default=[])

        def convert_dates(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, str):
                        parsed_value = parse_date(value)
                        if parsed_value:
                            if isinstance(parsed_value, date):
                                parsed_value = datetime.combine(parsed_value, time.min)
                            parsed_value = parsed_value.replace(tzinfo=timezone.utc)
                            obj[key] = datetime.isoformat(parsed_value, timespec="seconds")
                    elif isinstance(value, (dict, list)):
                        convert_dates(value)
            elif isinstance(obj, list):
                for i in range(len(obj)):
                    if isinstance(obj[i], (dict, list)):
                        convert_dates(obj[i])

        convert_dates(extracted)

        if isinstance(extracted, list):
            return extracted
        elif extracted:
            return [extracted]
        else:
            return []



@dataclass
class CustomAuthenticator(NoAuth):
    config: Config
    client_id: Union[InterpolatedString, str]
    client_secret: Union[InterpolatedString, str]
    refresh_token: Union[InterpolatedString, str]
    access_token: Union[InterpolatedString, str]
    scopes: Union[InterpolatedString, str]

    def __post_init__(self, parameters: Mapping[str, Any]):
        self._client_id = InterpolatedString.create(self.client_id, parameters=parameters).eval(self.config)
        self._client_secret = InterpolatedString.create(self.client_secret, parameters=parameters).eval(self.config)
        self._refresh_token = InterpolatedString.create(self.refresh_token, parameters=parameters).eval(self.config)
        self._access_token = InterpolatedString.create(self.access_token, parameters=parameters).eval(self.config)
        self._scopes = InterpolatedString.create(self.scopes, parameters=parameters).eval(self.config)

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        """Attach the page access token to params to authenticate on the HTTP request"""
        if self._access_token:
            checker = self.check_endpoint_connection()
        if self._access_token is None or checker != True:
            self._access_token, self._refresh_token = self.generate_access_token()
        headers = {
            self.auth_header: f"Bearer {self._access_token}", 
            "Accept": "application/json", 
        }
        request.headers.update(headers)
        # print(request.headers, request.body, request.url, checker)    # Logger statement for developing purposes
        return request

    @property
    def auth_header(self) -> str:
        return "Authorization"

    @property
    def token(self) -> str:
        return self._access_token

    ''' Check the connection using /connections endpoint to validate given access token, 
        if response code not 200, new access_token needs to be retrieved '''
    def check_endpoint_connection(self):
        cred = f"Bearer {self._access_token}"
        headers = {
            "Authorization": cred,
            "Host": "api.xero.com",
            "Accept": "application/json"
        }

        url = "https://api.xero.com/connections"
        rest = requests.get(url, headers=headers)
        if rest.status_code != HTTPStatus.OK:
            return False
        return True

    def _get_refresh_access_token_response(self):
        url = f"https://identity.xero.com/connect/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {
            "refresh_token": self._refresh_token,
            "grant_type": "refresh_token",
            "client_id": self._client_id
        }
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            return response
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e

    def generate_access_token(self) -> tuple[str, str]:
        try:
            encoded_credentials = base64.b64encode(f"{self._client_id}:{self._client_secret}".encode()).decode()
            cred = f"Basic {encoded_credentials}"
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": cred
            }

            data = {
                "grant_type": "client_credentials",
                "scope": self._scopes
            }

            url = "https://identity.xero.com/connect/token"
            rest = requests.post(url, headers=headers, data=data)
            if rest.status_code != HTTPStatus.OK:
                raise HTTPError(rest)
            return (rest.json().get("access_token"), rest.json().get("refresh_token"))
        except requests.exceptions.HTTPError as e:
            error_message = str(e)
            if e.response.status_code == 403:
                error_message = (
                    "For oauth2 authentication try to re-authenticate and allow all requested scopes, for token authentication please update "
                    "access token with all required scopes mentioned in prerequisites. Full error message: " + error_message
                )
            return False, error_message
        except Exception as e:
            return False, str(e)
