# Outreach Migration Guide

## Upgrading to 2.0.0
Change the data format (column type) from array to integer for fields are relationship identifiers to other streams.
You must upgrade manually the columns to integer data type and sync the data or reset/clean and full sync the data again.

## Upgrading to 1.0.0
The version migrates the Outreach connector to the low-code framework for greater maintainability. 
Important update: The sequence_steps stream schema from API has a breaking change to the creator field to an array containing integers instead of strings.
Destination should adapt to this change if needed.
You may need to refresh the connection schema (with the reset), and run a sync.