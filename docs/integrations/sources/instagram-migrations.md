# Instagram Migration Guide

## Upgrading to 2.0.0

This release adds a default primary key for the streams UserLifetimeInsights and UserInsights, and updates the format of timestamp fields to include timezone information.

Users should:
- Refresh the source schema
- And reset affected streams after upgrading to ensure uninterrupted syncs.