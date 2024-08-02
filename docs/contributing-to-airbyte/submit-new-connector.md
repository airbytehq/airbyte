# Contribute a New Connector

#### Find or start a Github Discussion about the connector

Before jumping into the code please first:

1. Check to see if there is an existing [Discussion](https://github.com/airbytehq/airbyte/discussions/categories/new-connector-request) for a connector you have in mind
2. If you don't find an existing issue, [Request a New Connector](https://github.com/airbytehq/airbyte/discussions/new?category=new-connector-request)

This will enable our team to make sure your contribution does not overlap with existing works and will comply with the design orientation we are currently heading the product toward. If you do not receive an update on the issue from our team, please ping us on [Slack](https://slack.airbyte.io)!

#### Build the connector

See the [Connector Development guide](../connector-development/README.md) for more details on how to build a connector. For most API source connectors, Connector Builder is the best approach to take.

#### Open a pull request

1. Make sure your connector passes `airbyte-ci connectors test` tests. [Here's a guide on how to run them](../connector-development/testing-connectors/README.md).
2. Make sure you include the README, documentation, and an icon for your connector. Without them, one of the CI checks will fail.
3. Follow the [pull request convention](./resources/pull-requests-handbook.md#pull-request-title-convention)
4. Wait for a review from a community maintainer or our team. We generally look for the following criteria:
  - Does this PR cover authentication, pagination, and incremental syncs where applicable?
  - ‌Does the PR add reasonable list of streams?
  - If the connector uses custom Python components, did you write unit tests?
5. Provide a sandbox account. For some APIs, we'll need a sandbox account that we'll ask for. We'll then set it up in our CI and use it to test this connector in the future.
