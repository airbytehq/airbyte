# Workday Migration Guide

## Upgrading to 1.0.0


This release splits Source Workday into two separate connectors - Source Workday and Source Workday REST. 


Connector you're currently using deprecates REST streams and continues to support only RAAS streams, REST streams will be available in the new Source Workday REST. 

Action required only if you were using this source to sync REST streams (REST authentication on Set Up page), you'll need to disable this connection and create a new connection using new Source Workday REST. Otherwise, simply upgrade this source to v1.0.0 and continue syncing RAAS streams as usual.

Migration Steps:

1. Go to yor connection that is uses Source Workday and syncs REST streams.
2. Disable the connectio using toggle on the top right.
3. Go to sources page and select `+ New source`, find and select Source Workday REST.
4. Set up the new Source Workday REST.
5. Define destination.
6. Select streams to sync.
7. Configure connection.
