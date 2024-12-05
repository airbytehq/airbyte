# Trello Migration Guide

## Upgrading to 1.0.0

This version upgrades the connector to the low-code framework for better maintainability. This migration includes a breaking change to the state format of the `actions` stream.

Any connection using the `actions` stream in `incremental` mode will need to be reset after the upgrade to avoid sync failures.
