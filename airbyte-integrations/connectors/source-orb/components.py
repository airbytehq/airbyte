#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Iterable, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.declarative.transformations.transformation import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.sources.streams.core import Stream


@dataclass
class SubscriptionUsageTransformation(RecordTransformation):
    subscription_id: str

    def transform(
        self,
        record: Record,
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Record:
        # for each top level response record, there can be multiple sub-records depending
        # on granularity and other input params. This function yields one transformed record
        # for each subrecord in the response.

        subrecords = record.get("usage", [])
        del record["usage"]
        for subrecord in subrecords:
            # skip records that don't contain any actual usage
            if subrecord.get("quantity", 0) > 0:
                # Merge the parent record with the sub record
                output = record.update(subrecord)

                # Add the subscription ID to the output
                output["subscription_id"] = self.subscription_id

                # Un-nest billable_metric -> name,id into billable_metric_name and billable_metric_id
                nested_billable_metric_name = output["billable_metric"]["name"]
                nested_billable_metric_id = output["billable_metric"]["id"]
                del output["billable_metric"]
                output["billable_metric_name"] = nested_billable_metric_name
                output["billable_metric_id"] = nested_billable_metric_id

                # If a group_by key is specified, un-nest it
                if config.subscription_usage_grouping_key:
                    nested_key = output["metric_group"]["property_key"]
                    nested_value = output["metric_group"]["property_value"]
                    del output["metric_group"]
                    output[nested_key] = nested_value
                yield output
        yield from []


@dataclass
class SubscriptionUsagePartitionRouter(StreamSlicer):
    plans_stream: Stream
    subscriptions_stream: Stream
    config: Config

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

            for plan in plans_stream.read_records(sync_mode=SyncMode.full_refresh):
                # if a plan_id filter is specified, skip any plan that doesn't match
                if self.config.get("plan_id") and plan["id"] != self.config.get("plan_id"):
                    continue

                prices = plan.get("prices", [])
                metric_ids_by_plan_id[plan["id"]] = [(price.get("billable_metric") or {}).get("id") for price in prices]

        for subscription in subscriptions_stream.read_records(sync_mode=SyncMode.full_refresh):
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
