# Metabase

## Overview

Metabase is an open-source Data Visualization tool popular for business intelligence applications.
It also offers embeddable charts and interactive dashboards, GUI and SQL editors to create questions or cards
that queries data from major data warehouses and databases with auditing and data sandboxing features, and more.

Just like Airbyte, it offers the options for deployment:
- self-hosted through their Open-Source or licensed (paid) versions which unlock more features.
- cloud managed by Metabase for their paying customers.

## Endpoints

This source connector uses Metabase API which can be both from a self-hosted or cloud-managed instance and uses HTTP as protocol.

## Quick Notes

Following the [introduction document to Metabase's API](https://www.metabase.com/learn/administration/metabase-api.html), there is currently
only one authentication method using a session token to authenticate requests.

To get a session token, one needs to submit a request to the /api/session endpoint with a username and password:
By default, such sessions are good for 14 days and the credentials tokens should be cached to be reused until they expire,
because logins are rate-limited for security. Invalid and expired session tokens return a 401 (Unauthorized) status code.

Because of this, the connector configuration needs to be supplied with the session_token id as the connector is not able to
edit its own configuration with the new value everytime it runs.

A consequence of this limitation is that the configuration of the connector will have to be updated when the credential token expires
(every 14 days). Unless, the airbyte-server is able to refresh this token and persist the value of the new token. 

If the connector is supplied with only username and password, a session_token will be generated everytime an 
authenticated query is running, which might trigger security alerts on the user's account.

All the API from metabase don't seem to support incremental sync modes as they don't expose cursor field values or pagination.
So all streams only support full refresh sync modes for the moment.

## API Reference

The Metabase reference documents: [Metabase API documentation](https://www.metabase.com/docs/latest/api-documentation.html)

