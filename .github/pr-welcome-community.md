## 👋 Welcome to Airbyte!

Thank you for your contribution from **{{ .repo_name }}**! We're excited to have you in the Airbyte community.

### Helpful Resources

- [PR Guidelines](https://docs.airbyte.com/contributing-to-airbyte): Check our guidelines for contributions.
- [Developing Connectors Locally](https://docs.airbyte.com/platform/connector-development/local-connector-development): Learn how to set up your environment and develop connectors locally.
- If you enable [BYO Connector Credentials](https://docs.airbyte.com/platform/connector-development/local-connector-development#managing-connector-secrets) within your fork, you can view your test results [here](https://github.com/{{ .repo_name }}/actions/workflows/run-connector-tests-command.yml):
  [![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/{{ .repo_name }}/run-connector-tests-command.yml?style=for-the-badge&label=Fork%20CI%20Status)](https://github.com/{{ .repo_name }}/actions/workflows/run-connector-tests-command.yml)

### PR Slash Commands

As needed or by request, Airbyte Maintainers can execute the following slash commands on your PR:

- `/format-fix` - Fixes most formatting issues.
- `/bump-version` - Bumps connector versions.
- `/run-connector-tests` - Runs connector tests.
- `/run-cat-tests` - Runs CAT tests.
- `/build-connector-images` - Builds and publishes a pre-release docker image for the modified connector(s).

If you have any questions, feel free to ask in the PR comments or join our [Slack community](https://airbytehq.slack.com/).

### Tips for Working with CI

1. **"Vercel" CI failures.** You can always ignore these. These are our docs builds but they can only be run by approval. A maintainer will approve the workflow upon request, but this failure should not be of concern.
2. **Pre-Release Checks.** Please pay attention to these, as they contain standard checks on the metadata.yaml file, docs requirements, etc. If you need help resolving a pre-release check, please ask a maintainer.
   - Note: If you are creating a new connector, please be sure to replace the default `logo.svg` file with a suitable icon.
3. **Connector CI Tests.** Some failures here may be expected if your tests require credentials. Please review these results to ensure (1) unit tests are passing, if applicable, and (2) integration tests pass to the degree possible and expected.
4. **(Optional.) [BYO Connector Credentials](https://docs.airbyte.com/platform/connector-development/local-connector-development#managing-connector-secrets) for tests in your fork.** You can _optionally_ set up your fork with BYO credentials for your connector. This can significantly speed up your review, ensuring your changes are fully tested before the maintainers begin their review.
