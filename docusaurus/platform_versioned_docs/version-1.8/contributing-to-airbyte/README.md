---
description: "We love contributions to Airbyte, big or small."
---

# Contributing to Airbyte

Thank you for your interest in contributing! Contributions are very welcome. We appreciate first time contributors and we are happy help you get started. Join our [community Slack](https://slack.airbyte.io) and feel free to reach out with questions in [`#dev-and-contribuions` channel](https://airbytehq.slack.com/archives/C054V9JFTC6).

If you're interacting in Slack, codebases, mailing lists, events, or any other Airbyte activity, you must follow the [Code of Conduct](/community/code-of-conduct). Please review it before getting started.

## Code Contributions

Most of the issues that are open for contributions are tagged with [`good first issue`](https://github.com/airbytehq/airbyte/issues?q=is%3Aopen+is%3Aissue+label%3A%22good%20first%20issue%22) or [`help-welcome`](https://github.com/airbytehq/airbyte/issues?q=is%3Aopen+is%3Aissue+label%3Ahelp-welcome).
If you are interested in an issue that isn't tagged, post a comment with your approach, and we'd be happy to assign it to you. If you submit a fix isn't linked to an issue you're assigned, there is chance Airbyte won't accept it.

### Contributions we accept

- Fixes and enhancements to existing API source connectors
- New streams and features for existing connectors using the Connector Builder/YAML
- New API source connectors built with the Connector Builder
- Migrations of an existing connector from Python to the Connector Builder/YAML

Airbyte evaluates contributions outside this scope on a case-by-case basis. Reach out to the Airbyte team before starting to ensure the team can accept your idea.

Contributions to Airbyte connectors may take some time to review, as they can affect many users. To assist us during code review, include as much information as possible in your pull request, including examples, use cases, documentation links, and more.

:::warning
Airbyte is revamping its core Java destinations codebase. We're not reviewing/accepting new Java connectors at this time.
:::

### Contributions we don't accept

- Platform contributions. In mid-2025, Airbyte stopping accepting community contributions to the Airbyte platform. Continue reporting issues through GitHub so we can investigate and prioritize fixes and improvements.

### Standard contribution workflow

1. Fork the `airbyte` repository.
2. Clone the repository locally.
3. Create a branch for your feature/bug fix with the format `{YOUR_USERNAME}/{FEATURE/BUG}` (e.g. `jdoe/source-stock-api-stream-fix`)
4. Make and commit changes.
5. Push your local branch to your fork.
6. Submit a Pull Request so that we can review your changes.
7. [Link an existing Issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue) that doesn't include the `needs triage` label to your Pull Request. Pull requests without an issue attached take longer to review.
8. Write a PR title and description that follows the [Pull Request Handbook](./resources/pull-requests-handbook.md).
9. An Airbyte maintainer will trigger the CI tests for you and review the code.
10. Review and respond to feedback and questions by Airbyte maintainers.
11. Merge the contribution.

You can check the status of your contribution in this [Github Project](https://github.com/orgs/airbytehq/projects/108/views/4). It will provide you what Sprint your contribution was assigned and when you can expect a review.

:::warning
Do not submit a pull request using the master branch from your forked repository.
The team will not be able to run integration tests and your pull request will be closed.
:::

Guidelines to common code contributions:

- [Contribute a code change to an existing connector](change-cdk-connector.md)
- [Contribute a new connector](submit-new-connector.md)

## Documentation contributions

We welcome all pull requests that clarify concepts, fix typos and grammar, and improve the structure of Airbyte's documentation. Check the [Updating Documentation](writing-docs.md) guide for details on submitting documentation changes.

For examples of good connector docs, see the [Salesforce source connector](/integrations/sources/salesforce) and [Snowflake destination connector](/integrations/destinations/snowflake) docs.

## Community Content

We welcome contributions as new tutorials / showcases / articles, or as enhancements to any of the existing guides on our tutorials page. Head to this repo dedicated to community content: [Write for the Community](https://github.com/airbytehq/write-for-the-community).

Feel free to submit a pull request in this repo, if you have something to add even if it's not related to anything mentioned above.

## Engage with the Community

Another crucial way to contribute is by reporting bugs and helping other users in the community. You're welcome to join the [Community Slack](https://slack.airbyte.io). Refer to our [Issues and Feature Requests](issues-and-requests.md) guide to learn about the best ways to report bugs.
