import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# OpenAI Ads Migration Guide

## Upgrading to 1.0.0

:::danger Risk of permanent data loss
If you clear this stream in Full Refresh | Append, earlier snapshots are deleted and cannot be fetched again. Do not clear the stream unless you no longer need that history.
:::

:::note
This change is only breaking if you are syncing the `spend_limit_windows` stream.
:::

The `start_date` and `end_date` fields of the `spend_limit_windows` stream are now declared with `format: date`, because the [OpenAI Ads API](https://developers.openai.com/ads/api-reference/ad-account) returns them as `YYYY-MM-DD` dates. Destinations that support a date type now store these columns as dates instead of strings.

### Migration steps

#### Refresh the source schema

1. Select **Connections** in the main nav bar, then select the connection that syncs `spend_limit_windows`.
2. Select the **Schema** tab.
3. Select **Refresh source schema**, then select **OK**.
4. Review the detected schema changes, then select **Save changes**.

#### Decide whether to clear the stream

Clearing `spend_limit_windows` is optional. The stream only supports full refresh:

- **Full Refresh | Overwrite:** the next sync rebuilds the table with the new types, so clearing gains nothing.
- **Full Refresh | Append:** clearing deletes every earlier snapshot. Spend limit windows deleted in OpenAI since those snapshots can't be fetched again, so don't clear unless you no longer need that history.

If Airbyte offers to clear affected streams when you save, leave the option unchecked unless you want to clear. For more information, see [Clearing your data](/platform/operator-guides/clear).

#### Check downstream queries

`start_date` and `end_date` now arrive as dates in destinations that support a date type. Update SQL, models and dashboards that compare, cast or format these columns as text.

## Connector upgrade guide

<MigrationGuide />
