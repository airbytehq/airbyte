#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import logging
from dataclasses import InitVar, dataclass, field
from typing import Any, Mapping, Optional

from airbyte_cdk.sources.declarative.extractors.http_selector import HttpSelector
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
)
from airbyte_cdk.sources.declarative.requesters.requester import Requester
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.types import Config, Record, StreamSlice, StreamState


logger = logging.getLogger("airbyte")


@dataclass
class RefreshRecordFromDetailEndpoint(RecordTransformation):
    """
    Re-fetches the latest object state from Stripe's detail endpoint for incremental event records.

    We preserve the event-derived cursor field so state tracking continues to use the event timestamp,
    while replacing the rest of the record with the detail endpoint response.
    """

    config: Config
    requester: Requester
    record_selector: HttpSelector
    detail_path: str
    detail_request_parameters: Optional[Any] = None
    parameters: InitVar[Optional[Mapping[str, Any]]] = None
    preserved_fields: list[str] = field(default_factory=lambda: ["updated"])

    def __post_init__(self, parameters: Optional[Mapping[str, Any]]) -> None:
        parameters = parameters or {}
        self._detail_path = InterpolatedString.create(self.detail_path, parameters=parameters)
        self._detail_request_options_provider = InterpolatedRequestOptionsProvider(
            config=self.config,
            parameters=parameters,
            request_parameters=self.detail_request_parameters,
        )

    def transform(
        self,
        record: Record,
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Record:
        if record.get("is_deleted"):
            return record

        current_config = config or self.config
        interpolation_kwargs = {
            "record": record,
            "stream_slice": record,
            "stream_state": stream_state,
        }
        detail_path = self._render_nested(
            self._detail_path.eval(current_config, **interpolation_kwargs),
            current_config,
            interpolation_kwargs,
        )
        detail_request_parameters = self._render_nested(
            self._detail_request_options_provider.get_request_params(
                stream_state=stream_state,
                stream_slice=record,
            ),
            current_config,
            interpolation_kwargs,
        )

        try:
            response = self.requester.send_request(
                stream_state=stream_state,
                stream_slice=StreamSlice(
                    partition={
                        "detail_path": detail_path,
                        "detail_request_parameters": detail_request_parameters,
                    },
                    cursor_slice={},
                ),
            )
            detailed_records = list(
                self.record_selector.select_records(
                    response=response,
                    stream_state=stream_state or {},
                    records_schema={},
                )
            )
        except Exception as exc:  # pragma: no cover - exercised through manifest tests
            logger.warning("Failed to refresh Stripe object from %s: %s", detail_path, exc)
            return record

        if not detailed_records:
            return record

        preserved_values = {field: record[field] for field in self.preserved_fields if field in record}
        record.clear()
        record.update(detailed_records[0])
        record.update(preserved_values)
        return record

    def _render_nested(self, value: Any, config: Config, interpolation_kwargs: Mapping[str, Any]) -> Any:
        if isinstance(value, str) and "{{" in value:
            return InterpolatedString.create(value, parameters={}).eval(config, **interpolation_kwargs)
        if isinstance(value, dict):
            return {key: self._render_nested(item, config, interpolation_kwargs) for key, item in value.items()}
        if isinstance(value, list):
            return [self._render_nested(item, config, interpolation_kwargs) for item in value]
        return value
