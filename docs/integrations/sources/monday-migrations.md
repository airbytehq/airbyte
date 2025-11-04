# Monday Migration Guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Upgrading to 2.0.0

Source Monday has deprecated API version 2023-07. We have upgraded the connector to the latest API version 2024-01. In this new version, the Id field has changed from an integer to a string in the streams Boards, Items, Tags, Teams, Updates, Users and Workspaces. Please reset affected streams.

## Connector upgrade guide

<MigrationGuide />