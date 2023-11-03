# Mixpanel Migration Guide

## Upgrading to 2.0.0

In this release, the default primary key for stream Export has been deleted, allowing users to select the key that best fits their data. Refreshing the source schema and resetting affected streams is necessary only if new primary keys are to be applied following the upgrade.

## Upgrading to 1.0.0

In this release, the datetime field of stream engage has had its type changed from date-time to string due to inconsistent data from Mixpanel. Additionally, the primary key for stream export has been fixed to uniquely identify records. Users will need to refresh the source schema and reset affected streams after upgrading.
