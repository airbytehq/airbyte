# Notion Migration Guide

## Upgrading to 2.0.0

Version 2.0.0 introduces a number of changes to the JSON schemas of all streams. These changes are being introduced to reflect updates to the Notion API. Some breaking changes have been introduced that will affect the Blocks, Databases and Pages stream.

- The type of the `rich_text` property in the Pages stream has been updated from an object to an array of `rich_text` objects
- The type of the `phone_number` property in the Pages stream has been updated from a string to an object
- The deprecated `text` property in content blocks has been renamed to `rich_text`. This change affects the Blocks, Databases and Pages streams.

A full schema refresh and data reset are required when upgrading to this version.
