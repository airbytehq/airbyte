#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Iterable

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.types import Record, StreamSlice, StreamState


class CustomerIdPartitionRouter(SubstreamPartitionRouter):
    """
    A SurveyIdPartitionRouter is specifically tailored for survey data, addressing the limitations of the current solution,
    SubstreamPartitionRouter, which only offers one option for partitioning via access to the parent stream with input.
    The SurveyIdPartitionRouter generates stream slices for partitioning based on either provided survey IDs or parent stream keys.


    Inherits from:
        SubstreamPartitionRouter

    Custom Methods:
        is_unique: Checks if customer_id has been seen before in one of the update streams.
        stream_slices: Generates stream slices for partitioning.

    Overridden Methods:
        read_records
        get_updated_state
    """

    def is_unique(self, customer_id, seen):
        """Check if customer_id has been seen before."""
        hash_key = hashlib.md5(customer_id.encode()).hexdigest()
        if hash_key in seen:
            return False
        seen.add(hash_key)
        return True

    def stream_slices(self) -> Iterable[StreamSlice]:
        """
        Generates stream slices for partitioning based on survey IDs or parent stream keys.
        """
        # Iterate over parent stream records and yield slices based on parent keys
        for parent_stream_config in self.parent_stream_configs:
            parent_key = parent_stream_config.parent_key.string
            partition_field = parent_stream_config.partition_field.string
            for item in parent_stream_config.stream.read_records(sync_mode=SyncMode.full_refresh):
                process = False
                if parent_key == "customer":
                    invoice = item
                    customer_id = invoice.get("customer")
                    total_amount = invoice.get("total", 0)
                    invoice_created = invoice.get(self.cursor_field, 0)
                    if customer_id and total_amount != 0 and invoice_created > last_cursor:
                        process = self.is_unique(customer_id, seen):                     
                else: 
                    customer = item
                    customer_id = customer.get("id")
                    balance = customer.get("balance", 0)
                    customer_created = customer.get(self.cursor_field, 0)
                    if customer_id and balance != 0 and customer_created > last_cursor:
                        process = self.is_unique(customer_id, seen):

                if process:
                    yield StreamSlice(partition={partition_field: item[parent_key]}, cursor_slice={})

        # Ensures the function always returns an iterable
        yield from []

    # WJK - not sure if this will still override read_records correctly or if it needs to be defined a different way?
    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        Calls the Stripe API for each customer ID and retrieves balance transactions.
        """
        customer_id = stream_slice["id"]
        path = f"customers/{customer_id}/balance_transactions"
        response = self._send_request(path, stream_state=stream_state, stream_slice=stream_slice)

        data = response.json().get("data", [])
        if not data:
            self.logger.info(f"No balance transactions found for customer: {customer_id}")

        current_cursor = stream_state.get(self.cursor_field, 0) if stream_state else 0
        max_cursor = current_cursor

        for record in self.record_extractor.extract_records(response.json().get("data", []), stream_slice):
            self.logger.info(f"Extracted balance transaction: {record}")
            yield {"customer_id": customer_id, **record}
            record_cursor = record.get(self.cursor_field, 0)
            max_cursor = max(max_cursor, record_cursor)

        if max_cursor > current_cursor:
            yield self.get_updated_state(stream_state, {self.cursor_field: max_cursor})

    def get_updated_state(self, current_stream_state: Mapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Updates the cursor to track only new transactions.
        """
        current_cursor = current_stream_state.get(self.cursor_field, 0) if current_stream_state else 0
        latest_cursor = latest_record.get(self.cursor_field, 0)
        # Apply 30-day lookback when updating the cursor
        adjusted_cursor = max(latest_cursor - int(timedelta(days=30).total_seconds()), 0)

        new_state = {self.cursor_field: max(current_cursor, adjusted_cursor)}
        self.logger.info(f"Updated cursor state: {new_state}")

        return new_state