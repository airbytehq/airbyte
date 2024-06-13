---
description: "We love contributions to Airbyte, big or small."
---

# Contributing to Airbyte

Thank you for your interest in contributing! We love community contributions.
Read on to learn how to contribute to Airbyte.
We appreciate first time contributors and we are happy to assist you in getting started. In case of questions, just reach out to us via email: [hey@airbyte.io](mailto:hey@airbyte.io) or [Slack](https://slack.airbyte.io)!

Before getting started, please review Airbyte's Code of Conduct. Everyone interacting in Slack, codebases, mailing lists, events, or other Airbyte activities is expected to follow [Code of Conduct](../community/code-of-conduct.md).

## Code Contributions

Most of the issues that are open for contributions are tagged with [`good-first-issue`](https://github.com/airbytehq/airbyte/issues?q=is%3Aopen+is%3Aissue+label%3Agood-first-issue) or [`help-welcome`](https://github.com/airbytehq/airbyte/labels/help-welcome).
A great place to start looking will be our GitHub projects for [**Community Connector Issues**](https://github.com/orgs/airbytehq/projects/50)

Contributions for new connectors should come with documentation. Refer to the [guidelines on updateing documentation](writing-docs.md) which include a template to use while documentiong a new connector. 

Proposed updates to a connector should include updates to the connector's documentation. 

Due to project priorities, we may not be able to accept all contributions at this time.
We are prioritizing the following contributions:

- Bug fixes, features, and enhancements to existing API source connectors.
- Migrating Python CDK to Low-code or No-Code Framework.
- New connector sources built with the Low-Code CDK or Connector Builder, as these connectors are easier to maintain.
- Bug fixes, features, and enhancements to the following database sources: Postgres, MySQL, MSSQL.
- Bug fixes to the following destinations: BigQuery, Snowflake, Redshift, S3, and Postgres.
- Helm Charts features, bug fixes, and other platform bug fixes.

:::warning
Airbyte is undergoing a major revamp of the shared core Java destinations codebase, with plans to release a new CDK in 2024.
We are actively working on improving usability, speed (through asynchronous loading), and implementing [Typing and Deduplication](/using-airbyte/core-concepts/typing-deduping) (Destinations V2).
For this reason, Airbyte is not reviewing/accepting new Java connectors for now.
:::

:::warning
Contributions outside of these will be evaluated on a case-by-case basis by our engineering team.
:::

The usual workflow of code contribution is:

1. Fork the Airbyte repository.
2. Clone the repository locally.
3. Create a branch for your feature/bug fix with the format `{YOUR_USERNAME}/{FEATURE/BUG}` (e.g. `jdoe/source-stock-api-stream-fix`)
4. Make and commit changes.
5. Push your local branch to your fork.
6. Submit a Pull Request so that we can review your changes.
7. [Link an existing Issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue) that does not include the `needs triage` label to your Pull Request. A pull request without a linked issue will be closed, otherwise.
8. Write a PR title and description that follows the [Pull Request Handbook](./resources/pull-requests-handbook.md).
9. An Airbyte maintainer will trigger the CI tests for you and review the code.
10. Review and respond to feedback and questions by Airbyte maintainers.
11. Merge the contribution.

Pull Request reviews are done on a regular basis.

:::info
Please make sure you respond to our feedback/questions and sign our CLA.

Pull Requests without updates will be closed due inactivity.
:::

Guidelines to common code contributions:

- [Submit code change to existing Source Connector](change-cdk-connector.md)
- [Submit a New Connector](submit-new-connector.md)

## Documentation

We welcome Pull Requests that enhance the grammar, structure, or fix typos in our documentation.

- Check the [Updating Documentation](writing-docs.md) guide for submitting documentation changes.

- Refer to this [template](https://hackmd.io/Bz75cgATSbm7DjrAqgl4rw) if you're submitting a new connector to the cataolg.

## Community Content

We welcome contributions as new tutorials / showcases / articles, or to any of the existing guides on our tutorials page.

We have a repo dedicated to community content: [Write for the Community](https://github.com/airbytehq/write-for-the-community).

Feel free to submit a pull request in this repo, if you have something to add even if it's not related to anything mentioned above.

## Engage with the Community

Another crucial way to contribute is by reporting bugs and helping other users in the community.

You're welcome to enter the [Community Slack](https://slack.airbyte.io) and help other users or report bugs in Github.

- Refer to the [Issues and Requests](issues-and-requests.md) guide to learn about reporting bugs.
