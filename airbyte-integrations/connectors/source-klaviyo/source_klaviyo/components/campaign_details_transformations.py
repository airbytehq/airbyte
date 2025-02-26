# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging
from typing import Any, Dict, Mapping, Optional

from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies import WaitTimeFromHeaderBackoffStrategy
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.message.repository import InMemoryMessageRepository
from airbyte_cdk.sources.streams.call_rate import APIBudget
from airbyte_cdk.sources.streams.http.error_handlers import BackoffStrategy, ErrorHandler, HttpStatusErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import DEFAULT_ERROR_MAPPING
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ErrorResolution, FailureType, ResponseAction
from airbyte_cdk.sources.streams.http.http_client import HttpClient
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState


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
