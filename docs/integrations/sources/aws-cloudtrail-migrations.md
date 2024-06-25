# Aws Cloudtrail Migration Guide

## Upgrading to 1.0.0
The verison migrates the Aws Cloudtrail connector to the low-code framework for greater maintainability. 
Important update: The management_events stream changed it's EventTime field from integer to float. Destination should adapt this change if applicable.
The connector as default uses us-east-1 region for accessing streams with its custom request signer.
You may need to refresh the connection schema (with the reset), and run a sync.
The `start_date` parameter is now optional and the connector now takes current date as default start date 
Connector has a new capability of adding filters to the response attributes using the `lookup_attributes_filter` config in the spec.