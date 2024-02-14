# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from typing import Any, List, Mapping, Optional

import pendulum
import requests
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.auth.token import BasicHttpAuthenticator, BearerAuthenticator
from airbyte_cdk.sources.declarative.extractors.record_filter import RecordFilter
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
    RequestInput,
)
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState


@dataclass
class MailChimpRequester(HttpRequester):

    request_body_json: Optional[RequestInput] = None
    request_headers: Optional[RequestInput] = None
    request_parameters: Optional[RequestInput] = None
    request_body_data: Optional[RequestInput] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:

        self.request_options_provider = InterpolatedRequestOptionsProvider(
            request_body_data=self.request_body_data,
            request_body_json=self.request_body_json,
            request_headers=self.request_headers,
            request_parameters=self.request_parameters,
            config=self.config,
            parameters=parameters or {},
        )
        super().__post_init__(parameters)

    def get_url_base(self) -> str:
        self.get_data_center_location()
        return super().get_url_base()

    def get_data_center_location(self):
        if not self.config.get("data_center"):
            if isinstance(self.authenticator, BasicHttpAuthenticator):
                data_center = self.config["credentials"]["apikey"].split("-").pop()
            else:
                data_center = self.get_oauth_data_center(self.config["credentials"]["access_token"])
            self.config["data_center"] = data_center

    @staticmethod
    def get_oauth_data_center(access_token: str) -> str:
        """
        Every Mailchimp API request must be sent to a specific data center.
        The data center is already embedded in API keys, but not OAuth access tokens.
        This method retrieves the data center for OAuth credentials.
        """
        try:
            response = requests.get(
                "https://login.mailchimp.com/oauth2/metadata", headers={"Authorization": "OAuth {}".format(access_token)}
            )

            # Requests to this endpoint will return a 200 status code even if the access token is invalid.
            error = response.json().get("error")
            if error == "invalid_token":
                raise ValueError("The access token you provided was invalid. Please check your credentials and try again.")
            return response.json()["dc"]

        # Handle any other exceptions that may occur.
        except Exception as e:
            raise Exception(f"An error occured while retrieving the data center for your account. \n {repr(e)}")


class MailChimpAuthenticator(DeclarativeAuthenticator):
    config: Mapping[str, Any]
    bearer: BearerAuthenticator
    basic: BasicHttpAuthenticator

    def __new__(cls, bearer, basic, config, *args, **kwargs):
        if config.get("credentials", {}).get("auth_type") == "oauth2.0":
            return bearer
        else:
            return basic


class MailChimpRecordFilter(RecordFilter):
    """
    Filter applied on a list of Records.
    """

    def filter_records(
        self,
        records: List[Mapping[str, Any]],
        stream_state: StreamState,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> List[Mapping[str, Any]]:
        current_state = [x for x in stream_state.get("states", []) if x["partition"]["id"] == stream_slice.partition["id"]]
        # TODO: REF what to do if no start_date mentioned (see manifest)
        #  implement the same logic
        start_date = self.config.get("start_date", (pendulum.now() - pendulum.duration(days=700)).to_iso8601_string())
        if current_state and start_date:
            filter_value = max(start_date, current_state[0]["cursor"][self.parameters["cursor_field"]])
            return [record for record in records if record[self.parameters["cursor_field"]] > filter_value]
        return records


class MailChimpRecordFilterEmailActivity(RecordFilter):
    def filter_records(
        self,
        records: List[Mapping[str, Any]],
        stream_state: StreamState,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> List[Mapping[str, Any]]:

        return [{**record, **activity_item} for record in records for activity_item in record.pop("activity", [])]
