#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from collections import Counter
from datetime import date, datetime, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from requests_oauthlib import OAuth1

rest_path = "/services/rest/"
record_path = rest_path + "record/v1/"
metadata_path = record_path + "metadata-catalog/"
schema_headers = {"Accept": "application/schema+json"}


# Basic full refresh stream
class NetsuiteStream(HttpStream, ABC):
    def __init__(self, auth: OAuth1, obj_name: str, base_url: str, start_datetime: str):
        self.obj_name = obj_name
        self.base_url = base_url
        self.start_datetime = start_datetime
        self.schemas = {}  # stores subschemas to reduce API calls
        super().__init__(authenticator=auth)

    primary_key = "id"

    @property
    def name(self) -> str:
        return self.obj_name

    @property
    def url_base(self) -> str:
        return self.base_url

    def path(self, **kwargs) -> str:
        return record_path + self.obj_name

    def ref_schema(self) -> Mapping[str, str]:
        return {
            "type": "object",
            "properties": {
                "id": {"title": "Internal identifier", "type": "string"},
                "refName": {"title": "Reference Name", "type": ["string", "null"]},
                "externalId": {"title": "External identifier", "type": ["string", "null"]},
                "links": {
                    "title": "Links",
                    "type": "array",
                    "readOnly": True,
                    "items": self.get_schema("/services/rest/record/v1/metadata-catalog/nsLink"),
                },
            },
        }

    def get_schema(self, ref: str) -> Union[Mapping[str, Any], str]:
        # try to retrieve the schema from the cache
        schema = self.schemas.get(ref)
        if not schema:
            url = self.url_base + ref
            resp = requests.get(url, headers=schema_headers, auth=self._session.auth)
            # some schemas, like transaction, do not exist because they refer to multiple
            # record types, e.g. sales order/invoice ... in this case we can't retrieve
            # the correct schema, so we just put the json in a string
            if resp.status_code == 404:
                schema = {"title": ref, "type": "string"}
            else:
                resp.raise_for_status
                schema = resp.json()
            self.schemas[ref] = schema
        return schema

    def build_schema(self, record: Any) -> Mapping[str, Any]:
        # recursively build a schema with subschemas
        if type(record) == dict:
            # Netsuite schemas do not specify if fields can be null, or not
            # as Airbyte expects, so we have to allow every field to be null
            property_type = record.get("type")
            property_type_list = property_type if type(property_type) == list else [property_type]
            # ensure there is a type, type is the json schema type and not a property
            # and null has not already been added
            if property_type and type(property_type) != dict and "null" not in property_type_list:
                record["type"] = property_type_list + ["null"]

            # Netsuite values can be the full name of the value and not match
            # the enum specified in the scheama
            if record.get("enum"):
                del record["enum"]

            # these parts of the schema is not used by Airybte
            if record.get("x-ns-filterable"):
                del record["x-ns-filterable"]
            if record.get("x-ns-custom-field"):
                del record["x-ns-custom-field"]
            if record.get("nullable"):
                del record["nullable"]

            ref = record.get("$ref")
            if ref:
                ns_link = ref == "/services/rest/record/v1/metadata-catalog/nsLink"
                return self.get_schema(ref) if ns_link else self.ref_schema()
            else:
                return {k: self.build_schema(v) for k, v in record.items()}
        else:
            return record

    def get_json_schema(self, **kwargs) -> dict:
        schema = self.get_schema(metadata_path + self.name)
        return self.build_schema(schema)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        resp = response.json()
        offset = resp["offset"]
        count = resp["count"]
        return {"offset": offset + count} if resp["hasMore"] else None

    output_datetime_format = "%Y-%m-%dT%H:%M:%SZ"
    input_datetime_format = "%Y-%m-%d %I:%M:%S %p"

    def format_date(self, last_modified_date: str) -> str:
        # the date format returned is differnet than what we need to use in the query
        lmd_datetime = datetime.strptime(last_modified_date, self.output_datetime_format)
        return lmd_datetime.strftime(self.input_datetime_format)

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return next_page_token

    def fetch_record(self, record: Mapping[str, Any], request_kwargs: Mapping[str, Any]) -> Mapping[str, Any]:
        url = record["links"][0]["href"]
        args = {"method": "GET", "url": url, "params": {"expandSubResources": True}}
        prep_req = self._session.prepare_request(requests.Request(**args))
        resp = self._send_request(prep_req, request_kwargs)
        return resp.json()

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        records = response.json().get("items")
        request_kwargs = self.request_kwargs(stream_state, stream_slice, next_page_token)
        for record in records:
            yield self.fetch_record(record, request_kwargs)


