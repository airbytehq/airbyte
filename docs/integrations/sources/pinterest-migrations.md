import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Pinterest Migration Guide

## Upgrading to 2.0.0

We're continuously striving to enhance the quality and reliability of our connectors at Airbyte.
As part of our commitment to delivering exceptional service, we are transitioning source Pinterest from the Python Connector Development Kit (CDK) to our innovative low-code framework.
This is part of a strategic move to streamline many processes across connectors, bolstering maintainability and freeing us to focus more of our efforts on improving the performance and features of our evolving platform and growing catalog.
However, due to differences between the Python and low-code CDKs, this migration constitutes a breaking change.

We’ve evolved and standardized how state is managed for incremental streams that are nested within a parent stream.
This change impacts how individual states are tracked and stored for each partition, using a more structured approach to ensure the most granular and flexible state management.
This change will affect the following streams:

- `ad_account_analytics`
- `ad_analytics`
- `ad_group_analytics`
- `ad_groups`
- `ads`
- `campaign_analytics`
- `campaigns`

To gracefully handle these changes for your existing connections, we highly recommend resetting your data before resuming your data syncs with the new version.

## Connector upgrade guide

<MigrationGuide />

## Upgrading to 1.0.0

This release updates date-time fields with airbyte_type: timestamp_without_timezone for streams BoardPins, BoardSectionPins, Boards, Catalogs, CatalogFeeds. Additionally, the stream names AdvertizerReport and AdvertizerTargetingReport have been renamed to AdvertiserReport and AdvertiserTargetingReport, respectively.

To ensure uninterrupted syncs, users should:

- Refresh the source schema
- Reset affected streams
