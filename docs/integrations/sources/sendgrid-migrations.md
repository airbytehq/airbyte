# Sendgrid Migration Guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Upgrading to 1.0.0

We're continuously striving to enhance the quality and reliability of our connectors at Airbyte.

As part of our commitment to delivering exceptional service, we are transitioning Source Sendgrid from the Python Connector Development Kit (CDK)
to our new low-code framework improving maintainability and reliability of the connector. Due to differences between the Python and low-code CDKs, this migration constitutes a breaking change.

- The configuration options have been renamed to `api_key` and `start_date`.
- The `unsubscribe_groups` stream has been removed as it was a duplicate of `suppression_groups`. You can use `suppression_groups` and get the same data you were previously receiving in `unsubscribe_groups`.
- The `single_sends` stream has been renamed to `singlesend_stats`. This was done to more closely match the data from the Sendgrid API.
- The `segments` stream has been upgraded to use the Sendgrid 2.0 API as the previous version of the API has been deprecated. As a result, fields within the stream have changed to reflect the new API.

To ensure a smooth upgrade, please clear your streams and trigger a sync to bring in historical data.

## Connector upgrade guide

<MigrationGuide />
