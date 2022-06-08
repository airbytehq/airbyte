# airbyte-scheduler:scheduler-persistence

This module encapsulates the logic for the Jobs Database. This Database is primarily used by the `airbyte-scheduler` and `airbyte-workers` but it is also access from the `airbyte-server`.

## Key Files
* `DefaultJobPersistence` is where all queries for interacting with the Jobs Database live.
* everything else is abstraction on top of that to make it easier to create / interact with / test jobs.
