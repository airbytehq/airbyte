> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-shopify

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Shopify REST API supports `updated_at_min` filtering on most resource endpoints. The connector is a Python CDK connector with `IncrementalShopifyStream`, `IncrementalShopifySubstream`, and `IncrementalShopifyNestedStream` classes providing layered incremental patterns.

**Connector type:** Python CDK

**Analysis status:** Pure Python CDK connector with comprehensive incremental patterns. Full stream-by-stream analysis requires Python code review.

### Discount code streams re-sync every code of an updated discount

`discount_codes` (bulk) and `discount_codes_sync` (synchronous) are incremental only at the discount level. Shopify's `DiscountRedeemCode` has no `updatedAt`, so both streams filter discounts by `updated_at` and then emit **every** code of each matched discount. For discounts with many codes, an incremental sync can behave much like a full refresh. This is documented as a user-facing warning in `docs/integrations/sources/shopify.md` ([#88422](https://github.com/airbytehq/airbyte/pull/88422), oncall [#13626](https://github.com/airbytehq/oncall/issues/13626)).

Don't try to make these streams incremental per code without new Shopify API support. There is no field that works as a reliable cursor:

- Codes change after they're created. `asyncUsageCount` (emitted as `usage_count`) changes on every redemption, and the REST API can rename a code in place under the same ID. A cursor on `createdAt` or on the code `id` only catches new codes and silently misses these updates.
- The `codes` connection can only be filtered by `id` and `times_used`. Shopify doesn't document that code IDs are assigned in ascending order, so an `id:>{last_id}` watermark can also miss newly created codes.
- Comparing the number of synced codes with the discount's `codesCount` doesn't close the gap. It can't detect updated codes, and Shopify reports counts above 10,000 as approximate.

An opt-in `discount_codes_sync_new_codes_only` option that tracked the highest code ID per discount was prototyped in #88422 and dropped for these reasons.

### `transactions` re-emits every transaction of an updated order

Shopify transactions have no `updatedAt`, so both `transactions` variants (`Transactions` over REST and `TransactionsGraphql` over GraphQL BULK) keep `created_at` as the cursor. Transactions still change after creation, for example a refund goes from `PENDING` to `SUCCESS`, and that change updates the parent order. Both variants only read orders updated since the previous sync, so they emit every transaction of those orders and don't filter records by the saved `created_at` cursor (`should_emit_record_older_than_state` returns `True`). The cursor still only moves forward.

Don't reintroduce a `created_at >= state` filter on these streams. It silently drops status changes ([airbyte-internal-issues#19163](https://github.com/airbytehq/airbyte-internal-issues/issues/19163)) and transactions that offsite gateways create before their order ([#87638](https://github.com/airbytehq/airbyte/pull/87638)). The cost is that unchanged transactions of an updated order are emitted again, which is documented for users in `docs/integrations/sources/shopify.md`.

### Future incremental stream candidates

- **All streams deferred for Python code review:** This connector defines its streams in Python code rather than declarative manifest YAML. A full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added by a future agent after reviewing the Python stream definitions, their `cursor_field` properties, and the API endpoints they call.
