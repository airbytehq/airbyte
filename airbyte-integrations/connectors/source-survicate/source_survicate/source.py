from abc import ABC
from datetime import datetime, timedelta
import dateutil
import json
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


class SourceSurvicate(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        start_datetime = None
        if "start_datetime" in config:
            start_datetime = _parse_datetime(config["start_datetime"])
        auth = TokenAuthenticator(config["api_key"], auth_method='Basic')
        for r in Responses(config["survey_id"], start_datetime, authenticator=auth).read_records(SyncMode.incremental):
            continue
        return (True, None)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        # Parse the date from a string into a datetime object
        start_datetime = None
        if "start_datetime" in config:
            start_datetime = _parse_datetime(config["start_datetime"])
        auth = TokenAuthenticator(config["api_key"], auth_method='Basic')
        return [Responses(config["survey_id"], start_datetime, authenticator=auth)]


class SurveyStream(HttpStream, ABC):
    """The base class for all survey-based streams."""

    _survey_id = None

    @property
    def url_base(self) -> str:
        return f"https://data-api.survicate.com/v1/surveys/{self._survey_id}/"


class Responses(SurveyStream):
    """Survey responses stream."""

    primary_key = "response_uuid"
    # We are assuming the API results are sorted by this field,
    # but they may be sorted by the `first_seen_date` field....
    cursor_field = "first_response_date"  
    # Save the state every 100 records
    state_checkpoint_interval = 100

    def __init__(self, survey_id: str, start_datetime: datetime, **kwargs):
        super(SurveyStream, self).__init__(**kwargs)
        self._survey_id = survey_id
        self._start_datetime = start_datetime
        self._page_number = 1

    def path(self, **kwargs) -> str:
        return "visitors"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if response.json():
            # Survicate doesn't indicate what page we are on
            # So, we have to store our own page counter and increment it
            self._page_number += 1
            return {'page': self._page_number}

        return None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, next_page_token=next_page_token)
        since_dt = stream_state.get(self.cursor_field, None)
        if since_dt:
            params['since'] = since_dt
        if next_page_token:
            params.update(next_page_token)

        return params

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        current_stream_state = current_stream_state or {}
        if not len(current_stream_state) and not self._start_datetime:
            current_stream_state[self.cursor_field] = _parse_datetime(latest_record[self.cursor_field])
        else:
            if self.cursor_field in current_stream_state and isinstance(current_stream_state[self.cursor_field], str):
                # Handle initial state loaded from JSON which is in str format
                current_stream_state[self.cursor_field] = _parse_datetime(current_stream_state[self.cursor_field], increment=True)
            current_stream_state[self.cursor_field] = max(
                _parse_datetime(latest_record[self.cursor_field]), current_stream_state.get(self.cursor_field, self._start_datetime)
            )

        return current_stream_state

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        print(f'parsing {len(response.json())} responses')
        for r in response.json():
            response_clean = {k.strip(): v for k, v in r.items()}
            # Process different question/answer values
            for qa in response_clean['answers']:
                if 'content' not in qa:
                    # Question has no answer content
                    continue
                response_clean[qa['question'].strip()] = qa['content']
            del response_clean['answers']
            # Process custom attributes
            for k,v in response_clean['custom_attributes'].items():
                response_clean[k.strip()] = v
            del response_clean['custom_attributes']
            yield response_clean


    def get_json_schema(self) -> Dict:
        """Get the JSON schema by appending any fields in a sample record to our existing schema def."""
        schema = super().get_json_schema()

        # Manually send the request
        # If we call `read_records` it will end up incrementing our page counter
        # We don't want this to happen when we are just fetching records to infer the schema
        request_headers = self.request_headers({})
        request = self._create_prepared_request(
            path=self.path(),
            headers=dict(request_headers, **self.authenticator.get_auth_header()),
            params=self.request_params({}),
        )
        response = self._send_request(request, {})
        record = next(self.parse_response(response, {}))

        # Add inferred properties
        for k in record.keys():
            kk = k.strip()
            if kk not in schema:
                schema['properties'][kk] = {"type": "date" if kk.endswith("date") else "string"}
        return schema


def _parse_datetime(dt_str: str,
                    increment: Optional[bool] = False):
    parsed_time = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S%z")
    if increment:
        # Increment the datetime cursor to prevent re-fetching the last fetched record.
        # This is required because the `since` parameter in the Survicate API is inclusive and we 
        # determine the cursor based on the last record we retrieved.
        return incremented_time = parsed_time + timedelta(minutes=1)
    return parsed_time
