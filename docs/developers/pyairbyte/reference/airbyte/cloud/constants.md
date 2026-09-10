---
id: airbyte-cloud-constants
title: "airbyte.cloud.constants Module"
sidebar_label: "airbyte.cloud.constants"
toc_max_heading_level: 5
---

# `airbyte.cloud.constants` Module

Useful constants for working with Airbyte Cloud features in PyAirbyte.

- **`FAILED_STATUSES`**&nbsp;(`set[airbyte.cloud.models.JobStatusEnum]`)

  The set of `.JobStatusEnum` strings that indicate a sync job has failed.

- **`FINAL_STATUSES`**&nbsp;(`set[airbyte.cloud.models.JobStatusEnum]`)

  The set of `.JobStatusEnum` strings that indicate a sync job has completed.

- **`READABLE_DESTINATION_TYPES`**&nbsp;(`set[str]`)

  List of Airbyte Cloud destinations that PyAirbyte is able to read from.