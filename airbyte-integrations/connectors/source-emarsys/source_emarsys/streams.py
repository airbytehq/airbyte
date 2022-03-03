#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import base64
import hashlib
import os
import re
from abc import ABC
from binascii import hexlify
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import parse_qs, urljoin, urlparse

import requests
from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream
from requests import models
from requests.auth import AuthBase


class EmarsysAuthenticator(AuthBase):
    def __init__(self, username, password) -> None:
        self.username = username
        self._password = password

    def _get_wsse(self):
        """Create X-WSSE header value from username & password.

        Returns:
            str: Header value.
        """
        nonce = hexlify(os.urandom(16)).decode("utf-8")
        created = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")
        sha1 = hashlib.sha1(str.encode(nonce + created + self._password)).hexdigest()
        password_digest = bytes.decode(base64.b64encode(str.encode(sha1)))

        return ('UsernameToken Username="{}", ' + 'PasswordDigest="{}", Nonce="{}", Created="{}"').format(
            self.username, password_digest, nonce, created
        )

    def __call__(self, r: models.PreparedRequest) -> models.PreparedRequest:
        r.headers["X-WSSE"] = self._get_wsse()
        return r


class EmarsysStream(HttpStream, ABC):
    @property
    def url_base(self) -> str:
        return "https://api.emarsys.net/api/v2/"

    def request_headers(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        """
        Default headers.
        """
        return {"Accept": "application/json", "Content-Type": "application/json"}

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        headers = response.headers
        try:
            reset_ts = datetime.utcfromtimestamp((int(headers.get("X-Ratelimit-Reset"))))
            current_ts = datetime.utcnow()
            if reset_ts >= current_ts:
                # Pause at least 1 second
                pause_secs = max((reset_ts - current_ts).total_seconds(), 1)
                self.logger.info("Delay API call for %s seconds", pause_secs)
                return pause_secs
        except ValueError:
            self.logger.warning("Could not parse X-Ratelimit-Reset timestamp. Fallback to exponential backoff.")
            return None

        return 1

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Parse data from response
        :return an iterable containing each record in the response
        """
        data = response.json().get("data", [])
        yield from data

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None


class PaginatedEmarsysStream(EmarsysStream):
    def __init__(self, authenticator=None, limit=10000):
        super().__init__(authenticator)
        self.limit = limit

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Return next offset if returned response contains data.

        :param response: the most recent response from the API
        :return Return None if there is no data in the response; elsewise, return last offset + # data records
        """
        data = response.json().get("data", [])

        if not data:
            return None

        queries = parse_qs(urlparse(response.request.url).query)
        offset = int(queries.get("offset", [0])[0]) + len(data)

        self.logger.info("Next offset: %s", offset)
        return {"offset": offset}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        """
        Override this method to define the query parameters that should be set on an outgoing HTTP request given the inputs.

        E.g: you might want to define query parameters for paging if next_page_token is not None.
        """
        params = {"offset": 0}

        if next_page_token:
            params["offset"] = next_page_token.get("offset", 0)

        if self.limit > 0:
            params["limit"] = self.limit

        return params


class Fields(EmarsysStream):
    primary_key = "id"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "field"


class ContactLists(EmarsysStream):
    primary_key = "id"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "contactlist"

    def use_cache(self):
        return True


class Segments(EmarsysStream):
    primary_key = "id"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "filter"


class SubPaginatedEmarsysStream(PaginatedEmarsysStream):
    def __init__(self, parent: HttpStream, **kwargs):
        """
        :param parent: should be the instance of HttpStream class
        """
        super().__init__(**kwargs)
        self.parent = parent

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )

        # iterate over all parent stream_slices
        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh,
                cursor_field=cursor_field,
                stream_slice=stream_slice,
                stream_state=stream_state,
            )

            # iterate over all parent records with current stream_slice
            for index, record in enumerate(parent_records):
                self.logger.info("Start slice #%s: %s", index + 1, record)
                yield {"parent": record}
                self.logger.info("Finished slice #%s: %s", index + 1, record)


class ContactListMemberships(SubPaginatedEmarsysStream):
    primary_key = ["contact_list_id", "id"]

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return f"contactlist/{stream_slice['parent']['id']}"

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        contact_list_id = stream_slice["parent"]["id"]
        data = response.json()["data"]
        for contact_id in data:
            yield {"id": contact_id, "contact_list_id": contact_list_id}


