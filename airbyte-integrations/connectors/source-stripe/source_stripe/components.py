from typing import Iterable, Mapping, Any, Optional, Set, Dict
from datetime import timedelta, datetime
from airbyte_cdk.sources.declarative.partition_routers import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.types import StreamSlice
from collections import Counter

class CustomerIdPartitionRouter(SubstreamPartitionRouter):
    def __init__(self, stream_state: Optional[Mapping[str, Any]] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stream_state = stream_state
        self.logger.info(f"[CustomerIdPartitionRouter] State after CustomStateMigration: {self._stream_state}")

    def _extract_metadata(self, slice: Dict[str, Any]) -> tuple[Optional[str], Optional[str], float]:
        extras = getattr(slice, "_extra_fields", {})
        object_type = extras.get("object")
        customer_id = slice.get("customer_id")
        balance_or_total = extras.get("balance", 0) if object_type == "customer" else extras.get("total", 0)
        return customer_id, object_type, balance_or_total

    def stream_slices(self) -> Iterable[StreamSlice]: # type: ignore
        parent_slices = list(super().stream_slices())
        seen_customer_ids: Set[str] = set()
        unique_slices = []
        totals = Counter()

        for slice in parent_slices:
            customer_id, object_type, balance_or_total = self._extract_metadata(slice)

            if object_type == "customer":
                totals["customers"] += 1
            elif object_type == "invoice":
                totals["invoices"] += 1

            if customer_id and customer_id not in seen_customer_ids and balance_or_total != 0:
                seen_customer_ids.add(customer_id)
                unique_slices.append(slice)
            else:
                totals["skipped"] += 1

        self.logger.info(f"[CustomerIdPartitionRouter] Total parent slices: {len(parent_slices)}")
        self.logger.info(f"[CustomerIdPartitionRouter] Total customer records: {totals['customers']}")
        self.logger.info(f"[CustomerIdPartitionRouter] Total invoice records: {totals['invoices']}")
        self.logger.info(f"[CustomerIdPartitionRouter] Unique slices emitted: {len(unique_slices)}")
        self.logger.info(f"[CustomerIdPartitionRouter] Skipped records: {totals['skipped']}")

        yield from unique_slices

class CustomerBalanceStateMigration(StateMigration):
    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return "parent_state" in stream_state

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        current_state = stream_state or {}
        state_created = int(current_state.get("state", {}).get("created", 0))
        current_parent_state = current_state.get("parent_state", {})

        two_days = int(timedelta(days=2).total_seconds())
        fourteen_day_floor = int(datetime.utcnow().timestamp()) - int(timedelta(days=14).total_seconds())

        created_customer_balance_transactions = max(state_created - two_days, fourteen_day_floor, 0)
        updated_customers = max(0, current_parent_state.get("customers", {}).get("updated", 0) - two_days, fourteen_day_floor)
        updated_invoices = max(0, current_parent_state.get("invoices", {}).get("updated", 0) - two_days, fourteen_day_floor)

        migrated_state = {
            "state": {
                "created": created_customer_balance_transactions
            },
            "parent_state": {
                "customers": {
                    "updated": updated_customers
                },
                "invoices": {
                    "updated": updated_invoices
                }
            },
            "use_global_cursor": True
        }

        return migrated_state

