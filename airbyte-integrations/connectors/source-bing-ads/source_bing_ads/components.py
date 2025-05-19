#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from dataclasses import InitVar, dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional

from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.partition_routers import PartitionRouter
from airbyte_cdk.sources.declarative.types import Config, StreamSlice, StreamState


@dataclass
class AccountsPartitionRouter(PartitionRouter):
    """
    A custom partition router for the Accounts stream that emulates
    the original Python implementation.
    This router creates a stream slice with a user ID.
    """

    config: Optional[Config] = None
    parameters: InitVar[Mapping[str, Any]] = None

    # Add state management
    _state: Dict[str, Any] = field(default_factory=dict, init=False)
    _logger: logging.Logger = field(default_factory=lambda: logging.getLogger("airbyte"), init=False)

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self.parameters = parameters or {}

    def stream_slices(self) -> Iterable[StreamSlice]:
        """
        Create a stream slice with a user ID.

        For simplicity, we'll use a direct approach to create slices with user ID.
        """
        # Try to get the user ID directly from the original implementation
        try:
            from source_bing_ads.client import Client

            self._logger.info("Creating client to get user ID")
            client = Client(
                client_id=self.config["client_id"],
                client_secret=self.config.get("client_secret", ""),
                refresh_token=self.config["refresh_token"],
                tenant_id=self.config.get("tenant_id", "common"),
                developer_token=self.config["developer_token"],
            )

            # The original implementation directly calls GetUser() in the base class,
            # let's replicate that behavior without instantiating the abstract class
            service = client.get_service(service_name="CustomerManagementService")
            user_id = str(service.GetUser().User.Id)

            self._logger.info(f"Successfully retrieved user ID: {user_id}")

        except Exception as e:
            # Fall back to using "0" as a placeholder if we can't get a real user ID
            self._logger.error(f"Failed to get user ID: {str(e)}")
            user_id = "0"

        self._logger.info(f"Using user_id: {user_id}")

        # Create a single slice with the user ID
        yield StreamSlice(partition={"user_id": str(user_id)}, cursor_slice={}, extra_fields={})

    def get_request_params(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return {}

    def get_request_headers(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return {}

    def get_request_body_data(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return {}

    def get_request_body_json(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        # This is where we inject the user ID into the request body
        if stream_slice and "user_id" in stream_slice.partition:
            user_id = stream_slice.partition["user_id"]
            self._logger.info(f"Adding user_id to request: {user_id}")
            return {"Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": user_id}]}
        return {}

    def get_stream_state(self) -> StreamState:
        """
        Get the current state of the stream.
        This router doesn't track any state.
        """
        return self._state

    def set_initial_state(self, stream_state: StreamState) -> None:
        """
        Set the initial state of the stream.
        This router doesn't need to track any state.
        """
        self._state = stream_state or {}


@dataclass
class DedupingAccountsExtractor(RecordExtractor):
    """
    A record extractor to match deduplication behavior from the Python-based accounts stream
    Records are deduplicated based on the "Id" field.
    """

    # Required parameters that come from the declarative framework
    config: Optional[Config] = None
    parameters: InitVar[Mapping[str, Any]] = None  # Changed from default_factory

    # Optional parameters with default values
    field_path: List[str] = field(default_factory=lambda: ["Accounts"])
    primary_key: str = "Id"

    # Fields not passed as parameters
    _seen_ids: set = field(default_factory=set, init=False)
    _dpath_extractor: DpathExtractor = field(init=False)

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        """Initialize after dataclass initialization"""
        self.parameters = parameters or {}
        self._dpath_extractor = DpathExtractor(field_path=self.field_path, config=self.config, parameters=parameters or {})

    def extract_records(self, response: Any) -> List[Mapping[str, Any]]:
        """
        Extract records from the response and deduplicate based on primary key.
        """
        # Use the standard extractor to get all records
        all_records = self._dpath_extractor.extract_records(response)

        # Filter out duplicates
        unique_records = []
        for record in all_records:
            record_id = record.get(self.primary_key)
            if record_id not in self._seen_ids:
                self._seen_ids.add(record_id)
                unique_records.append(record)

        return unique_records
