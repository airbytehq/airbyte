## 👋 Greetings, Airbyte Team Member!

Here are some helpful tips and reminders for your convenience.

### Helpful Resources

- [Breaking Changes Guide](https://docs.airbyte.com/platform/connector-development/connector-breaking-changes) - Breaking changes, migration guides, and upgrade deadlines
- [Developing Connectors Locally](https://docs.airbyte.com/platform/connector-development/local-connector-development)
- [Managing Connector Secrets](https://docs.airbyte.com/platform/connector-development/local-connector-development#managing-connector-secrets)
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
- `/bump-progressive-rollout-version` - Bumps connector version with an RC suffix for progressive rollouts.
  - Creates a release candidate version (e.g., `2.16.10-rc.1`) with `enableProgressiveRollout: true`
  - Example: `/bump-progressive-rollout-version changelog="Add new feature for progressive rollout"`
- `/run-cat-tests` - Runs legacy CAT tests (Connector Acceptance Tests)
- `/run-regression-tests` - Runs regression tests for the modified connector(s).
- `/build-connector-images` - Builds and publishes a pre-release docker image for the modified connector(s).
- `/publish-connectors-prerelease` - Publishes pre-release connector builds (tagged as `{version}-preview.{git-sha}`) for all modified connectors in the PR.
- Connector release lifecycle (AI-powered):
  - `/ai-prove-fix` - Runs prerelease readiness checks, including testing against customer connections.
  - `/ai-canary-prerelease` - Rolls out prerelease to 5-10 connections for canary testing.
  - `/ai-release-watch` - Monitors rollout post-release and tracks sync success rates.
- Documentation:
  - `/ai-docs-review` - Provides AI-powered documentation recommendations for PRs with connector changes.
- JVM connectors:
  - `/update-connector-cdk-version connector=<CONNECTOR_NAME>` - Updates the specified connector to the latest CDK version.
    Example: `/update-connector-cdk-version connector=destination-bigquery`
  - `/bump-bulk-cdk-version bump=patch changelog='foo'` - Bump the Bulk CDK's version. `bump` can be major/minor/patch.
- Python connectors:
  - `/poe connector source-example lock` - Run the Poe `lock` task on the `source-example` connector, committing the results back to the branch.
  - `/poe source example lock` - Alias for `/poe connector source-example lock`.
  - `/poe source example use-cdk-branch my/branch` - Pin the `source-example` CDK reference to the branch name specified.
  - `/poe source example use-cdk-latest` - Update the `source-example` CDK dependency to the latest available version.

[📝 _Edit this welcome message._](https://github.com/airbytehq/airbyte/blob/master/.github/pr-welcome-internal.md)
