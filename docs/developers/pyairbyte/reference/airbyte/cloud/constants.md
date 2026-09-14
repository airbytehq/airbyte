---
id: airbyte-cloud-constants
title: airbyte.cloud.constants
---

Module airbyte.cloud.constants
==============================
Useful constants for working with Airbyte Cloud features in PyAirbyte.

Variables
---------

`FAILED_STATUSES: set[airbyte_api.models.jobstatusenum.JobStatusEnum]`
:   The set of `.JobStatusEnum` strings that indicate a sync job has failed.

`FINAL_STATUSES: set[airbyte_api.models.jobstatusenum.JobStatusEnum]`
:   The set of `.JobStatusEnum` strings that indicate a sync job has completed.

`READABLE_DESTINATION_TYPES: set[str]`
:   List of Airbyte Cloud destinations that PyAirbyte is able to read from.