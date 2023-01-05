#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from http import HTTPStatus
from itertools import chain
from typing import Any, List, Mapping, Union

import dpath.util
import requests
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import NoAuth
from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.types import Config, Record
from requests import HTTPError


@dataclass
class AuthenticatorFacebookPageAccessToken(NoAuth):
    config: Config
    page_id: Union[InterpolatedString, str]
    access_token: Union[InterpolatedString, str]

    def __post_init__(self, options: Mapping[str, Any]):
        self._page_id = InterpolatedString.create(self.page_id, options=options).eval(self.config)
        self._access_token = InterpolatedString.create(self.access_token, options=options).eval(self.config)

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        """Attach the page access token to params to authenticate on the HTTP request"""
        page_access_token = self.generate_page_access_token()
        request.prepare_url(url=request.url, params={"access_token": page_access_token})
        return request

    # @staticmethod
    def generate_page_access_token(self) -> str:
        # We are expecting to receive User access token from config. To access
        # Pages API we need to generate Page access token. Page access tokens
        # can be generated from another Page access token (with the same page ID)
        # so if user manually set Page access token instead of User access
        # token it would be no problem unless it has wrong page ID.
        # https://developers.facebook.com/docs/pages/access-tokens#get-a-page-access-token
        try:
            r = requests.get(
                f"https://graph.facebook.com/{self._page_id}", params={"fields": "access_token", "access_token": self._access_token}
            )
            if r.status_code != HTTPStatus.OK:
                raise HTTPError(r.text)
            return r.json().get("access_token")
        except Exception as e:
            raise Exception(f"Error while generating page access token: {e}") from e


@dataclass
class NestedDpathExtractor(DpathExtractor):
    """
    Record extractor that searches a decoded response over a path defined as an array of fields.

    Extends the DpathExtractor to allow for a list of records to be generated from a dpath that points
    to an array object as first point and iterates over list of records by the rest of path. See the example.

    Example data:
    ```
    {
        "data": [
            {'insights':
                {'data': [
                    {"id": "id1",
                    "name": "name1",
                    ...
                    },
                    {"id": "id1",
                    "name": "name1",
                    ...
                    },
                    ...
            },
            ...
        ]
    }
    ```
    """

    def extract_records(self, response: requests.Response) -> List[Record]:
        response_body = self.decoder.decode(response)
        if len(self.field_pointer) == 0:
            extracted = response_body
        else:
            pointer = [pointer.eval(self.config) for pointer in self.field_pointer]
            extracted_list = dpath.util.get(response_body, pointer[0], default=[])
            extracted = list(chain(*[dpath.util.get(x, pointer[1:], default=[]) for x in extracted_list])) if extracted_list else []
        if isinstance(extracted, list):
            return extracted
        elif extracted:
            return [extracted]
        else:
            return []
