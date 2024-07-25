## Streams

Orb is a REST API. Connector has the following streams, and all of them support incremental refresh.

- [Subscriptions](https://docs.withorb.com/reference/list-subscriptions)
- [Plans](https://docs.withorb.com/reference/list-plans)
- [Customers](https://docs.withorb.com/reference/list-customers)
- [Credits Ledger Entries](https://docs.withorb.com/reference/view-credits-ledger)
- [Invoices](https://docs.withorb.com/docs/orb-docs/api-reference/schemas/invoice)

Note that the Credits Ledger Entries must read all Customers for an incremental sync, but will only incrementally return new ledger entries for each customer.

Since the Orb API does not allow querying objects based on `updated_at`, these incremental syncs will capture updates to newly created objects but not resources updated after object creation. Use a full resync in order to capture newly updated entries.

## Pagination

Orb's API uses cursor-based pagination, which is documented [here](https://docs.withorb.com/reference/pagination).

## Enriching Credit Ledger entries

The connector configuration includes two properties: `numeric_event_properties_keys` and `string_event_properties_keys`.

When a ledger entry has an `event_id` attached to it (e.g. an automated decrement), the connector will make a follow-up request to enrich those entries with event properties corresponding to the keys provided. The connector assumes (and generates schema) that property values corresponding to the keys listed in `numeric_event_properties_keys` are numeric, and the property values corresponding to the keys listed in `string_event_properties_keys` are string typed.

## Authentication

This connector authenticates against the Orb API with an API key that can be issued via the Orb Admin Console.

Please reach out to the Orb team at [team@withorb.com](mailto:team@withorb.com) to request an Orb Account and API Key.
