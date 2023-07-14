---
description: 'We love contributions to Airbyte, big or small.'
---

# Contributing to Airbyte

Thank you for your interest in contributing! We love community contributions. 
Read on to learn how to contribute to Airbyte.
We appreciate first time contributors and we are happy to assist you in getting started. In case of questions, just reach out to us via [email](mailto:hey@airbyte.io) or [Slack](https://slack.airbyte.io)!

Before getting started, please review Airbyte's Code of Conduct. Everyone interacting in Slack, codebases, mailing lists, events, or other Airbyte activities is expected to follow [Code of Conduct](../project-overview/code-of-conduct.md).

## Code Contributions

Most of the issues that are open for contributions are tagged with `good first issue` or `help-welcome`. 
A great place to start looking will be our GitHub projects for:

[**Community Connector Issues Project**](https://github.com/orgs/airbytehq/projects/50)

Due to project priorities, we may not be able to accept all contributions at this time. 
We are prioritizing the following contributions: 
* Bug fixes, features, and enhancements to existing API source connectors
* New connector sources and destinations built with the Python CDK, with a preference for low and no-code CDK, as these connectors are easier to maintain
* Bug fixes, features, and enhancements to the following database sources: MongoDB, Postgres, MySQL, MSSQL
* Bug fixes to the following destinations: BigQuery, Snowflake, Redshift, S3, and Postgres
* Helm Charts features, bug fixes, and other platform bug fixes


:::warning
Contributions outside of these will be evaluated on a case-by-case basis by our engineering team.
:::

The usual workflow of code contribution is:
1. Fork the Airbyte repository
2. Clone the repository locally
3. Make changes and commit them
4. Push your local branch to your fork
5. Submit a Pull Request so that we can review your changes
6. [Link an existing Issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue) without `needs triage` label to your Pull Request (PR without this will be closed)
7. Write a commit message
8. An Airbyte maintainer will trigger the CI tests for you and review the code
9. Update the comments and review
10. Merge the contribution

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

- Check the [guidelines](writing-docs.md) to submit documentation changes

## Community Content

We welcome contributions as new tutorials / showcases / articles, or to any of the existing guides on our tutorials page.

We have a repo dedicated to community content. Everything is documented [there](https://github.com/airbytehq/community-content/).

Feel free to submit a pull request in this repo, if you have something to add even if it's not related to anything mentioned above.

## Engage with the Community

Another crucial way to contribute is by reporting bugs and helping other users in the community.

You're welcome to enter the Community Slack and help other users or report bugs in Github.

- How to report a bug [guideline](issues-and-requests.md)
