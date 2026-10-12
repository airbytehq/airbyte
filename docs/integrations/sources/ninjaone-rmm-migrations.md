# NinjaOne RMM Migration Guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Upgrading to 0.1.0

Version 0.1.0 replaces the static **API Key** with NinjaOne OAuth 2.0 **Client Credentials**.

### What changed

- The `api_key` configuration field is removed. The connector now takes a `client_id` and `client_secret` and exchanges them for an access token at `https://<region>.ninjarmm.com/ws/oauth/token` before each sync (and again whenever the token expires).
- A new optional `region` field selects the NinjaOne instance (`app`, `us2`, `eu`, `ca` or `oc`). Previously only `app.ninjarmm.com` was supported.
- Pagination of the `organizations`, `locations` and `activities` streams now follows the NinjaOne API: `after` is sent as the last organization/location ID of the previous page, and `activities` pages backwards with `olderThan=<last activity ID>`. Earlier versions sent a record offset in these parameters, which the API interprets as an ID or a date.

### Why

The NinjaOne Public API only supports [OAuth 2.0](https://app.ninjarmm.com/apidocs-beta/authorization/overview) and its access tokens are valid for one hour (`"expires_in": 3600` in the [Client Credentials flow](https://app.ninjarmm.com/apidocs-beta/authorization/flows/client-credentials-flow)). The token that earlier versions asked you to paste as the API Key therefore stopped working an hour after it was generated, so scheduled syncs could not succeed.

### Who is affected

All users of this connector. Existing sources will fail their connection test until they are reconfigured.

### Migration steps

1. In NinjaOne, open **Administration > Apps > API** and click **Add**.
2. Select **API Services (machine-to-machine)** as the Application Platform, select at least the `Monitoring` scope, and enable the **Client Credentials** grant type.
3. Save the application and copy its **Client ID** and **Client Secret**.
4. In Airbyte, open your NinjaOne RMM source, upgrade it to 0.1.0, and enter the **Client ID**, **Client Secret** and (if your account is not on `app.ninjarmm.com`) the **Region**. Keep your existing **Start date**.
5. Click **Set up source** / **Test and save**. No stream reset is required: schemas, primary keys and cursor fields are unchanged.

## Connector upgrade guide

<MigrationGuide />
