# Contribute a New Connector

## API Connectors in Connector Builder

You can contribute a new low-code API Connector in Connector Builder. They're the fastest to review, and easiest for you and others to maintain!

To contribute a new connector in Connector Builder:
1. Build the connector in Connector Builder. [Read this guide to get started](../connector-development/connector-builder-ui/overview.md).
2. When you're happy with the connector, press the **Publish -> Contribute to Marketplace** button.
3. You'll be prompted for a connector description and your Github Access Token.
4. Builder will make a new pull request on your behalf automatically!
5. Airbyte Marketplace team will review the PR.

## Custom Python CDK or Java CDK connectors

### Find or start a Github Discussion about the connector

While Connector Builder is great, some [connectors won't work in the Builder just yet](../connector-development/connector-builder-ui/connector-builder-compatibility.md).
See the [Connector Development guide](../connector-development/README.md) for more details on how to build a connector. If you're building a custom Python CDK or Database (Java CDK) connector, please start with filing a discussion or an issue:

1. Check to see if there is an existing [Discussion](https://github.com/airbytehq/airbyte/discussions/categories/new-connector-request) for a connector you have in mind
2. If you don't find an existing issue, [Request a New Connector](https://github.com/airbytehq/airbyte/discussions/new?category=new-connector-request)

This will enable our team to make sure your contribution does not overlap with existing works and will comply with the design orientation we are currently heading the product toward. If you do not receive an update on the issue from our team, please ping us on [Slack](https://slack.airbyte.io)!

### Open a pull request

1. Make sure your connector passes `airbyte-ci connectors test` tests. [Here's a guide on how to run them](../connector-development/testing-connectors/README.md).
2. Make sure you include the README, documentation, and an icon for your connector. Without them, one of the CI checks will fail.
3. Follow the [pull request convention](./resources/pull-requests-handbook.md#pull-request-title-convention)
4. Wait for a review from a community maintainer or our team. We generally look for the following criteria:
  - Does this PR cover authentication, pagination, and incremental syncs where applicable?
  - ‌Does the PR add reasonable list of streams?
  - If the connector uses custom Python components, did you write unit tests?
5. Provide a sandbox account. For some APIs, we'll need a sandbox account that we'll ask for. We'll then set it up in our CI and use it to test this connector in the future.
