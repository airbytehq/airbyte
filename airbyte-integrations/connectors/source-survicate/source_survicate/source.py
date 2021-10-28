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


class SurvicateStream(HttpStream, ABC):
    """The base class for all Survicate streams."""

    primary_key = "response_uuid"
    # We are assuming the API results are sorted by this field,
    # but they may be sorted by the `first_seen_date` field....
    cursor_field = "first_response_date"  
    # Save the state every 100 records
    state_checkpoint_interval = 100

    def __init__(self, survey_id: str, start_datetime: datetime, **kwargs):
        super(SurvicateStream, self).__init__(**kwargs)
        self._survey_id = survey_id
        self._start_datetime = start_datetime
        self._page_number = 1

    @property
    def url_base(self) -> str:
        return f"https://data-api.survicate.com/v1/surveys/{self._survey_id}/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_data = response.json()
        if response_data:
            # Survicate doesn't indicate what page we are on
            # So, we have to store our own page counter and increment it
            self._page_number += 1
            return {'page': self._page_number}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:

        params = {}
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
                # TODO: Is there a clearner way to handle this?
                current_stream_state[self.cursor_field] = _parse_datetime(current_stream_state[self.cursor_field])
            current_stream_state[self.cursor_field] = max(
                _parse_datetime(latest_record[self.cursor_field]), current_stream_state.get(self.cursor_field, self._start_datetime)
            )

        return current_stream_state

    """
    NOTE
    ----
    Inferring the schema seems somewhat unreliable.
    Besides the initial setup of the connector, schema update needs to be triggered manually.
    It also only checks a subset of records for the new schema; in this case just the first available record.
    ----
    def get_json_schema(self) -> Dict:
        schema = super().get_json_schema()
        r = next(self.read_records(SyncMode.full_refresh))
        for k in r.keys():
            kk = k.strip()
            if kk not in schema:
                schema[kk] = {"type": "date" if kk.endswith("date") else "string"}
        return schema
    """

class Responses(SurvicateStream):
    """Survey responses stream."""

    def path(self, **kwargs) -> str:
        return "visitors"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        survey_responses_parsed = []
        survey_responses_raw = response.json()
        for sr_raw in survey_responses_raw:
            ### TODO - Is there custom processing of fields required?
            sr_parsed = {k.strip(): v for k, v in sr_raw.items()}
            ### TODO -- How do we handle all different question types
            for qa in sr_raw['answers']:
                if 'content' not in qa:
                    # Question has no answer content
                    continue
                sr_parsed[qa['question'].strip()] = qa['content']
            del sr_parsed['answers']
            del sr_parsed['custom_attributes']  ### TODO - what to do with this?
            survey_responses_parsed.append(sr_parsed)
        return survey_responses_parsed


def _parse_datetime(dt_str: str):
    return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S%z")