import MigrationGuide from "@site/static/_migration_guides_upgrade_guide.md";

# Recurly Migration Guide

## Upgrading to 2.0.0

Version 2.0.0 corrects the following schemas to match the Recurly API:

| Stream                       | Field                                                              | Change                                                                                                             |
| :--------------------------- | :----------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------- |
| `subscriptions`              | `coupon_redemptions`                                               | An array of coupon redemption objects instead of a single object. The fields within each redemption are unchanged. |
| `accounts`                   | `external_accounts[].created_at`, `external_accounts[].updated_at` | Strings now declared with the `date-time` format.                                                                  |
| `account_coupon_redemptions` | `coupon.redeem_by`                                                 | String now declared with the `date-time` format.                                                                   |
| `coupons`                    | `redeem_by`                                                        | String now declared with the `date-time` format.                                                                   |
| `unique_coupons_parent`      | `created_at`, `updated_at`                                         | Strings now declared with the `date-time` format.                                                                  |

:::danger Risk of permanent data loss
Clearing a stream, or refreshing it with **Refresh and remove records**, deletes its existing destination data and re-reads only records whose `updated_at` is on or after the connector's **Start Date**. If Start Date is empty, the connector reads only the last five years, measured from the time of the re-sync, and older records are permanently removed. Before you clear or refresh-and-remove a stream, snapshot its destination table and set Start Date to a fixed date earlier than your oldest record.
:::

To migrate:

1. Upgrade the Recurly source connector to version 2.0.0.
2. Refresh the source schema for the affected streams listed above and apply the schema changes to your connections.
3. Optional: restore `coupon_redemptions` on `subscriptions` rows synced before 2.0.0. With Destinations V2, rows written using the old object schema had this field nulled, with an error recorded in `_airbyte_meta`. Refreshing the schema only fixes new rows.
   - **Incremental | Append + Deduped:** run [**Refresh stream**](https://docs.airbyte.com/platform/operator-guides/refreshes) on `subscriptions` and choose **Refresh and retain records**. The deduplicated table keeps the refreshed copy of each subscription. Subscriptions updated before the Start Date aren't re-read, so they keep their existing row with `coupon_redemptions` still null.
   - **Incremental | Append:** the only refresh available retains existing records, so each subscription appears twice: once from the old rows with `coupon_redemptions` nulled, and once from the refresh. Query only the latest `_airbyte_generation_id`, or follow the warning above and clear the stream instead.
   - **Full Refresh:** no action. Every sync rewrites all rows.
4. The `date-time` format changes don't require re-syncing history. If your destination can't change an affected column's type and syncs fail after the schema refresh, follow the warning above, then clear **only that stream** and sync it again.
5. Update downstream queries or models that treat `subscriptions.coupon_redemptions` as an object to handle an array, and check any models that rely on the affected timestamp columns being strings.

## Upgrading to 1.0.0

We recently rolled out an update to the Recurly connector using a newer version of our CDK, as well as introducing several additions to the existing stream schemas. Our aim with these updates is always to enhance the connector's functionality and provide you with a richer set of data to support your integration needs.

While our intention was to make these updates as seamless as possible, we've observed that some users are experiencing issues during the "Discover" step of the sync process. This has led us to re-categorize the recent changes as breaking updates, despite not removing fields or altering property names within the schema.

Once you have migrated to the new version, we highly recommend all users refresh their schemas and reset their data before resuming syncs

## Connector upgrade guide

<MigrationGuide />
