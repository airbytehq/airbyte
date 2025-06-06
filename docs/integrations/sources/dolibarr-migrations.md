# Dolibarr Migration Guide

## Upgrading to 1.0.0

### Change Summary
- This version implements the incremental sync and date_modification descendent sortfield for all parent streams, except the `company profile data` stream, as required for incremental sync for no date filter API endpoints.

### Migration Steps
1. Please update the user inputs of the connector
2. Update all the configured streams
3. Select the corresponding modification date parameter in the schema of the streams with incremental sync
4. Clean and refres your destination.
5. Update your Dolibarr installation to 21.0.0 or higher versions before sync

### Additional Notes
- This version change the sortfiled to `t.tms` that is the modification date and change sortorder to descendent for all the streams with incremental sync and their child streams.
