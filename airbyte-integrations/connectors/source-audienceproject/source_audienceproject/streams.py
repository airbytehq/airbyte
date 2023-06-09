#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional, Tuple, Union

import pendulum
import requests
from airbyte_cdk.sources.streams.http import HttpStream

DEFAULT_END_DATE = pendulum.yesterday().date()


class AudienceprojectStream(HttpStream, ABC):
    url_base = "https://campaign-api.audiencereport.com/"
    oauth_url_base = "https://oauth.audiencereport.com/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(
        self, response: requests.Response, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping]:
        data = response.json().get("data")
        if data:
            data["campaign_id"] = stream_slice["campaign_id"]
            yield data

    @staticmethod
    def _get_time_interval(
        starting_date: Union[pendulum.datetime, str], ending_date: Union[pendulum.datetime, str]
    ) -> Iterable[Tuple[pendulum.datetime, pendulum.datetime]]:
        if isinstance(starting_date, str):
            start_date = pendulum.parse(starting_date).date()
        if isinstance(ending_date, str):
            end_date = pendulum.parse(ending_date).date()
        else:
            end_date = DEFAULT_END_DATE
        if end_date < start_date:
            raise ValueError(
                f"""Provided start date has to be before end_date.
                 Start date: {start_date} -> end date: {end_date}"""
            )
        return start_date, end_date


# Basic incremental stream


class IncrementalAudienceprojectStream(AudienceprojectStream, ABC):
    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        return []

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {}
