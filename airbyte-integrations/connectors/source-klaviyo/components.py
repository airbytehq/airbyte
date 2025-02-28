#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
import logging
from abc import ABC
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping, Optional, Union

import dpath
import requests
from requests.exceptions import InvalidURL

from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.requesters.error_handlers import DefaultErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies import WaitTimeFromHeaderBackoffStrategy
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.message.repository import InMemoryMessageRepository
from airbyte_cdk.sources.streams.call_rate import APIBudget
from airbyte_cdk.sources.streams.http.error_handlers import BackoffStrategy, ErrorHandler, HttpStatusErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import DEFAULT_ERROR_MAPPING
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ErrorResolution, FailureType, ResponseAction
from airbyte_cdk.sources.streams.http.http_client import HttpClient
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState


ARCHIVED_EMAIL = {"archived": "true", "campaign_type": "email"}
NOT_ARCHIVED_EMAIL = {"archived": "false", "campaign_type": "email"}

ARCHIVED = {"archived": "true"}
NOT_ARCHIVED = {"archived": "false"}

DEFAULT_START_DATE = "2012-01-01T00:00:00Z"


class ArchivedToPerPartitionStateMigration(StateMigration, ABC):
    """
    Updates old format state to new per partitioned format.
    Partitions: [{archived: True}, {archived: False}]
    Default built in airbyte cdk migration will recognise only top-level field cursor value(updated_at),
    but for partition {archived: True} source should use cursor value from archived object.

    Example input state:
    {
        "updated_at": "2020-10-10T00:00:00+00:00",
        "archived": {
          "updated_at": "2021-10-10T00:00:00+00:00"
        }
    }

    Example output state:
    {
        "partition":{ "archived":"true" },
        "cursor":{ "updated_at":"2021-10-10T00:00:00+00:00" }
    }
    {
        "partition":{ "archived":"false" },
        "cursor":{ "updated_at":"2020-10-10T00:00:00+00:00" }
    }
    """

    declarative_stream: DeclarativeStream
    config: Config

    def __init__(self, declarative_stream: DeclarativeStream, config: Config):
        self._config = config
        self.declarative_stream = declarative_stream
        self._cursor = declarative_stream.incremental_sync
        self._parameters = declarative_stream.parameters
        self._cursor_field = InterpolatedString.create(self._cursor.cursor_field, parameters=self._parameters).eval(self._config)

    def get_archived_cursor_value(self, stream_state: Mapping[str, Any]):
        return stream_state.get("archived", {}).get(self._cursor.cursor_field, self._config.get("start_date", DEFAULT_START_DATE))

    def get_not_archived_cursor_value(self, stream_state: Mapping[str, Any]):
        return stream_state.get(self._cursor.cursor_field, self._config.get("start_date", DEFAULT_START_DATE))

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return bool("states" not in stream_state and stream_state)

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        if not self.should_migrate(stream_state):
            return stream_state
        is_archived_updated_at = self.get_archived_cursor_value(stream_state)
        is_not_archived_updated_at = self.get_not_archived_cursor_value(stream_state)

        migrated_stream_state = {
            "states": [
                {"partition": ARCHIVED, "cursor": {self._cursor.cursor_field: is_archived_updated_at}},
                {"partition": NOT_ARCHIVED, "cursor": {self._cursor.cursor_field: is_not_archived_updated_at}},
            ]
        }
        return migrated_stream_state


