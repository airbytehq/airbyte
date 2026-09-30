# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Generated due-work checks for Shopify bulk checkpoint continuation."""

import pytest
from source_shopify.streams.streams import Products


pytest.importorskip("due_work_harness")

from due_work_harness import Host, configure  # noqa: E402
from due_work_harness.contract import (  # noqa: E402
    Adoption,
    Decline,
    DueWorkContract,
    NotApplicable,
    Profile,
    SafetyContract,
    SafetyProfile,
    due_work_contract_suite,
)
from due_work_harness.crash_histories import Findings  # noqa: E402
from due_work_harness.integrations.airbyte_shopify import bulk_checkpoint_history  # noqa: E402


CONFIG = {
    "shop": "test-shop",
    "start_date": "2023-01-01",
    "credentials": {"auth_method": "api_password", "api_password": "api_password"},
    "authenticator": None,
}


configure(Host(production_packages=frozenset({"source_shopify"})))

SHOPIFY_BULK_CHECKPOINT = DueWorkContract(
    name="Airbyte Shopify bulk checkpoint continuation",
    adoption=Adoption.LEGACY,
    profiles={
        Profile.A: Decline("Airbyte platform schedules sync retries; the connector has no durable retry sweep"),
        Profile.B: NotApplicable("one connector process owns each local bulk result"),
        Profile.C: Decline("Shopify bulk operation creation has no persisted attempt record in the connector"),
        Profile.D: NotApplicable("the connector has no durable due-work retention pass"),
        Profile.E: NotApplicable("bulk result files are consumed by one stream, without competing snapshot writes"),
        Profile.F: Decline("Airbyte platform state, rather than this connector, determines which sync is due"),
    },
    safety=SafetyContract(
        name="Airbyte Shopify bulk checkpoint continuation",
        adoption=Adoption.LEGACY,
        profiles={
            SafetyProfile.REPLAY_SAFE_EXECUTION: Decline("Shopify bulk operation creation can be replayed after an uncertain outcome"),
            SafetyProfile.BOUNDED_RETRY: Decline("connector retry budget is separate from this checkpoint boundary"),
        },
    ),
    process_handoffs=(
        bulk_checkpoint_history(
            stream_type=Products,
            config=CONFIG,
            first_record={"__typename": "Product", "id": "gid://shopify/Product/1", "updatedAt": "2023-01-01T12:00:00Z"},
            later_record={"__typename": "Product", "id": "gid://shopify/Product/2", "updatedAt": "2023-01-02T06:00:00Z"},
            findings=Findings(
                delivered=((1, 2), "2023-01-02T06:00:00+00:00"),
                outcomes={"canceled without partial result URL": ((2,), "2023-01-02T06:00:00+00:00")},
            ),
        ),
    ),
    handoff_gaps={
        "self-canceled bulk job without partial result URL": "#85372: a self-canceled job with no partialDataUrl skips its undownloaded slice",
    },
)


# The decorator generates every test in this class from the contract above.
# The missing-URL history is a strict legacy XFAIL: a fix makes the case pass
# and forces its gap declaration to be removed.
@due_work_contract_suite(SHOPIFY_BULK_CHECKPOINT)
class TestShopifyBulkCheckpointDueWork:
    pass
