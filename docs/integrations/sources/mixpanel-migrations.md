# Mixpanel Migration Guide

## Upgrading to 1.0.0

In this release, the datetime field of stream engage has had its type changed from date-time to string due to inconsistent data from Mixpanel. Additionally, the primary key for stream export has been fixed to uniquely identify records. Users will need to refresh the source schema and reset affected streams after upgrading.