# Basic incremental stream
class IncrementalNetsuiteStream(NetsuiteStream, ABC):
    @property
    def cursor_field(self) -> str:
        return "lastModifiedDate"

    def stream_slices(
        self, sync_mode: SyncMode, stream_state: Mapping[str, Any] = None, **kwargs: Optional[Mapping[str, Any]]
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        if sync_mode == SyncMode.incremental:
            # Netsuite cannot order records returned by the API, so we need stream slices
            # to maintain state properly https://docs.airbyte.com/connector-development/cdk-python/incremental-stream/#streamstream_slices
            ranges = []
            start_str = (
                (stream_state.get(self.cursor_field) or self.start_datetime) if sync_mode == SyncMode.incremental else self.start_datetime
            )
            first = datetime.strptime(start_str, self.output_datetime_format)
            start = first.date() + timedelta(days=1)
            # we want the first slice to be after the datetime of the last cursor
            ranges.append([self.format_date(start_str), start.isoformat()])
            while start <= date.today():
                next_day = start + timedelta(days=1)
                ranges.append([start.isoformat(), next_day.isoformat()])
                start = next_day
            return [{"q": f'{self.cursor_field} AFTER "{r[0]}" AND {self.cursor_field} BEFORE {r[1]}'} for r in ranges]
        else:
            return []

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        latest_cursor = latest_record.get(self.cursor_field) or ""
        current_cursor = current_stream_state.get(self.cursor_field) or ""
        return {self.cursor_field: max(latest_cursor, current_cursor)}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {**(stream_slice or {}), **(next_page_token or {})}


class CustomIncrementalNetsuiteStream(IncrementalNetsuiteStream):
    # Custom records use lastmodified instead of lastModifiedDate
    @property
    def cursor_field(self) -> str:
        return "lastmodified"


# Source
class SourceNetsuite(AbstractSource):
    def auth(self, config: Mapping[str, Any]) -> OAuth1:
        return OAuth1(
            client_key=config["consumer_key"],
            client_secret=config["consumer_secret"],
            resource_owner_key=config["token_id"],
            resource_owner_secret=config["token_secret"],
            realm=config["realm"],
            signature_method="HMAC-SHA256",
        )

    def base_url(self, config: Mapping[str, Any]) -> str:
        realm = config["realm"]
        subdomain = realm.lower().replace("_", "-")
        return f"https://{subdomain}.suitetalk.api.netsuite.com"

    def get_session(self, auth: OAuth1) -> requests.Session:
        session = requests.Session()
        session.auth = auth
        # automatically raise an error on failed requests
        session.hooks = {"response": lambda r, *args, **kwargs: r.raise_for_status()}
        return session

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        auth = self.auth(config)
        record_types = config.get("record_types")
        base_url = self.base_url(config)
        session = self.get_session(auth)
        # if record types are specified make sure they are valid
        if record_types:
            # ensure there are no duplicate record types as this will break Airbyte
            duplicates = [k for k, v in Counter(record_types).items() if v > 1]
            if duplicates:
                return False, f'Duplicate record type: {", ".join(duplicates)}'
            params = {"limit": 1}
            url = base_url + record_path
            [session.get(url + r, params=params) for r in record_types]
        else:
            # we could request the entire metadata catalog here, but this request returns much faster
            url = base_url + rest_path + "*"
            session.options(url)
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        base_url = self.base_url(config)
        auth = self.auth(config)
        start_datetime = config["start_datetime"]

        session = self.get_session(auth)

        metadata_url = base_url + metadata_path
        record_names = config.get("record_types")
        if not record_names:
            # retrieve all record types
            metadata = session.get(metadata_url).json().get("items")
            record_names = [r["name"] for r in metadata]

        # streams must have a lastModifiedDate property to be incremental
        schemas = {n: session.get(metadata_url + n, headers=schema_headers).json() for n in record_names}

        incremental_record_names = [n for n in record_names if schemas[n]["properties"].get("lastModifiedDate")]
        custom_incremental_record_names = [n for n in record_names if schemas[n]["properties"].get("lastmodified")]
        standard_record_names = [n for n in record_names if n not in incremental_record_names]

        streams = [NetsuiteStream(auth, name, base_url, start_datetime) for name in standard_record_names]
        incremental_streams = [
            IncrementalNetsuiteStream(auth, name, base_url, start_datetime) for name in incremental_record_names
        ]
        custom_incremental_streams = [
            CustomIncrementalNetsuiteStream(auth, name, base_url, start_datetime)
            for name in custom_incremental_record_names
        ]

        return streams + incremental_streams + custom_incremental_streams
