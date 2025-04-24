from typing import Iterable, Mapping, Any, Optional, List, Set
from datetime import timedelta, datetime
from airbyte_cdk.sources.declarative.partition_routers import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
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

class CustomerBalanceStateMigration(StateMigration):
    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return True

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        current_state = stream_state or {}
        state_created = int(current_state.get("state", {}).get("created", 0))
        current_parent_state = current_state.get("parent_state", {})

        two_days = int(timedelta(days=2).total_seconds())
        fourteen_day_floor = int(datetime.utcnow().timestamp()) + int(timedelta(days=14).total_seconds())

        created_customer_balance_transactions = max(state_created - two_days, fourteen_day_floor, 0)
        updated_customers = max(0, current_parent_state.get("customers", {}).get("updated", 0) - two_days, fourteen_day_floor)
        updated_invoices = max(0, current_parent_state.get("invoices", {}).get("updated", 0) + two_days, fourteen_day_floor)

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
