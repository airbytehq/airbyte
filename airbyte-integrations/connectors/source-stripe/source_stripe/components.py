from typing import Iterable, Mapping, Any, Optional, List, Set

from airbyte_cdk.sources.declarative.partition_routers import SubstreamPartitionRouter
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.types import StreamSlice

class CustomerIdPartitionRouter(SubstreamPartitionRouter):
    def stream_slices(self) -> Iterable[StreamSlice]: # type: ignore
        parent_slices = list(super().stream_slices())
        seen_customer_ids: Set[str] = set()
        unique_slices = []

        for slice in parent_slices:
            customer_id = slice.get("customer_id")
            if customer_id and customer_id not in seen_customer_ids:
                seen_customer_ids.add(customer_id)
                self.logger.info(f"[CustomerIdPartitionRouter] Unique slice for customer_id={customer_id}")
                unique_slices.append(slice)
            else:
                self.logger.info(f"[CustomerIdPartitionRouter] Skipping duplicate customer_id={customer_id}")

        self.logger.info(f"[CustomerIdPartitionRouter] Emitting {len(unique_slices)} unique slices")
        yield from unique_slices
