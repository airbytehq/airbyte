## 👋 Greetings, Contributor!

Here are some helpful tips and reminders for your convenience.

### Helpful Resources

- [Developing Connectors Locally](https://docs.airbyte.com/platform/connector-development/local-connector-development)
- [Managing Connector Secrets](https://docs.airbyte.com/platform/connector-development/local-connector-development#managing-connector-secrets)
- [On-Demand Live Tests](https://github.com/airbytehq/airbyte/actions/workflows/live_tests.yml)
- [On-Demand Regression Tests](https://github.com/airbytehq/airbyte/actions/workflows/regression_tests.yml)
- [`#connector-ci-issues`](https://airbytehq-team.slack.com/archives/C05KSGM8MNC)
- [`#connector-publish-updates`](https://airbytehq-team.slack.com/archives/C056HGD1QSW)
- [`#connector-build-statuses`](https://airbytehq-team.slack.com/archives/C02TYE9QL9M)

### PR Slash Commands

Airbyte Maintainers (that's you!) can execute the following slash commands on your PR:

- `/format-fix` - Fixes most formatting issues.
- `/bump-version` - Bumps connector versions.
  - You can specify a custom changelog by passing `changelog`. Example: `/bump-version changelog="My cool update"`
  - Leaving the changelog arg blank will auto-populate the changelog from the PR title.
- `/run-cat-tests` - Runs legacy CAT tests (Connector Acceptance Tests)
- `/build-connector-images` - Builds and publishes a pre-release docker image for the modified connector(s).

[📝 _Edit this welcome message._](https://github.com/airbytehq/airbyte/blob/master/.github/pr-welcome-internal.md)
