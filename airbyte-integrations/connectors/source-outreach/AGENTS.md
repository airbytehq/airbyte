# Contributing to source-outreach

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Rotating Refresh Tokens

Outreach rotates refresh tokens on every successful refresh, invalidating the previously issued token. The manifest's `refresh_token_updater` persists the replacement refresh token, access token, and expiry date in the top-level connection configuration; keep these settings in sync with the OAuth authenticator. The shared requester refreshes the access token and retries API requests rejected with HTTP 401 so long paginated syncs can continue.
