#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import logging
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from requests.auth import AuthBase

BASE_URL = "https://coda.io/apis/v1/"

# Basic full refresh stream
class CodaStream(HttpStream, ABC):
   

    url_base = BASE_URL

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.limit = 25

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return response.json().get("nextPageToken", None)

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        if next_page_token:
            return {"pageToken": next_page_token, "limit": self.limit}
        else:
            return {"limit": self.limit}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json()['items']


class UserDetails(CodaStream):

    primary_key = "USER_DETAILS"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "whoami"


class Docs(CodaStream):

    primary_key = "DOCS"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "docs"


class Permissions(CodaStream):

    primary_key = "PERMISSIONS"

    def __init__(self, doc_id, **kwargs):
        super().__init__(**kwargs)
        self._doc_id = doc_id

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"docs/{self._doc_id}/acl/permissions"



class Categories(CodaStream):

    primary_key = "CATEGORIES"


    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "categories"




class Pages(CodaStream):

    primary_key = "PAGES"

    def __init__(self, doc_id, **kwargs):
        super().__init__(**kwargs)
        self._doc_id = doc_id

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"docs/{self._doc_id}/pages"

class Tables(CodaStream):

    primary_key = "TABLES"

    def __init__(self, doc_id, **kwargs):
        super().__init__(**kwargs)
        self._doc_id = doc_id

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"docs/{self._doc_id}/tables"



class Formulas(CodaStream):

    primary_key = "FORMULAS"

    def __init__(self, doc_id, **kwargs):
        super().__init__(**kwargs)
        self._doc_id = doc_id

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"docs/{self._doc_id}/formulas"

class Controls(CodaStream):

    primary_key = "CONTROLS"

    def __init__(self, doc_id, **kwargs):
        super().__init__(**kwargs)
        self._doc_id = doc_id

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"docs/{self._doc_id}/controls"

# Source
class SourceCoda(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            token = config.get("auth_token")
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{BASE_URL}whoami", headers=headers)
            return True, None
        except Exception as e:
            return False, e



    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        stream_args = {
            "authenticator": TokenAuthenticator(token=config.get("auth_token")),
        }

        additional_args = {
            **stream_args,
            'doc_id': config.get('doc_id')
        }

        return [
            UserDetails(**stream_args),
            Docs(**stream_args),
            Permissions(**additional_args),
            Categories(**stream_args),
            Pages(**additional_args),
            Tables(**additional_args),
            Formulas(**additional_args),
            Controls(**additional_args),
        ]
