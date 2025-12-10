# Asana Migration Guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Upgrading to 1.0.0

We're continuously striving to enhance the quality and reliability of our connectors at Airbyte.
As part of our commitment to delivering exceptional service, we are transitioning source Asana from the Python Connector Development Kit (CDK) to our innovative low-code framework.
This is part of a strategic move to streamline many processes across connectors, bolstering maintainability and freeing us to focus more of our efforts on improving the performance and features of our evolving platform and growing catalog.
However, due to differences between the Python and low-code CDKs, this migration constitutes a breaking change. 

This release introduces an updated data type of the `name` field in the `events` stream. You must clear this stream after upgrading.

## Connector upgrade guide

<MigrationGuide />
