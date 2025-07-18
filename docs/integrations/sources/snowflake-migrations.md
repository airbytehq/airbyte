# Snowflake Migration Guide

## Upgrading to 1.0.0

This version introduces Airbyte certified source connector for Snowflake to replace the community supported source connector.

**THIS VERSION INCLUDES BREAKING CHANGES FROM PREVIOUS VERSIONS OF THE CONNECTOR!**

### What to expect when upgrading:

1. No change to full refresh sync mode.
2. If you're using incremental sync mode, the incremental sync will trigger a one-time full refresh sync on the first run after upgrade because the old connection state will not be compatible with the new connector. After the full refresh the new state will be populated and the incremental sync will work as expected.

### Migration steps:
No extra actions are required to set up the new connector. The new connector configuration spec is backwards compatible with the community supported version.