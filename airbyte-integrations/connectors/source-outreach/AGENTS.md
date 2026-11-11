# source-outreach: Unique Connector Behaviors

## 1. Authentication recovery during long syncs

[Outreach OAuth access tokens](https://developers.outreach.io/api/oauth/) have a
limited lifetime (the documented example is 7,200 seconds). An API request can
receive HTTP 401 even when the connector's local token expiry has not passed.
The shared requester uses `REFRESH_TOKEN_THEN_RETRY` to force an OAuth refresh and
retry the same page. The CDK stops with a configuration error if that request is
rejected again after refresh. HTTP 403 permission failures retain their normal
fatal handling.

**Why this matters:** Ordinary retries can resend the same locally valid but
server-rejected token. Preserve the forced refresh action so large streams can
continue across token expiration without skipping the interrupted page.
