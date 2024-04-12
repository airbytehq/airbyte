# Notion Migration Guide

## Upgrading to 3.0.0

We're continuously striving to enhance the quality and reliability of our connectors at Airbyte. As part of our commitment to delivering exceptional service, we are transitioning source Notion from the Python Connector Development Kit (CDK) to our innovative low-code framework. This is part of a strategic move to streamline many processes across connectors, bolstering maintainability and freeing us to focus more of our efforts on improving the performance and features of our evolving platform and growing catalog. However, due to differences between the Python and low-code CDKs, this migration constitutes a breaking change for users syncing data from the `Comments` stream.

We’ve evolved and standardized how state is managed for incremental streams that are nested within a parent stream. This change impacts how individual states are tracked and stored for each partition, using a more structured approach to ensure the most granular and flexible state management. To gracefully handle these changes for your existing connections, we highly recommend resetting your data for the `Comments` stream before resuming your syncs with the new version.

If you are not syncing data from the `Comments` stream, this change is non-breaking, and no further action is required.

### Refresh affected schemas and reset data

TODO: Add migration steps

## Upgrading to 2.0.0

Version 2.0.0 introduces a number of changes to the JSON schemas of all streams. These changes are being introduced to reflect updates to the Notion API. Some breaking changes have been introduced that will affect the Blocks, Databases and Pages stream.

- The type of the `rich_text` property in the Pages stream has been updated from an object to an array of `rich_text` objects
- The type of the `phone_number` property in the Pages stream has been updated from a string to an object
- The deprecated `text` property in content blocks has been renamed to `rich_text`. This change affects the Blocks, Databases and Pages streams.

A full schema refresh and data reset are required when upgrading to this version.
