# Changes to Python CDK or Low-Code Connector

## Contribution Process

### Open an issue, or find a similar one.

Before jumping into the code please first:

1. Check if the improvement you want to make or bug you want to fix is already captured in an [existing issue](https://github.com/airbytehq/airbyte/issues?q=is%3Aopen+is%3Aissue+label%3Aarea%2Fconnectors+-label%3Aneeds-triage+label%3Acommunity)
2. If you don't find an existing issue, either

- [Report a Connector Bug](https://github.com/airbytehq/airbyte/issues/new?assignees=&labels=type%2Fbug%2Carea%2Fconnectors%2Cneeds-triage&projects=&template=1-issue-connector.yaml), or
- [Request a New Connector Feature](https://github.com/airbytehq/airbyte/issues/new?assignees=&labels=type%2Fenhancement%2Cneeds-triage&projects=&template=6-feature-request.yaml)

This will enable our team to make sure your contribution does not overlap with existing works and will comply with the design orientation we are currently heading the product toward. If you do not receive an update on the issue from our team, please ping us on [Slack](https://slack.airbyte.io)!

:::info
Make sure you're working on an issue had been already triaged to not have your contribution declined.
:::

### Code your contribution

1. To contribute to a connector, fork the [Connector repository](https://github.com/airbytehq/airbyte).
2. Open a branch for your work
3. Code the change
4. Write a unit test for each custom function you added or changed
5. Ensure all tests, including connector acceptance tests, pass
6. Update the `metadata.yaml` following the [guidelines](./resources/pull-requests-handbook.md#semantic-versioning-for-connectors)
7. Update the changelog entry in documentation in `docs/integrations/<connector-name>.md`
8. Make sure your contribution passes our [QA checks](./resources/qa-checks.md)

:::info
There is a README file inside each connector folder containing instructions to run that connector's tests locally.
:::

:::warning
Pay attention to breaking changes to connectors. You can read more [here](#breaking-changes-to-connectors).
:::

### Open a pull request

1. Rebase master with your branch before submitting a pull request.
2. Open the pull request.
3. Follow the [title convention](./resources/pull-requests-handbook.md#pull-request-title-convention) for Pull Requests
4. Link to an existing Issue
5. Update the [description](./resources/pull-requests-handbook.md#descriptions)
6. Wait for a review from a community maintainer or our team.

### Review process

When we review, we look at:

- ‌Does the PR solve the issue?
- Is the proposed solution reasonable?
- Is it tested? \(unit tests or integration tests\)
- Is it introducing security risks?
- Is it introducing a breaking change?
  ‌Once your PR passes, we will merge it 🎉.

## Breaking Changes to Connectors

Often times, changes to connectors can be made without impacting the user experience.  However, there are some changes that will require users to take action before they can continue to sync data.  These changes are considered **Breaking Changes** and require:

1. A **Major Version** increase
2. A [`breakingChanges` entry](https://docs.airbyte.com/connector-development/connector-metadata-file/) in the `releases` section of the `metadata.yaml` file
3. A migration guide which details steps that users should take to resolve the change
4. An Airbyte Engineer to follow the  [Connector Breaking Change Release Playbook](https://docs.google.com/document/u/0/d/1VYQggHbL_PN0dDDu7rCyzBLGRtX-R3cpwXaY8QxEgzw/edit) before merging.

### Types of Breaking Changes

A breaking change is any change that will require users to take action before they can continue to sync data. The following are examples of breaking changes:

- **Spec Change** - The configuration required by users of this connector have been changed and syncs will fail until users reconfigure or re-authenticate.  This change is not possible via a Config Migration
- **Schema Change** - The type of property previously present within a record has changed
- **Stream or Property Removal** - Data that was previously being synced is no longer going to be synced.
- **Destination Format / Normalization Change** - The way the destination writes the final data or how normalization cleans that data is changing in a way that requires a full-refresh.
- **State Changes** - The format of the source’s state has changed, and the full dataset will need to be re-synced

### Limiting the Impact of Breaking Changes

Some of the changes listed above may not impact all users of the connector. For example, a change to the schema of a specific stream only impacts users who are syncing that stream.

The breaking change metadata allows you to specify narrowed scopes that are specifically affected by a breaking change. See the [`breakingChanges` entry](https://docs.airbyte.com/connector-development/connector-metadata-file/) documentation for supported scopes.
