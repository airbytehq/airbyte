# BigQuery Migration Guide

## Upgrading to 2.0.0

Destinations V2 includes enhanced final table structures, better error handling, and other usability improvements. Learn more about what's new [here](/understanding-airbyte/typing-deduping) and how to upgrade [here](/release_notes/upgrading_to_destinations_v2). This breaking change will change the format of your final tables.

Worthy of specific mention:

- Per-record error handling
- Clearer table structure
- Removal of sub-tables for nested properties
- Removal of SCD tables
