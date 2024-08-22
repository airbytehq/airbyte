---
description: "We love contributions to Airbyte, big or small."
---

# Contributing to Airbyte

Thank you for your interest in contributing! Contributions are very welcome.
We appreciate first time contributors and we are happy help you get started. Join our [community Slack](https://slack.airbyte.io) and feel free to reach out with questions!

Everyone interacting in Slack, codebases, mailing lists, events, or any other Airbyte activities is expected to follow the [Code of Conduct](../community/code-of-conduct.md). Please review it before getting started.

## Code Contributions

Most of the issues that are open for contributions are tagged with [`good first issue`]( https://github.com/airbytehq/airbyte/issues?q=is%3Aopen+is%3Aissue+label%3A%22good%20first%20issue%22 ) or [`help-welcome`](https://github.com/airbytehq/airbyte/issues?q=is%3Aopen+is%3Aissue+label%3Ahelp-welcome).
If you see an issue that isn't tagged that you're interested in, post a comment with your approach, and we'd be happy to assign it to you.


#### Here are the areas that we love seeing contributions to:

- Bug fixes, features, and enhancements to existing API source connectors.
- New API sources built with the low-code CDK or Connector Builder.
- Migrating existing sources from Python to the low-code CDK.
- Bug fixes, features, and enhancements to the following database sources: Postgres, MySQL, MSSQL.
- Bug fixes to the following destinations: BigQuery, Snowflake, Redshift, S3, and Postgres.
- Helm Charts features, bug fixes, and other platform bug fixes.

:::warning
Airbyte is undergoing a major revamp of the shared core Java destinations codebase, with plans to release a new CDK in 2024.
We are actively working on improving usability, speed (through asynchronous loading), and implementing [Typing and Deduplication](/using-airbyte/core-concepts/typing-deduping) (Destinations V2).
We're not actively reviewing/accepting new Java connectors for now.
:::

#### The usual workflow of code contribution is:

1. Fork the Airbyte repository.
2. Clone the repository locally.
3. Create a branch for your feature/bug fix with the format `{YOUR_USERNAME}/{FEATURE/BUG}` (e.g. `jdoe/source-stock-api-stream-fix`)
4. Make and commit changes.
5. Push your local branch to your fork.
6. Submit a Pull Request so that we can review your changes.
7. [Link an existing Issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue) that does not include the `needs triage` label to your Pull Request. Pull requests without an issue attached take longer to review.
8. Write a PR title and description that follows the [Pull Request Handbook](./resources/pull-requests-handbook.md).
9. An Airbyte maintainer will trigger the CI tests for you and review the code.
10. Review and respond to feedback and questions by Airbyte maintainers.
11. Merge the contribution.

Guidelines to common code contributions:

- [Contribute a code change to an existing connector](change-cdk-connector.md)
- [Contribute a new connector](submit-new-connector.md)

## Documentation

We welcome pull requests that fix typos or enhance the grammar and structure of our documentation! Check the [Updating Documentation](writing-docs.md) guide for details on submitting documentation changes.


The following highlights from the [Google developer documentation style guide](https://developers.google.com/style) are helpful for new writers:

- [Be conversational and friendly without being frivolous](https://developers.google.com/style/tone)
- [Use second person](https://developers.google.com/style/person)
- [Use active voice](https://developers.google.com/style/voice)
- [Put conditional clauses before instructions](https://developers.google.com/style/clause-order)
- [Put UI elements in bold](https://developers.google.com/style/ui-elements)
- [Write inclusive documentation](https://developers.google.com/style/inclusive-documentation)
- [Don't pre-announce anything in documentation](https://developers.google.com/style/future)

Guideline for visuals: Use links to videos instead of screenshots (Reason: Users are more forgiving of outdated videos than screenshots).

For examples of good connector docs, see the [Salesforce source connector doc](https://docs.airbyte.com/integrations/sources/salesforce) and [Snowflake destination connector doc](https://docs.airbyte.com/integrations/destinations/snowflake)

## Community Content

We welcome contributions as new tutorials / showcases / articles, or as enhancements to any of the existing guides on our tutorials page. Head to this repo dedicated to community content: [Write for the Community](https://github.com/airbytehq/write-for-the-community).

Feel free to submit a pull request in this repo, if you have something to add even if it's not related to anything mentioned above.

## Engage with the Community

Another crucial way to contribute is by reporting bugs and helping other users in the community. You're welcome to join the [Community Slack](https://slack.airbyte.io). Refer to our [Issues and Feature Requests](issues-and-requests.md) guide to learn about the best ways to report bugs.
