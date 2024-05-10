# Google Analytics 4 (GA4) Migration Guide

## Upgrading to 2.0.0

This version update only affects the schema of GA4 connections that sync <b>more than one property</b>.

Version 2.0.0 prevents the duplication of stream names by renaming some property streams with a new stream name that includes the property ID.

<b>If you only are syncing from one property, no changes will occur when you upgrade to the new version. </b> The stream names will continue to appear as:

- "daily_active_users",
- "weekly_active_users"

If you are syncing more than one property, any property after the first will have the property ID appended to the stream name.

For example, if your property IDs are: `0001`, `0002`, `0003`, the streams related to properties `0002` and `0003` will have the property ID appended to the end of the stream name.

- "daily_active_users",
- "daily_active_users_property_0002",
- "daily_active_users_property_0003",
- "weekly_active_users",
- "weekly_active_users_property_0002"
- "weekly_active_users_property_0003"

If you are syncing more than one property ID, you will need to reset those streams to ensure syncing continues accurately.

In the future, if you add an additional property ID, all new streams will append the property ID to the stream name without affecting existing streams. A reset is not required if you add the consecutive property after upgrading to 2.0.0.
