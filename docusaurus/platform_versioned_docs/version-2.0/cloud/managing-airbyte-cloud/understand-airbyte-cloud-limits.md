---
products: cloud
---

# Airbyte Cloud limits

Understanding the following limitations will help you more effectively manage Airbyte Cloud.

## Standard plan limitations

These limitations only apply to those using the Standard plan. If you upgrade to Pro or Enterprise Flex, Airbyte removes these limitations.

- Max number of workspaces per user: 1. If you were a Cloud Standard customer before September 24, 2025, Airbyte has grandfathered you into its historical 3-workspace limit.

- Max number of instances of the same source connector: 10

- Max number of destinations in a workspace: 20

## Cloud limitations for all plans

- Max number of streams that can be returned by a source in a discover call: 1,000

- Max number of streams that can be configured to sync in a single connection: 1,000

- Max number of fields that can be selected to sync in a single connection: 20,000

- Size of a single record: 20MB\*\*

\*\* The effective maximum size of the record may vary based per destination. Some destinations may
fail to sync if a record cannot be stored, but Destinations which support
[typing and deduping](/platform/using-airbyte/core-concepts/typing-deduping) will adjust your record so that
the sync does not fail, given the database/file constraints. For example, the maximum size of a
record in MongoDB is 16MB - records larger than that will need to be modified. At the very least,
primary keys and cursors will be maintained. Any modifications to the record will be stored within
`airbyte_meta.changes` for your review within the destination.
