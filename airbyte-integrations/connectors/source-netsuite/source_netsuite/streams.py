#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from datetime import date, datetime, timedelta
from typing import Any, Iterable, Mapping, MutableMapping, Optional, Union

import requests
from airbyte_cdk.sources.streams.http import HttpStream
from requests_oauthlib import OAuth1
from source_netsuite.constraints import (
    CUSTOM_INCREMENTAL_CURSOR,
    INCREMENTAL_CURSOR,
    META_PATH,
    NETSUITE_ERRORS_MAPPING,
    RECORD_PATH,
    REFERAL_SCHEMA,
    REFERAL_SCHEMA_URL,
    SCHEMA_HEADERS,
    USLESS_SCHEMA_ELEMENTS,
)


class NetsuiteStream(HttpStream, ABC):
    def __init__(
        self,
        auth: OAuth1,
        object_name: str,
        base_url: str,
        start_datetime: str,
        window_in_days: int,
    ):
        self.object_name = object_name
        self.base_url = base_url
        self.start_datetime = start_datetime
        self.window_in_days = window_in_days
        self.schemas = {}  # store subschemas to reduce API calls
        super().__init__(authenticator=auth)

    primary_key = "id"
    raise_on_http_errors = True
    output_datetime_format = "%Y-%m-%dT%H:%M:%SZ"
    input_datetime_format = "%m/%d/%Y"

    @property
    def name(self) -> str:
        return self.object_name

    @property
    def url_base(self) -> str:
        return self.base_url

    def path(self, **kwargs) -> str:
        return RECORD_PATH + self.object_name

    @property
    def ref_schema(self) -> Mapping[str, str]:
        schema = REFERAL_SCHEMA
        schema["properties"]["links"]["items"] = self.get_schema(REFERAL_SCHEMA_URL)
        return schema

    def get_schema(self, ref: str) -> Union[Mapping[str, Any], str]:
        # try to retrieve the schema from the cache
        schema = self.schemas.get(ref)
        if not schema:
            resp = self._session.get(url=self.url_base + ref, headers=SCHEMA_HEADERS)
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
        if isinstance(record, dict):
            # Netsuite schemas do not specify if fields can be null, or not
            # as Airbyte expects, so we have to allow every field to be null
            property_type = record.get("type")
            property_type_list = property_type if isinstance(property_type, list) else [property_type]
            # ensure there is a type, type is the json schema type and not a property
            # and null has not already been added
            if property_type and not isinstance(property_type, dict) and "null" not in property_type_list:
                record["type"] = ["null"] + property_type_list
            # removing non-functional elements from schema
            [record.pop(element) for element in USLESS_SCHEMA_ELEMENTS if record.get(element)]

            ref = record.get("$ref")
            if ref:
                return self.get_schema(ref) if ref == REFERAL_SCHEMA_URL else self.ref_schema
            else:
                return {k: self.build_schema(v) for k, v in record.items()}
        else:
            return record

    def get_json_schema(self, **kwargs) -> dict:
        schema = self.get_schema(META_PATH + self.name)
        return self.build_schema(schema)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        resp = response.json()
        has_more = resp.get("hasMore")
        if has_more:
            return {"offset": resp["offset"] + resp["count"]}
        return None

    def format_date(self, last_modified_date: str) -> str:
        # the date format returned is differnet than what we need to use in the query
        lmd_datetime = datetime.strptime(last_modified_date, self.output_datetime_format)
        return lmd_datetime.strftime(self.input_datetime_format)

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = {}
        if next_page_token:
            params.update(**next_page_token)
        return params

    def fetch_record(self, record: Mapping[str, Any], request_kwargs: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        url = record["links"][0]["href"]
        args = {"method": "GET", "url": url, "params": {"expandSubResources": True}}
        prep_req = self._session.prepare_request(requests.Request(**args))
        response = self._send_request(prep_req, request_kwargs)
        # sometimes response.status_code == 400,
        # but contains json elements with error description,
        # to avoid passing it as {TYPE: RECORD}, we filter response by status
        if response.status_code == requests.codes.ok:
            yield response.json()

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
        **kwargs,
    ) -> Iterable[Mapping]:

        records = response.json().get("items")
        request_kwargs = self.request_kwargs(stream_slice, next_page_token)
        if records:
            for record in records:
                # make sub-requests for each record fetched
                yield from self.fetch_record(record, request_kwargs)

    def should_retry(self, response: requests.Response) -> bool:
        if response.status_code in NETSUITE_ERRORS_MAPPING.keys():
            message = response.json().get("o:errorDetails")
            if isinstance(message, list):
                error_code = message[0].get("o:errorCode")
                detail_message = message[0].get("detail")
                known_error = NETSUITE_ERRORS_MAPPING.get(response.status_code)
                if error_code in known_error.keys():
                    setattr(self, "raise_on_http_errors", False)
                    self.logger.warn(
                        f"Stream `{self.name}`: {known_error.get(error_code)}, full error message: {detail_message}",
                    )
                    pass
                else:
                    return super().should_retry(response)
        return super().should_retry(response)


class IncrementalNetsuiteStream(NetsuiteStream):
    @property
    def cursor_field(self) -> str:
        return INCREMENTAL_CURSOR

    def filter_records_newer_than_state(
        self,
        stream_state: Mapping[str, Any] = None,
        records: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Parse the records with respect to `stream_state` for `incremental` sync."""
        if stream_state:
            for record in records:
                if record.get(self.cursor_field, "") >= stream_state.get(self.cursor_field):
                    yield record
        else:
            yield from records

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
        **kwargs,
    ) -> Iterable[Mapping]:
        records = super().parse_response(response, stream_state, stream_slice, next_page_token)
        yield from self.filter_records_newer_than_state(stream_state, records)

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        latest_cursor = latest_record.get(self.cursor_field, "")
        current_cursor = current_stream_state.get(self.cursor_field, "")
        return {self.cursor_field: max(latest_cursor, current_cursor)}

    def request_params(
        self, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = {**(next_page_token or {})}
        if stream_slice:
            params.update(
                **{"q": f'{self.cursor_field} AFTER "{stream_slice["start"]}" AND {self.cursor_field} BEFORE "{stream_slice["end"]}"'}
            )
        return params

    def stream_slices(
        self,
        stream_state: Mapping[str, Any] = None,
        **kwargs: Optional[Mapping[str, Any]],
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        # Netsuite cannot order records returned by the API, so we need stream slices
        # to maintain state properly https://docs.airbyte.com/connector-development/cdk-python/incremental-stream/#streamstream_slices
        slices = []
        start_str = stream_state.get(self.cursor_field) if stream_state else self.start_datetime
        start = datetime.strptime(start_str, self.output_datetime_format).date()
        # handle abnormal state values
        if start > date.today():
            return slices
        else:
            while start <= date.today():
                next_day = start + timedelta(days=self.window_in_days)
                slices.append(
                    {
                        "start": start.strftime(self.input_datetime_format),
                        "end": next_day.strftime(self.input_datetime_format),
                    }
                )
                start = next_day
        return slices


class CustomIncrementalNetsuiteStream(IncrementalNetsuiteStream):
    @property
    def cursor_field(self) -> str:
        return CUSTOM_INCREMENTAL_CURSOR
