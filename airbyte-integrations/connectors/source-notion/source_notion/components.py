# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass, field
from typing import Any, List, Mapping, MutableMapping, Optional

import pendulum

from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.auth.token import BearerAuthenticator
from airbyte_cdk.sources.declarative.extractors.record_filter import RecordFilter
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState


@dataclass
class NotionAuthenticator(DeclarativeAuthenticator):
    """
    Custom authenticator designed to handle all existing Notion authenticator configurations, being:
    token_auth: Private integration token
    legacy_token_auth: Legacy config for private tokens
    oauth: Public integration token (static oauth-derived token using advanced auth protocol)
    """
    config: Mapping[str, Any]
    token_auth: BearerAuthenticator
    legacy_token_auth: BearerAuthenticator
    oauth: BearerAuthenticator

    def __new__(cls, token_auth, legacy_token_auth, oauth, config, *args, **kwargs) -> BearerAuthenticator:
        credentials = config.get("credentials", {})

        if config.get("access_token", {}):
            return legacy_token_auth
        elif credentials["auth_type"] == "token":
            return token_auth
        elif credentials["auth_type"] == "OAuth2.0":
            return oauth


@dataclass
class NotionPropertiesTransformation(RecordTransformation):
    """
    # TODO: Flesh out docstring
    Custom transformation that normalizes nested 'properties' object by moving
    unique named entities into 'name', 'value' mappings
    """

    def transform(self, record: MutableMapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        properties = record.get("properties", {})
        transformed_properties = [
            {"name": name, "value": value} for name, value in properties.items()
        ]
        record["properties"] = transformed_properties
        return record


@dataclass
class NotionSemiIncrementalFilter(RecordFilter):
    """
    Custom filter to implement semi-incremental syncing for the Comments endpoints, which does not support sorting or filtering.
    This filter emulates incremental behavior by filtering out records based on the comparison of the cursor value with current value in state,
    ensuring only records updated after the cutoff timestamp are synced.
    """

    def filter_records(
        self,
        records: List[Mapping[str, Any]],
        stream_state: StreamState,
        stream_slice: Optional[StreamSlice] = None,
        **kwargs
    ) -> List[Mapping[str, Any]]:
      """
      Filters a list of records, returning only those with a cursor_value greater than the current value in state.
      """
      current_state = [state_value for state_value in stream_state.get(
            "states", []) if state_value["partition"]["id"] == stream_slice.partition["id"]]
      cursor_value = self.get_filter_date(
            self.config.get("start_date"), current_state)
      if cursor_value:
            return [record for record in records if record["last_edited_time"] > cursor_value]
      return records

    def get_filter_date(self, start_date: str, state_value: list) -> str:
        """
        Calculates the filter date to pass in the request parameters by comparing the start_date with the value of state obtained from the stream_slice.
        If only the start_date exists, use it by default.
        """

        start_date_parsed = pendulum.parse(
            start_date).to_iso8601_string() if start_date else None
        state_date_parsed = (
            pendulum.parse(state_value[0]["cursor"]["last_edited_time"]).to_iso8601_string(
            ) if state_value else None
        )

        if state_date_parsed:
            return max(filter(None, [start_date_parsed, state_date_parsed]), default=start_date_parsed)
        return start_date_parsed
