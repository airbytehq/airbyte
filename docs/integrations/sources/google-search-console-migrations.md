# Google Search Console Migration Guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Upgrading to 2.0.0

The `search_appearance` field has been appended to the existing primary keys of the following streams:

- `search_analytics_keyword_page_report`
- `search_analytics_keyword_site_report_by_page`
- `search_analytics_keyword_site_report_by_site`

Previously, these streams partitioned API requests by `search_appearance` but did not include the value in the output records or primary key. This caused silent data loss when the same combination of dimensions (e.g., date, country, device, query, page) appeared under multiple search appearance types, where one row would overwrite the other during deduplication.

With this change, `search_appearance` is now included in both the output records and the primary key, ensuring all rows are preserved.

### Action required

After upgrading to version 2.0.0, you must refresh the source schema and reset the affected streams. The new primary key is not compatible with the existing state, and a full refresh is needed for correct deduplication.

Streams not listed above are unaffected and do not require any action.

### Refresh affected schemas and reset data

1. Select **Connections** in the main navbar.
   - Select the connection affected by the update.
2. Select the **Schema** tab.
   - Select **Refresh source schema**.
   - Select **OK**.

:::note
Any detected schema changes will be listed for your review.
:::

3. Select **Save changes** at the top right of the page.
   - Ensure the **Reset affected streams** option is checked.

:::note
Depending on destination type you may not be prompted to reset your data.
:::

4. Select **Save connection**.

:::note
This will reset the data in your destination and initiate a fresh sync.
:::

For more information on resetting your data in Airbyte, see [this page](/platform/operator-guides/clear).

## Connector upgrade guide

<MigrationGuide />
