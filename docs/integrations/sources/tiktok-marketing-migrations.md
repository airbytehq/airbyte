import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# TikTok Marketing Migration Guide

## Upgrading to 5.5.0

:::danger Preserve existing sandbox data

Create a new connection that writes to separate destination tables or paths. Reusing sandbox tables can overwrite mock records or mix them with production records. Back up any sandbox data you need before changing its destination configuration.

:::

Version 5.5.0 removes **Sandbox Access Token** authentication. TikTok [announced that sandbox accounts will be deprecated by December 1, 2026](https://business-api.tiktok.com/portal/docs/sandbox-accounts/v1.3) and recommends using a production test account instead.

This change affects every stream in a source configured with **Sandbox Access Token** (`credentials.auth_type: sandbox_access_token`). Existing production **OAuth2.0** sources require no configuration changes, schema refresh, or data clearing. Their stream schemas, primary keys, and incremental state are unchanged.

Sandbox tokens do not authorize production advertisers. Airbyte cannot convert a sandbox account, token, or mock reporting data into production credentials or data automatically.

If you upgrade a sandbox source without migrating, its connection checks and syncs fail. Upgrading does not authorize a production account or replace the sandbox credentials. Existing destination data remains in place, but the connection cannot sync new data.

### Migration steps

If you use sandbox authentication, complete these steps before upgrading to 5.5.0 and ahead of TikTok's December 1, 2026 sandbox deprecation:

#### Step 1: Identify affected sources and connections

1. In Airbyte, open **Sources** and select your TikTok Marketing source.
2. Open its configuration and check **Authentication Method**. Follow this migration only if it is **Sandbox Access Token**. For API-managed configurations, check for `credentials.auth_type: sandbox_access_token`.
3. For each connection using that source, record the selected streams, sync modes, destination, namespace or table prefix, and schedule. Also record the source's date range, attribution window, and other report settings you want to use for production.
4. Identify any SQL queries, transformation models, dashboards, or exports that read the sandbox tables. Update these after validating the production data.

Repeat the connection steps below for every affected connection. Sources already using production **OAuth2.0** need no migration.

#### Step 2: Prepare a production advertiser

1. Sign in to TikTok Ads Manager with a user who can access the production advertiser you want to sync. Reuse an existing advertiser if you have one. Otherwise, follow TikTok's instructions to [create an Ads Manager account](https://ads.tiktok.com/help/article/create-tiktok-ads-manager-account?lang=en).
2. Record the production advertiser's **Advertiser ID** from Ads Manager. Use the advertiser account ID, not a Business Center ID or the old sandbox advertiser ID.
3. If you manage your own developer app, prepare its production **App ID**, **Secret**, and an **Access Token** authorized for that advertiser. Follow the [setup guide](tiktok-marketing.md#step-1-set-up-tiktok-marketing) for developer app setup. The token must have permission to read the data for your selected streams.

Creating or choosing a production advertiser does not transfer the sandbox's campaigns or mock reports. The new connection reads only data available in the production account.

#### Step 3: Create and authorize a new Airbyte source

Create a separate source so you can validate production access while retaining the old sandbox configuration.

For **Airbyte Cloud**:

1. Open **Sources**, select **+ New source**, and choose **TikTok Marketing**.
2. Give the source a distinct name, such as `TikTok Marketing - Production`.
3. Select **OAuth2.0** as the authentication method, then select **Authenticate your account**.
4. Sign in to TikTok with the user from step 2 and authorize access to the production advertiser. After authorization, return to Airbyte.

For **Airbyte Open Source**:

1. Open **Sources**, select **+ New source**, and choose **TikTok Marketing**.
2. Give the source a distinct name, such as `TikTok Marketing - Production`.
3. Select **OAuth2.0** and enter the production app's **App ID**, **Secret**, and **Access Token** from step 2. Do not reuse the sandbox token.

Then, for either deployment:

1. To sync only the advertiser from step 2, enter its ID in **Advertiser ID**. Leave this field empty only if you want to sync every advertiser the token can access.
2. Set **Replication Start Date** (`start_date`) to the beginning of the production history you need, in `YYYY-MM-DD` format. Do not copy a recent sandbox date unless it also matches your production requirements. The connector can read only history that TikTok makes available.
3. Leave **End Date** empty for ongoing syncs, or set it if you need a bounded historical sync.
4. Review **Attribution Window**, **Daily Reports Date Step**, and **Include Deleted Data** for your production requirements. See the [source setup guide](tiktok-marketing.md#step-2-set-up-the-source-connector-in-airbyte) for details.
5. Select **Set up source** and wait for the connection check to succeed. If it fails, correct the production credentials or advertiser access before proceeding.

#### Step 4: Create a connection with separate destination storage

1. Create a new Airbyte connection using the production source and your chosen destination. You can reuse the existing destination connector if you configure a separate location for the production records.
2. Set **Schedule Type** to **Manual** while validating the migration so a sync does not start automatically.
3. Configure a unique [destination namespace](/platform/using-airbyte/core-concepts/namespaces), such as `tiktok_production`, or a unique table prefix, such as `prod_`, as supported by your destination. For file destinations, use a separate output path. Verify that no selected stream writes to an existing sandbox table or path.
4. Review the discovered streams and select the production data you need. Production accounts expose additional streams that were unavailable in the sandbox; enable only the streams you intend to sync.
5. Set each stream's sync mode, cursor, and primary key where applicable. Use the settings recorded in step 1 as a reference, and review any additional production streams separately.
6. Save the new connection. Keep the old connection unchanged and do not copy its incremental state to the new connection. A new connection starts with fresh state and reads production history from the configured start date.

You do not need to clear or delete the old connection's destination data. Clearing it would remove sandbox records that the production account cannot restore.

#### Step 5: Run and validate the first production sync

1. Select **Sync now** on the new connection and wait for it to complete.
2. Review the sync results for each selected stream. Investigate failed streams before enabling the schedule.
3. In the destination, confirm that records appear in the new namespace, tables, or output path and that the sandbox data remains separate.
4. Compare advertiser IDs, campaign or ad names, report dates, and metrics with the same production account in TikTok Ads Manager. Production counts and values are not expected to match the sandbox's mock reports.
5. If a stream returns no records, check that the advertiser has data for that stream and date range. A successful sync against an account without campaigns or reporting history can return no records.

#### Step 6: Switch downstream consumers and retire the old connection

1. Update the SQL queries, transformation models, dashboards, and exports identified in step 1 to read the new production tables or paths. Verify their results before switching scheduled workloads. Do not combine sandbox mock metrics with production reporting metrics.
2. Set the new connection's production sync schedule.
3. Disable each old sandbox connection after validating its replacement. Keep its destination tables or files if you still need the mock data; deleting them is optional and is not part of this upgrade.

Pinning the connector to an older version does not preserve sandbox access after TikTok retires the sandbox service. If validation fails, keep the new connection on a manual schedule while you resolve the problem; do not point it at the sandbox tables as a workaround.

### Troubleshooting

| Problem | Action |
| --- | --- |
| The source connection check fails after switching authentication. | Confirm that you supplied production credentials and authorized the intended advertiser. Sandbox tokens cannot be reused with production authentication. |
| The expected advertiser is missing or inaccessible. | Check the TikTok user's advertiser permissions and the app's authorization. If you set **Advertiser ID**, use the production advertiser ID rather than a Business Center or sandbox ID. |
| A selected stream fails with a permission error. | Check that the authorized app can read that stream's data, then reauthorize and retry. A successful connection check does not verify access to every stream. |
| Report streams are empty. | Confirm that the production advertiser has reporting data within the configured date range. Sandbox mock reports are not copied to production. |

## Upgrading to 5.0.0

The `currency` field in the `pixels` stream's `events` array has been corrected from `boolean` to `string` type. The TikTok API returns currency as a string value (e.g. `"USD"`), so the previous `boolean` type was incorrect and caused transform errors during syncs.

Users syncing the `pixels` stream need to refresh the source schema and clear data for that stream after upgrading.

### Migration steps

1. Select **Connections** in the main nav bar.
   1. Select the connection(s) affected by the update.
2. Select the **Schema** tab.
   1. Select **Refresh source schema**.
   2. Select **OK** and **Save changes**.
3. Select the **Status** tab.
   1. In the **Enabled streams** list, click the three dots on the right side of the `pixels` stream and select **Clear Data**.

After the clear succeeds, trigger a sync by clicking **Sync Now**. For more information on clearing your data in Airbyte, see [this page](https://docs.airbyte.com/operator-guides/reset).

## Upgrading to 4.0.0

This version migrated source TikTok Marketing from the Python CDK to the declarative low-code CDK. Due to changes in how state is managed for incremental streams nested within a parent stream, this migration constitutes a breaking change.

The following streams are affected:

- `ad_group_audience_reports_by_country_daily`
- `ad_group_audience_reports_by_platform_daily`
- `ad_group_audience_reports_daily`
- `ad_groups`
- `ad_groups_reports_daily`
- `ad_groups_reports_hourly`
- `ads`
- `ads_audience_reports_by_country_daily`
- `ads_audience_reports_by_platform_daily`
- `ads_audience_reports_by_province_daily`
- `ads_audience_reports_daily`
- `ads_reports_daily`
- `ads_reports_hourly`
- `advertisers_audience_reports_by_country_daily`
- `advertisers_audience_reports_by_platform_daily`
- `advertisers_audience_reports_daily`
- `advertisers_reports_daily`
- `advertisers_reports_hourly`
- `campaigns`
- `campaigns_audience_reports_by_country_daily`
- `campaigns_audience_reports_by_platform_daily`
- `campaigns_audience_reports_daily`
- `campaigns_reports_daily`
- `campaigns_reports_hourly`
- `creative_assets_images`
- `creative_assets_videos`

See [Clearing data](#clearing-data) to update your connection.

The `advertiser_ids` stream schema also changed: the `advertiser_id` field type was corrected from integer to string to match the API response. Users need to refresh the stream schema.

See [Refresh schemas](#refresh-schemas) to update your connection.

### Migration steps

#### Refresh schemas

Refresh the `advertiser_ids` schema to continue syncing that stream:

1. Select **Connections** in the main navbar.
   1. Select the connection(s) affected by the update.
2. Select the **Schema** tab.
   1. Select **Refresh source schema**.
   2. Select **OK** and **Save changes**.
3. Select **Connections** in the main nav bar.
   1. Select the connection(s) affected by the update.
4. Select the **Status** tab.
   1. In the **Enabled streams** list, click the three dots on the right side of the `advertiser_ids` stream and select **Clear Data**.

Important: If you were using `advertiser_ids` without provided advertiser_id in the source configuration you should firstly refresh source schema for `advertiser_ids` stream and then clear data for affected streams from the list above.

#### Clearing data

Clear data for the affected streams listed above:

1. Select **Connections** in the main nav bar.
   1. Select the connection(s) affected by the update.
2. Select the **Status** tab.
   1. In the **Enabled streams** list, click the three dots on the right side of the impacted stream and select **Clear Data**.
3. Do the same steps from 1-2.1 for all streams in your connection that were affected by this update.

After the clear succeeds, trigger a sync by clicking **Sync Now**. For more information on clearing your data in Airbyte, see [this page](https://docs.airbyte.com/operator-guides/reset).

## Connector upgrade guide

<MigrationGuide />