class CampaignsStateMigration(ArchivedToPerPartitionStateMigration):
    """
    Campaigns stream has 2 partition field: archived and campaign_type(email, sms).
    Previous API version didn't return sms in campaigns output so we need to migrate only email partition.

    Example input state:
    {
        "updated_at": "2020-10-10T00:00:00+00:00",
        "archived": {
          "updated_at": "2021-10-10T00:00:00+00:00"
        }
      }
    Example output state:
    {
        "partition":{ "archived":"true","campaign_type":"email" },
        "cursor":{ "updated_at":"2021-10-10T00:00:00+00:00" }
    }
    {
        "partition":{ "archived":"false","campaign_type":"email" },
        "cursor":{ "updated_at":"2020-10-10T00:00:00+00:00" }
    }
    """

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        if not self.should_migrate(stream_state):
            return stream_state
        is_archived_updated_at = self.get_archived_cursor_value(stream_state)
        is_not_archived_updated_at = self.get_not_archived_cursor_value(stream_state)

        migrated_stream_state = {
            "states": [
                {"partition": ARCHIVED_EMAIL, "cursor": {self._cursor.cursor_field: is_archived_updated_at}},
                {"partition": NOT_ARCHIVED_EMAIL, "cursor": {self._cursor.cursor_field: is_not_archived_updated_at}},
            ]
        }
        return migrated_stream_state


