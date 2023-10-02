# Google Analytics 4 (GA4) Migration Guide

## Upgrading to 2.0.0

A major update of most streams to avoid having duplicate stream names. This is relevant for the connections having more than one property ID.
Resetting a connector is needed if you have more than one property ID in your config.

Let's say you have three property IDs - `0001`, `0002`, `0003`. Two of them will be included in the stream names:
 - "daily_active_users",
 - "daily_active_users_property_0002",
 - "daily_active_users_property_0003",
 - "weekly_active_users",
 - "weekly_active_users_property_0002"
 - "weekly_active_users_property_0003"
...

If the number of properties in your config does not exceed one, you will not see changes to your stream names, and the reset is not required:
 - "daily_active_users",
 - "weekly_active_users"

Once you add the second property ID, new streams will have names with the new property ID included. Existing streams will not be affected:
 - "daily_active_users",
 - "daily_active_users_property_0002",
 - "weekly_active_users",
 - "weekly_active_users_property_0002"

If you add the second+ property after running the upgrade, the reset is not required.