# Aws Cloudtrail Migration Guide

## Upgrading to 1.0.0
The verison migrates the Aws Cloudtrail connector to the low-code framework for greater maintainability. 
Important update: The management_events stream changed it's EventTime field from integer to float. Destination should adapt this change if applicable.
You may need to refresh the connection schema (with the reset), and run a sync.