class CampaignsDetailedTransformation(RecordTransformation):
    """
    Campaigns detailed stream fetches detailed campaigns info:
    estimated_recipient_count: integer
    campaign_messages: list of objects.

    To get this data CampaignsDetailedTransformation makes extra API requests:
    https://a.klaviyo.com/api/campaign-recipient-estimations/{campaign_id}
    https://developers.klaviyo.com/en/v2024-10-15/reference/get_messages_for_campaign
    """

    config: Config

    api_revision = "2024-10-15"
    url_base = "https://a.klaviyo.com/api/"
    name = "campaigns_detailed"
    max_retries = 5
    max_time = 60 * 10

    def __init__(self, config: Config, **kwargs):
        self.logger = logging.getLogger("airbyte")
        self.config = config
        self._api_key = self.config["api_key"]
        self._http_client = HttpClient(
            name=self.name,
            logger=self.logger,
            error_handler=self.get_error_handler(),
            api_budget=APIBudget(policies=[]),
            backoff_strategy=self.get_backoff_strategy(),
            message_repository=InMemoryMessageRepository(),
        )

    def transform(
        self,
        record: Dict[str, Any],
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        self._set_recipient_count(record)
        self._set_campaign_message(record)

    def _set_recipient_count(self, record: Mapping[str, Any]) -> None:
        campaign_id = record["id"]
        _, recipient_count_response = self._http_client.send_request(
            url=f"{self.url_base}campaign-recipient-estimations/{campaign_id}",
            request_kwargs={},
            headers=self.request_headers(),
            http_method="GET",
        )
        record["estimated_recipient_count"] = (
            recipient_count_response.json().get("data", {}).get("attributes", {}).get("estimated_recipient_count", 0)
        )

    def _set_campaign_message(self, record: Mapping[str, Any]) -> None:
        messages_link = record.get("relationships", {}).get("campaign-messages", {}).get("links", {}).get("related")
        if messages_link:
            _, campaign_message_response = self._http_client.send_request(
                url=messages_link, request_kwargs={}, headers=self.request_headers(), http_method="GET"
            )
            record["campaign_messages"] = campaign_message_response.json().get("data")

    def get_backoff_strategy(self) -> BackoffStrategy:
        return WaitTimeFromHeaderBackoffStrategy(header="Retry-After", max_waiting_time_in_seconds=self.max_time, parameters={}, config={})

    def request_headers(self):
        return {
            "Accept": "application/json",
            "Revision": self.api_revision,
            "Authorization": f"Klaviyo-API-Key {self._api_key}",
        }

    def get_error_handler(self) -> ErrorHandler:
        error_mapping = DEFAULT_ERROR_MAPPING | {
            404: ErrorResolution(ResponseAction.IGNORE, FailureType.config_error, "Resource not found. Ignoring.")
        }

        return HttpStatusErrorHandler(logger=self.logger, error_mapping=error_mapping, max_retries=self.max_retries)


@dataclass
class KlaviyoIncludedFieldExtractor(DpathExtractor):
    def extract_records(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        # Evaluate and retrieve the extraction paths
        evaluated_field_paths = [field_path.eval(self.config) for field_path in self._field_path]
        target_records = self.extract_records_by_path(response, evaluated_field_paths)
        included_relations = list(self.extract_records_by_path(response, ["included"]))

        # Update target records with included records
        updated_records = self.update_target_records_with_included(target_records, included_relations)
        yield from updated_records

    @staticmethod
    def update_target_records_with_included(
        target_records: Iterable[Mapping[str, Any]], included_relations: Iterable[Mapping[str, Any]]
    ) -> Iterable[Mapping[str, Any]]:
        for target_record in target_records:
            target_relationships = target_record.get("relationships", {})

            for included_relation in included_relations:
                included_relation_attributes = included_relation.get("attributes", {})
                included_relation_type = included_relation["type"]
                included_relation_id = included_relation["id"]

                target_relationship_id = target_relationships.get(included_relation_type, {}).get("data", {}).get("id")

                if included_relation_id == target_relationship_id:
                    target_relationships[included_relation_type]["data"].update(included_relation_attributes)

            yield target_record

    def extract_records_by_path(self, response: requests.Response, field_paths: list = None) -> Iterable[Mapping[str, Any]]:
        try:
            response_body = response.json()
        except Exception as e:
            raise Exception(f"Failed to parse response body as JSON: {e}")

        # Extract data from the response body based on the provided field paths
        if not field_paths:
            extracted_data = response_body
        else:
            field_path_str = "/".join(field_paths)  # Convert list of field paths to a single string path for dpath
            if "*" in field_path_str:
                extracted_data = dpath.values(response_body, field_path_str)
            else:
                extracted_data = dpath.get(response_body, field_path_str, default=[])

        # Yield extracted data as individual records
        if isinstance(extracted_data, list):
            yield from extracted_data
        elif extracted_data:
            yield extracted_data
        else:
            yield from []


class KlaviyoErrorHandler(DefaultErrorHandler):
    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]]) -> ErrorResolution:
        """
        We have seen `[Errno -3] Temporary failure in name resolution` a couple of times on two different connections
        (1fed2ede-2d33-4543-85e3-7d6e5736075d and 1b276f7d-358a-4fe3-a437-6747fd780eed). Retrying the requests on later syncs is working
        which makes it sound like a transient issue.
        """
        if isinstance(response_or_exception, InvalidURL):
            return ErrorResolution(
                response_action=ResponseAction.RETRY,
                failure_type=FailureType.transient_error,
                error_message="source-klaviyo has faced a temporary DNS resolution issue. Retrying...",
            )
        return super().interpret_response(response_or_exception)


class PerPartitionToSingleStateMigration(StateMigration):
    """
    Transforms the input state for per-partitioned streams from the legacy format to the low-code format.
    The cursor field and partition ID fields are automatically extracted from the stream's DatetimebasedCursor and SubstreamPartitionRouter.

    Example input state:
    {
      "partition": {"event_id": "13506132"},
      "cursor": {"datetime": "2120-10-10 00:00:00+00:00"}
    }
    Example output state:
    {
      "datetime": "2120-10-10 00:00:00+00:00"
    }
    """

    declarative_stream: DeclarativeStream
    config: Config

    def __init__(self, declarative_stream: DeclarativeStream, config: Config):
        self._config = config
        self.declarative_stream = declarative_stream
        self._cursor = declarative_stream.incremental_sync
        self._parameters = declarative_stream.parameters
        self._cursor_field = InterpolatedString.create(self._cursor.cursor_field, parameters=self._parameters).eval(self._config)

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return "states" in stream_state

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        if not self.should_migrate(stream_state):
            return stream_state

        min_state = min(stream_state.get("states"), key=lambda state: state["cursor"][self._cursor_field])
        return min_state.get("cursor")
