# Instagram Migration Guide

## Upgrading to 2.0.0

This release adds a default primary key for the streams UserLifetimeInsights and UserInsights, and updates the format of timestamp fields in the UserLifetimeInsights, UserInsights, Media and Stories streams to include timezone information.

To ensure uninterrupted syncs, users should:
- Refresh the source schema
- Reset affected streams