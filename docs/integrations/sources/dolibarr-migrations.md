# Dolibarr Migration Guide

## Breaking Changes in Version 1.0.0

### Change Summary
- [This version implements the incremental sync and date_modification descendent sortfield for all parent streams, except the `company profile data` stream, as required for incremental sync for no date filter API endpoints.].

### Migration Steps
1. [ Please reset all the configured streams and clean and refres your destination].

### Additional Notes
- [This version change the sortfiled to t.tms that is the modification date and change sortorder to descendent for all the streams with incremental sync and their child streams].
