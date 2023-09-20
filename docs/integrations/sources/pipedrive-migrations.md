# Pipedrive Migration Guide

## Upgrading to 2.0.0

The verison migrates the Pipedrive connector to the low-code framework for greater maintainability. This introduces a breaking change to the state format for the `deals`, `files`, `filters`, `notes`, `activities`, `persons`, `pipelines`, `products`, `stages`, and `users` streams. 

Any connection using these streams in `incremental` mode will need to be reset after the upgrade to avoid sync failures.
