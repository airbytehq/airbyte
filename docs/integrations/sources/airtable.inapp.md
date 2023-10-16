:::info
Currently, this source connector works with `Standard` subscription plan only. `Enterprise` level accounts are not supported yet.
:::

## Prerequisites

* An active Airtable account

## Setup guide
1. Name your source.
2. You can use OAuth or a Personal Access Token to authenticate your Airtable account. We recommend using OAuth for Airbyte Cloud.
   - To authenticate using OAuth, select **OAuth2.0** from the Authentication dropdown click **Authenticate your Airtable account** to sign in with Airtable, select required workspaces you want to sync and authorize your account.
   - To authenticate using a [Personal Access Token](https://airtable.com/developers/web/guides/personal-access-tokens), select **Personal Access Token** from the Authentication dropdown and enter the Access Token for your Airtable account. The following scopes are required:
     - `data.records:read`
     - `data.recordComments:read`
     - `schema.bases:read`

:::info
When using OAuth, you may see a `400` or `401` error causing a failed sync. You can re-authenticate your Airtable connector to solve the issue temporarily. We are working on a permanent fix that you can follow [here](https://github.com/airbytehq/airbyte/issues/25278).
:::

3. Click **Set up source**.
