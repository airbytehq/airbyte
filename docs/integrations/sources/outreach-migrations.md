# Outreach Migration Guide

## Upgrading to 1.0.0
The verison migrates the Outreach connector to the low-code framework for greater maintainability. 
Important update: The sequence_steps stream schema from API has a breaking change to the creator field to an array containing integers instead of strings.
Destination should adapt to this change if needed.
You may need to refresh the connection schema (with the reset), and run a sync.