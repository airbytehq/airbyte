# Google Search Console Migration Guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Upgrading to 2.0.0

The `search_appearance` field has been added to the primary key of the following streams:

- `search_analytics_keyword_page_report`
- `search_analytics_keyword_site_report_by_page`
- `search_analytics_keyword_site_report_by_site`

Previously, these streams partitioned API requests by `search_appearance` but did not include the value in the output records or primary key. This caused silent data loss when the same combination of dimensions (e.g., date, country, device, query, page) appeared under multiple search appearance types — one row would overwrite the other during deduplication.

With this change, `search_appearance` is now included in both the output records and the primary key, ensuring all rows are preserved.

### Action required

After upgrading to version 2.0.0, you must perform a **full refresh** for any of the three affected streams listed above. The new primary key is not compatible with the existing state, and a full refresh is needed for correct deduplication.

Streams not listed above are unaffected and do not require any action.

## Connector upgrade guide

<MigrationGuide />
