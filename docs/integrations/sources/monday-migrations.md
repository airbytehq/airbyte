# Mixpanel Migration Guide

## Upgrading to 2.0.0

Connector migrated to the latest API Version 2024-01. Type of Id fields was changed from integer to string for the following streams: "boards", "items", "teams", "users", "workspaces"

To ensure uninterrupted syncs, users should:
- Refresh the source schema
- Reset affected streams
