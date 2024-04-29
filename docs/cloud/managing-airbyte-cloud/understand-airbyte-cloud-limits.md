---
products: cloud
---

# Airbyte Cloud limits

Understanding the following limitations will help you more effectively manage Airbyte Cloud.

- Max number of workspaces per user: 3\*
- Max number of instances of the same source connector: 10\*
- Max number of destinations in a workspace: 20\*
- Max number of streams that can be returned by a source in a discover call: 1K
- Max number of streams that can be configured to sync in a single connection: 1K
- Max number of fields that can be selected to sync in a single connection: 20k
- Size of a single record: 20MB\*\*

---

\* Limits on workspaces, sources, and destinations do not apply to customers of
[Powered by Airbyte](https://airbyte.com/solutions/powered-by-airbyte). To learn more
[contact us](https://airbyte.com/talk-to-sales)!

\*\* The effective maximum size of the record may vary based per destination. Some destinations may
fail to sync if a record cannot be stored, but Destinations which support
[typing and deduping](/using-airbyte/core-concepts/typing-deduping) will adjust your record so that
the sync does not fail, given the database/file constraints. For example, the maximum size of a
record in MongoDB is 16MB - records larger than that will need to be modified. At the very least,
primary keys and cursors will be maintained. Any modifications to the record will be stored within
`airbyte_meta.changes` for your review within the destination.
