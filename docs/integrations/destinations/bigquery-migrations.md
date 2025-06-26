# BigQuery Migration Guide

## Upgrading to 3.0.0

This version upgrades Destination BigQuery to the [Direct-Load](/platform/using-airbyte/core-concepts/direct-load-tables) paradigm, which improves performance and reduces warehouse spend. If you have unusual requirements around record visibility or schema evolution, read that document for more information about how direct-load differs from Typing and Deduping.

This version also adds an option to enable CDC deletions as soft-deletes.

If you do not interact with the raw tables, you can safely upgrade. There is no breakage for this usecase.

If you _only_ interact with the raw tables, make sure that you have the `Disable Final Tables` option enabled before upgrading. This will automatically enable the `Legacy raw tables` option after upgrading.

If you interact with both the raw _and_ final tables, this usecase will no longer be directly supported. You must create two connectors (one with `Disable Final Tables` enabled, and one with it disabled) and run two connections in parallel.

## Upgrading to 2.0.0

This version introduces [Destinations V2](/release_notes/upgrading_to_destinations_v2/#what-is-destinations-v2), which provides better error handling, incremental delivery of data for large syncs, and improved final table structures. To review the breaking changes, and how to upgrade, see [here](/release_notes/upgrading_to_destinations_v2/#quick-start-to-upgrading). These changes will likely require updates to downstream dbt / SQL models, which we walk through [here](/release_notes/upgrading_to_destinations_v2/#updating-downstream-transformations). Selecting `Upgrade` will upgrade **all** connections using this destination at their next sync. You can manually sync existing connections prior to the next scheduled sync to start the upgrade early.

Worthy of specific mention, this version includes:

- Per-record error handling
- Clearer table structure
- Removal of sub-tables for nested properties
- Removal of SCD tables

Learn more about what's new in Destinations V2 [here](/platform/using-airbyte/core-concepts/typing-deduping).
