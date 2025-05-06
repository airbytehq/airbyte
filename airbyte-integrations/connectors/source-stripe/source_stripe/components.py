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
    A CustomerIdPartitionRouter is specifically tailored for customer balance transactions and requires both
    invoices and customers to detect POTENTIAL incremental changes.


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
            sync_mode = SyncMode.incremental if parent_stream_config.incremental_dependency.boolean else SyncMode.full_refresh
            for item in parent_stream_config.stream.read_records(sync_mode=sync_mode):
                process = False
                if parent_key == "customer":
                    invoice = item
                    customer_id = invoice.get("customer")
                    total_amount = invoice.get("total", 0)
                    created = invoice.get(self.cursor_field, 0)
                    if customer_id and total_amount != 0 and created > last_cursor:
                        process = self.is_unique(customer_id, seen):                     
                else: 
                    customer = item
                    customer_id = customer.get("id")
                    balance = customer.get("balance", 0)
                    created = customer.get(self.cursor_field, 0)
                    if customer_id and balance != 0 and created > last_cursor:
                        process = self.is_unique(customer_id, seen):

                if process:
                    yield StreamSlice(partition={id: customer_id}, cursor_slice={created: created})

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

        last_cursor = stream_state.get(self.cursor_field, 0) if stream_state else 0
        latest_cursor = last_cursor

        for record in self.record_extractor.extract_records(response.json().get("data", []), stream_slice):
            self.logger.info(f"Extracted balance transaction: {record}")
            yield {"customer_id": customer_id, **record}
            current_cursor = record.get(self.cursor_field, 0)
            latest_cursor = max(latest_cursor, current_cursor)

        updated_state = self.get_updated_state(stream_state, {self.cursor_field: latest_cursor})
        self.logger.info(f"Final cursor update after batch: {updated_state}")
        return updated_state

    def get_updated_state(self, current_stream_state: Mapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Updates the cursor to track only new transactions.
        """
        current_cursor = current_stream_state.get(self.cursor_field, 0) if current_stream_state else 0
        latest_cursor = latest_record.get(self.cursor_field, 0)
        last_successful_run = int(datetime.now().timestamp())  # Use current timestamp as last successful run
        adjusted_cursor = max(last_successful_run - int(timedelta(days=15).total_seconds()), current_cursor)

        if latest_cursor > current_cursor:
            self.logger.info(f"Updated cursor to latest record: {latest_cursor}")
            return {self.cursor_field: latest_cursor}

        self.logger.info(f"No new data, keeping cursor at: {adjusted_cursor}")
        return {self.cursor_field: adjusted_cursor}