class Contacts(SubPaginatedEmarsysStream):
    primary_key = "id"

    def __init__(self, parent: HttpStream, fields: List, recur_list_patterns=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.field_string_ids = fields
        self._field_dict = None
        self._field_string_2_id = None
        self.yielded_contact_ids = set()
        self.recur_list_patterns = recur_list_patterns or []

    @property
    def field_dict(self):
        if not self._field_dict:
            self._field_dict, self._field_string_2_id = self._build_field_mapping()
        return self._field_dict

    @property
    def field_string_2_id(self):
        if not self._field_string_2_id:
            self._field_dict, self._field_string_2_id = self._build_field_mapping()
        return self._field_string_2_id

    def _filter_recur_lists(self, records: List[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
        """Filter any recurring contact list record that matchs pattern and is not the latest.

        Args:
            records (List[Mapping[str, Any]]): List of records

        Returns:
            List[Mapping[str, Any]]: List of records after filtering
        """
        no_recurs = []
        recurs = {}
        for record in records:
            matched = False

            for pattern in self.recur_list_patterns:
                # Use only the latest list if name matchs pattern
                if re.match(pattern, record["name"]):
                    matched = True
                    match_list = recurs.setdefault(pattern, [])
                    match_list.append(record)

            if not matched:
                no_recurs.append(record)

        for pattern, match_list in recurs.items():
            match_list.sort(key=lambda x: x["created"], reverse=True)
            self.logger.info("For pattern %s, use the latest list %s", pattern, match_list[0])

            ignores = match_list[1:]
            if ignores:
                self.logger.info(
                    "And ignore %s lists from %s to %s", len(ignores), ignores[-1]["name"], ignores[0]["name"]
                )

        # Unique latest recurring contact lists
        unique_recurs = {match_list[0]["id"]: match_list[0] for match_list in recurs.values() if len(match_list) > 0}

        return no_recurs + list(unique_recurs.values())

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )

        for stream_slice in parent_stream_slices:
            parent_records = list(
                self.parent.read_records(
                    sync_mode=SyncMode.full_refresh,
                    cursor_field=cursor_field,
                    stream_slice=stream_slice,
                    stream_state=stream_state,
                )
            )

            parent_records = self._filter_recur_lists(parent_records)

            for index, record in enumerate(parent_records):
                self.logger.info("Start slice #%s: %s", index + 1, record)
                yield {"parent": record}
                self.logger.info("Finished slice #%s: %s", index + 1, record)

    def _build_field_mapping(self) -> Tuple[Mapping[str, Any], Mapping[str, Any]]:
        """Build field dictionary and mapping from field string_id to id.

        Returns:
            Tuple[Mapping[str, Any], Mapping[str, Any]]: Tuple of field dict & mapping
        """
        url = urljoin(self.url_base, "field")
        response = self._session.get(url, headers={"Accept": "application/json", "Content-Type": "application/json"})
        data = response.json()["data"]
        field_dict = {}
        field_string_2_id = {}
        for field in data:
            field_dict[str(field["id"])] = field
            field_string_2_id[field["string_id"]] = str(field["id"])
        return field_dict, field_string_2_id

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return f"contactlist/{stream_slice['parent']['id']}/contacts/data"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        # Map field string_id to id
        params["fields"] = ",".join(str(self.field_string_2_id[string_id]) for string_id in self.field_string_ids)
        return params

    def get_airbyte_format(self, field_string_id: str) -> Mapping[str, any]:
        """Get Airbyte field specification from Emarsys field string_id.

        Args:
            field_string_id (str): Emarsys field string_id

        Returns:
            Mapping[str, any]: Airbyte field specification
        """
        field_id = self.field_string_2_id[field_string_id]

        airbyte_format = {"type": ["null", "string"]}
        if self.field_dict[field_id]["application_type"] == "numeric":
            airbyte_format = {"type": ["null", "number"]}

        if self.field_dict[field_id]["application_type"] == "date":
            airbyte_format = {"type": ["null", "string"], "format": "date"}

        return airbyte_format

    def get_json_schema(self) -> Mapping[str, Any]:
        schema = super().get_json_schema()
        for string_id in self.field_string_ids:
            schema["properties"][string_id] = self.get_airbyte_format(string_id)
        return schema

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        data = response.json()["data"]

        if data and isinstance(data, dict):
            for contact_id, contact_data in data.items():
                # One contact can be in multiple contact lists. Try to yield only once
                # for each contact data record.
                if contact_id in self.yielded_contact_ids:
                    continue
                self.yielded_contact_ids.add(contact_id)

                output_record = {"id": contact_id}

                for field_id, value in contact_data["fields"].items():
                    # Mapping field Id to field string_id
                    if field_id == "uid":
                        output_record["uid"] = value
                    elif field_id.isdigit():
                        field_string_id = self.field_dict[field_id]["string_id"]
                        output_record[field_string_id] = value

                yield output_record

        yield from []
