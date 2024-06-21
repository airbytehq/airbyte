## GitHub

<HideInUI>

This page contains the setup guide and reference information for the [GitHub](https://www.github.com).

</HideInUI>

## Prerequisites

- Start Date - the start date to replicate your date.

### For Airbyte Cloud:

1. [Log into Airbyte](https://cloud.airbyte.com/workspaces) account.
2. Click Sources and then click + New source.
3. On the Set up the source page, select GitHub from the Source type dropdown.
4. Enter a name for the GitHub connector.

### For Airbyte Open Source:

1. Navigate to the Airbyte dashboard.

## Supported sync modes

The source supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync):

### Tutorials

Now that you have set up the source connector, check out the following tutorials:

### Changelog

| Version | Date       | Pull Request                                             | Subject                                          |
|:--------|:-----------|:---------------------------------------------------------|:-------------------------------------------------|
| 1.5.5   | 2023-12-26 | [33783](https://github.com/airbytehq/airbyte/pull/33783) | Fix retry for 504 error in GraphQL based streams |
