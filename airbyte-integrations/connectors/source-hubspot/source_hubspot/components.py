#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
from datetime import timedelta
from typing import Any, Dict, Mapping, MutableMapping, Optional

import pendulum

from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.requesters import HttpRequester
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.types import Config, Record, StreamSlice, StreamState


class NewtoLegacyFieldTransformation(RecordTransformation):
    """
    Implements a custom transformation which adds the legacy field equivalent of v2 fields for streams which contain Deals and Contacts entities.

    This custom implmentation was developed in lieu of the AddFields component due to the dynamic-nature of the record properties for the HubSpot source. Each

    For example:
    hs_v2_date_exited_{stage_id} -> hs_date_exited_{stage_id} where {stage_id} is a user-generated value
    """

    def __init__(self, field_mapping: Dict[str, str]) -> None:
        self._field_mapping = field_mapping

    def transform(
        self,
        record_or_schema: Dict[str, Any],
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        """
        Transform a record in place by adding fields directly to the record by manipulating the injected fields into a legacy field to avoid breaking syncs.

        :param record_or_schema: The input record or schema to be transformed.
        """
        is_record = record_or_schema.get("properties") is not None

        for field, value in list(record_or_schema.get("properties", record_or_schema).items()):
            for legacy_field, new_field in self._field_mapping.items():
                if new_field in field:
                    transformed_field = field.replace(new_field, legacy_field)

                    if legacy_field == "hs_lifecyclestage_" and not transformed_field.endswith("_date"):
                        transformed_field += "_date"

                    if is_record:
                        if record_or_schema["properties"].get(transformed_field) is None:
                            record_or_schema["properties"][transformed_field] = value
                    else:
                        if record_or_schema.get(transformed_field) is None:
                            record_or_schema[transformed_field] = value


class MigrateEmptyStringState(StateMigration):
    cursor_field: str
    config: Config

    def __init__(self, cursor_field, config: Config):
        self.cursor_field = cursor_field
        self.config = config

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        # if start date wasn't provided in the config default date will be used
        start_date = self.config.get("start_date", "2006-06-01T00:00:00.000Z")
        return {self.cursor_field: start_date}

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return stream_state.get(self.cursor_field) == ""


class EngagementsHttpRequester(HttpRequester):

    recent_api_total_records_limit = 10000
    recent_api_last_days_limit = 29

    recent_api_path = "/engagements/v1/engagements/recent/modified"
    all_api_path = "/engagements/v1/engagements/paged"

    _use_recent_api = None

    def should_use_recent_api(self, stream_slice: StreamSlice) -> bool:
        if self._use_recent_api is not None:
            return self._use_recent_api

        # Recent engagements API returns records updated in the last 30 days only. If start time is older All engagements API should be used
        if int(stream_slice["start_time"]) >= int((pendulum.now() - timedelta(days=self.recent_api_last_days_limit)).timestamp() * 1000):
            # Recent engagements API returns only 10k most recently updated records.
            # API response indicates that there are more records so All engagements API should be used
            _, response = self._http_client.send_request(
                http_method=self.get_method().value,
                url=self._join_url(self.get_url_base(), self.recent_api_path),
                headers=self._request_headers({}, stream_slice, {}, {}),
                params={"count": 250, "since": stream_slice["start_time"]},
                request_kwargs={"stream": self.stream_response},
            )
            if response.json().get("total") <= self.recent_api_total_records_limit:
                self._use_recent_api = True
        else:
            self._use_recent_api = False

        return self._use_recent_api

    def get_path(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        if self.should_use_recent_api(stream_slice):
            return self.recent_api_path
        return self.all_api_path

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        request_params = self._request_options_provider.get_request_params(
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
        )
        if self.should_use_recent_api(stream_slice):
            request_params.update({"since": stream_slice["start_time"]})
        return request_params
