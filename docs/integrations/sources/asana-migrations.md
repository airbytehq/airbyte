# Asana Migration Guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Upgrading to 2.0.0

This release eliminates the N+1 substream design that caused sync failures, heartbeat starvation, and excessive API calls for large workspaces.

### What changed

- The `events` stream has been removed. The Asana Events API is designed for webhook-style polling with sync tokens, not bulk data extraction. The previous implementation created a request per task and per project, generating tens of thousands of 404 errors in large workspaces.
- The `sections`, `stories`, `attachments`, and `portfolios` streams now fetch data via list endpoints instead of fetching each record individually. This dramatically reduces API calls and eliminates heartbeat starvation for large workspaces.

### Who is affected

- Users syncing the `events` stream must remove it from their configured catalog.
- Users syncing the `sections`, `stories`, `attachments`, or `portfolios` streams should refresh their schemas after upgrading, as the field set returned by list endpoints may differ slightly from individual record endpoints.

### Migration steps

1. If you are syncing the `events` stream, deselect it from your configured catalog before upgrading.
2. After upgrading, refresh the schema for the `sections`, `stories`, `attachments`, and `portfolios` streams.
3. Perform a full refresh on these streams to ensure data consistency.

## Upgrading to 1.0.0

We're continuously striving to enhance the quality and reliability of our connectors at Airbyte.
As part of our commitment to delivering exceptional service, we are transitioning source Asana from the Python Connector Development Kit (CDK) to our innovative low-code framework.
This is part of a strategic move to streamline many processes across connectors, bolstering maintainability and freeing us to focus more of our efforts on improving the performance and features of our evolving platform and growing catalog.
However, due to differences between the Python and low-code CDKs, this migration constitutes a breaking change. 

This release introduces an updated data type of the `name` field in the `events` stream. You must clear this stream after upgrading.

## Connector upgrade guide

<MigrationGuide />
