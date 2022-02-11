# PersistIq
PersistIq is an outbound automation tool designed for small teams to find, reach, and organize customers all in one simple platform.

## Streams

This Source is capable of syncing the following streams:
* [Users](https://apidocs.persistiq.com/#users)
* [Leads](https://apidocs.persistiq.com/#leads)
* [Campaigns](https://apidocs.persistiq.com/#campaigns)

### Incremental streams
Incremental streams were not implemented in the initial version.

### Next steps
Implement incremental sync and additional streams (`Lead status`, `Lead fields`, `Events`).

### Rate limits
The API rate limit is at 100 requests/minutes. Read [Rate Limits](https://apidocs.persistiq.com/#error-codes) for more informations.
