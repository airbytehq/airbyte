---
products: cloud
---

# Airbyte Cloud limits

Understanding the following limitations will help you more effectively manage Airbyte Cloud.

* Max number of workspaces per user: 3*
* Max number of instances of the same source connector: 10*
* Max number of destinations in a workspace: 20*
* Max number of streams that can be returned by a source in a discover call: 1K
* Max number of streams that can be configured to sync in a single connection: 1K
* Size of a single record: 20MB
  * A flag can be set in order to log the PKs of the record that are skipped because of a size limit. In order to do that,
the following entry need to be added to the file `flag.yml`: 
```yaml
  - name: platform.print-long-record-pks
    serve: true
```
  * It is possible to not fail the syncs and instead skip the records by adding the following entry to the file `flag.yml`
```yaml
  - name: platform.fail-sync-if-too-big
    serve: false
```

*Limits on workspaces, sources, and destinations do not apply to customers of [Powered by Airbyte](https://airbyte.com/solutions/powered-by-airbyte). To learn more [contact us](https://airbyte.com/talk-to-sales)!
