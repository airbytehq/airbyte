import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Recurly Migration Guide

## Upgrading to 2.0.0

Version 2.0.0 corrects the following schemas to match the Recurly API:

| Stream | Field | Change |
| :----- | :---- | :----- |
| `subscriptions` | `coupon_redemptions` | An array of coupon redemption objects instead of a single object. The fields within each redemption are unchanged. |
| `accounts` | `external_accounts[].created_at`, `external_accounts[].updated_at` | Strings now declared with the `date-time` format. |
| `account_coupon_redemptions` | `coupon.redeem_by` | String now declared with the `date-time` format. |
| `coupons` | `redeem_by` | String now declared with the `date-time` format. |
| `unique_coupons_parent` | `created_at`, `updated_at` | Strings now declared with the `date-time` format. |

To migrate:

1. Upgrade the Recurly source connector to version 2.0.0.
2. Refresh the source schema for the affected streams listed above and apply the schema changes to your connections.
3. Resume syncing. If your destination cannot alter an affected column's type, reset or clear **only the affected streams**, then sync them again to rebuild their data. Clearing deletes existing destination data for those streams until the sync completes; confirm that you can re-read the required history before doing so. No reset or clear is needed if your destination can apply the type changes.
4. Update downstream queries or models that treat `subscriptions.coupon_redemptions` as an object to handle an array, and check any models that rely on the affected timestamp columns being strings.

## Upgrading to 1.0.0

We recently rolled out an update to the Recurly connector using a newer version of our CDK, as well as introducing several additions to the existing stream schemas. Our aim with these updates is always to enhance the connector's functionality and provide you with a richer set of data to support your integration needs.

While our intention was to make these updates as seamless as possible, we've observed that some users are experiencing issues during the "Discover" step of the sync process. This has led us to re-categorize the recent changes as breaking updates, despite not removing fields or altering property names within the schema.

Once you have migrated to the new version, we highly recommend all users refresh their schemas and reset their data before resuming syncs

## Connector upgrade guide

<MigrationGuide />
