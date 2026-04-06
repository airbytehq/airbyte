# Workday Migration Guide

## Upgrading to 1.0.0

This release splits Source Workday into two separate connectors - Source Workday (for RaaS streams) and Source Workday REST (for REST streams).
The connector you're currently using is deprecating REST streams and will continue to support only RAAS streams. REST streams will be available in the new Source Workday REST.

Action required only if you were using this source to sync REST streams (REST authentication on Setup Page). In that case, you will need to disable this connection and create a new connection using new Source Workday REST. Otherwise, simply upgrade this source to v1.0.0 and continue syncing RaaS streams as usual.

Migration Steps:

1. Go to your connection that is uses Source Workday and syncs REST streams.
2. Disable the connection using toggle on the top right.
3. Go to Sources Page and select `+ New source`, find and select Source Workday REST.
4. Set up the new Source Workday REST.
5. Define destination.
6. Select streams to sync.
7. Configure connection.
