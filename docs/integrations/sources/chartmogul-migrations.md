# Chartmogul Migration Guide

## Upgrading to 1.0.0

Version 1.0.0 refactors and separates the `customer_count` stream into multiple streams (daily, weekly, monthly, quarterly).

Users that have this stream enabled will need to refresh the schema and run a reset to use the new streams in affected connections to continue syncing.
