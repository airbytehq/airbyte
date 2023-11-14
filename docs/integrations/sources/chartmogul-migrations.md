# Chartmogul Migration Guide

## Upgrading to 1.0.0

Version 1.0.0 refactors and breaks `customer_count` stream  into multiple streams (daily, weekly, monthly, quarterly).

You need to update your schema and use the new streams.
