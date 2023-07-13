#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

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
        return response.json()["items"]


class Docs(CodaStream):

    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "docs"


class CodaStreamDoc(CodaStream):
    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        self.authenticator (which should be used as the
        authenticator for Users) is object of NoAuth()

        so self._session.auth is used instead
        """
        docs_stream = Docs(**{"authenticator": self._authenticator})
        for doc in docs_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"doc_id": doc["id"]}


class Permissions(CodaStreamDoc):

    primary_key = "id"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        doc_id = stream_slice["doc_id"]
        return f"docs/{doc_id}/acl/permissions"


class Categories(CodaStreamDoc):

    primary_key = "name"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "categories"


class Pages(CodaStreamDoc):

    primary_key = "id"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        doc_id = stream_slice["doc_id"]
        return f"docs/{doc_id}/pages"


class Tables(CodaStreamDoc):

    primary_key = "id"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        doc_id = stream_slice["doc_id"]
        return f"docs/{doc_id}/tables"


class Rows(CodaStreamDoc):

    primary_key = "id"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        doc_id = stream_slice["doc_id"]
        tableid_or_name = stream_slice["tableid"]

        return f"docs/{doc_id}/tables/${tableid_or_name}/rows"


class Formulas(CodaStreamDoc):

    primary_key = "id"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        doc_id = stream_slice["doc_id"]
        return f"docs/{doc_id}/formulas"


class Controls(CodaStreamDoc):

    primary_key = "id"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        doc_id = stream_slice["doc_id"]
        return f"docs/{doc_id}/controls"


# Source
class SourceCoda(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            token = config.get("auth_token")
            headers = {"Authorization": f"Bearer {token}"}
            r = requests.get(f"{BASE_URL}whoami", headers=headers)
            if r.status_code == 200:
                return True, None
            else:
                r.raise_for_status()
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        stream_args = {
            "authenticator": TokenAuthenticator(token=config.get("auth_token")),
        }

        return [
            Docs(**stream_args),
            Permissions(**stream_args),
            Categories(**stream_args),
            Pages(**stream_args),
            Tables(**stream_args),
            Formulas(**stream_args),
            Controls(**stream_args),
            Rows(**stream_args),
        ]
