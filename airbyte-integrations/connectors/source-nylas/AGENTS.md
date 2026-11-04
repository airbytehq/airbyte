## HTTP error handling

The events requester ignores HTTP 404 responses per calendar partition so other calendars can continue syncing.
The CDK logs the configured error message at INFO; events from a skipped calendar are not emitted.
