# Gong Migration Guide

###  Upgrading to 1.0.0

The format of the `start_date` config parameter changed to include the time. Eg, going from "2020-01-01" to "2020-01-01T00:00:00Z".

### Summary of changes:

- The format of the `start_date` config parameter changed to include the time. Eg, going from "2020-01-01" to "2020-01-01T00:00:00Z".

### Change the configuration
Reconfigure the source, setting the `start_date` to the datetime to start syncing data.