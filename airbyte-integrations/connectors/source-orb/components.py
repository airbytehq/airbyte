#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass, field
from typing import Any, Iterable, List, Mapping, MutableMapping

import requests

from airbyte_cdk.sources.declarative.decoders import Decoder, JsonDecoder
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.declarative.types import Config, StreamSlice
from airbyte_cdk.sources.types import Record


@dataclass
class SubscriptionUsageRecordExtractor(RecordExtractor):
    """
    Custom record extractor for the subscription_usage stream.

    The Orb API returns records in the shape:
        {"data": [{"billable_metric": {...}, "usage": [{"quantity": ..., "timeframe_start": ..., ...}, ...]}, ...]}

    This extractor performs 1:N expansion: each top-level data item is expanded
    into one output record per usage sub-record that has quantity > 0.  Parent-level
    fields (billable_metric name/id) are merged into each output record.

    This cannot be done with built-in declarative components because
    RecordTransformation.transform() only supports 1:1 in-place mutation, and no
    built-in extractor supports nested array expansion with parent-field merging.
    """

    config: Config
    parameters: InitVar[Mapping[str, Any]]
    decoder: Decoder = field(default_factory=lambda: JsonDecoder(parameters={}))

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._parameters = parameters

    def extract_records(self, response: requests.Response) -> Iterable[MutableMapping[str, Any]]:
        for body in self.decoder.decode(response):
            data_items: List[Any] = body.get("data", [])
            for item in data_items:
                billable_metric = item.get("billable_metric", {})
                billable_metric_name = billable_metric.get("name", "")
                billable_metric_id = billable_metric.get("id", "")

                usage_records = item.get("usage", [])
                for subrecord in usage_records:
                    if subrecord.get("quantity", 0) > 0:
                        output: MutableMapping[str, Any] = {}
                        output.update(subrecord)
                        output["billable_metric_name"] = billable_metric_name
                        output["billable_metric_id"] = billable_metric_id
                        yield output


@dataclass
class SubscriptionUsagePartitionRouter(StreamSlicer):
    plans_stream: Any  # Stream or DefaultStream depending on CDK execution context
    subscriptions_stream: Any  # Stream or DefaultStream depending on CDK execution context
    config: Config

    @staticmethod
    def _to_dict(record: Any) -> Mapping[str, Any]:
        """Extract a plain dict from a record."""
        if isinstance(record, Record):
            return record.data  # type: ignore[return-value]
        if isinstance(record, Mapping):
            return record
        return dict(record)  # type: ignore[arg-type]

    def _read_records(self, stream: Any) -> Iterable[Mapping[str, Any]]:
        """Read records from a stream, handling both Stream and DefaultStream types.

        In CDK 6.x, parent streams injected into custom partition routers may be
        either ``Stream`` (with ``read_only_records()``) or ``DefaultStream``
        (concurrent wrapper with only ``generate_partitions()``).  This helper
        abstracts the difference so ``stream_slices`` works in both contexts.
        """
        if hasattr(stream, "read_only_records"):
            for record in stream.read_only_records():
                yield self._to_dict(record)
        elif hasattr(stream, "generate_partitions"):
            for partition in stream.generate_partitions():
                for record in partition.read():
                    yield self._to_dict(record)
        else:
            raise AttributeError(f"Stream {type(stream).__name__} has no supported method for reading records")

    def stream_slices(self) -> Iterable[StreamSlice]:
        """
        This stream is sliced per `subscription_id` and day, as well as `billable_metric_id`
        if a grouping key is provided. This is because the API only supports a
        single billable_metric_id per API call when using a group_by param.

        """
        slice_yielded = False
        subscriptions_stream = self.subscriptions_stream
        plans_stream = self.plans_stream

        # if using a group_by key, populate prices_by_plan_id so that each
        # billable metric will get its own slice
        if self.config.get("subscription_usage_grouping_key"):
            metric_ids_by_plan_id = {}

            for plan in self._read_records(plans_stream):
                # if a plan_id filter is specified, skip any plan that doesn't match
                if self.config.get("plan_id") and plan["id"] != self.config.get("plan_id"):
                    continue

                prices = plan.get("prices", [])
                metric_ids_by_plan_id[plan["id"]] = [(price.get("billable_metric") or {}).get("id") for price in prices]

        for subscription in self._read_records(subscriptions_stream):
            subscription_id = subscription["id"]
            subscription_plan_id = subscription["plan_id"]

            # if filtering subscription usage by plan ID, skip any subscription that doesn't match the plan_id
            if self.config.get("plan_id") and subscription_plan_id != self.config.get("plan_id"):
                continue

            slice = {
                "subscription_id": subscription_id,
            }

            # if using a group_by key, yield one slice per billable_metric_id.
            # otherwise, yield slices without a billable_metric_id because
            # each API call will return usage broken down by billable metric
            # when grouping isn't used.
            if self.config.get("subscription_usage_grouping_key"):
                metric_ids = metric_ids_by_plan_id.get(subscription_plan_id)
                if metric_ids is not None:
                    for metric_id in metric_ids:
                        # self.logger.warning("stream_slices is about to yield the following slice: %s", slice)
                        yield {**slice, "billable_metric_id": metric_id}
                        slice_yielded = True
            else:
                # self.logger.warning("stream_slices is about to yield the following slice: %s", slice)
                yield slice
                slice_yielded = True
        if not slice_yielded:
            # yield an empty slice to checkpoint state later
            yield {}
