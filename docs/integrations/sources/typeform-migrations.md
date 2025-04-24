# Typeform Migration Guide

## Upgrading to 1.1.0

This version upgrades the connector to the low-code framework for better maintainability. This migration includes a breaking change to the state format of the `responses` stream.

Any connection using the `responses` stream in `incremental` mode will need to be reset after the upgrade to avoid sync failures.
