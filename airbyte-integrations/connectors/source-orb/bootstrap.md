## Streams

Orb is a REST API. Connector has the following streams, and all of them support incremental refresh.

* [Subscriptions]( https://docs.withorb.com/reference/list-subscriptions)
* [Plans](https://docs.withorb.com/reference/list-plans)
* [Customers](https://docs.withorb.com/reference/list-customers) 
* [Credits Ledger Entries](https://docs.withorb.com/reference/view-credits-ledger)

Note that the Credits Ledger Entries must read all Customers for an incremental sync, but will only incrementally return new ledger entries for each customer.

Since the Orb API does not allow querying objects based on `updated_at`, these incremental syncs will capture updates to newly created objects but not resources updated after object creation.

## Authentication

This connector authenticates against the Orb API with an API key that can be issued via the Orb Admin Console.

Please reach out to the Orb team at [team@withorb.com](mailto:team@withorb.com) to request an Orb Account and API Key.