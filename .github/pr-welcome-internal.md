## 👋 Greetings, Airbyte Team Member!

Here are some helpful tips and reminders for your convenience.

<details>
<summary><b>💡 Show Tips and Tricks</b></summary>

### PR Slash Commands

Airbyte Maintainers (that's you!) can execute the following slash commands on your PR:

- 🛠️ Quick Fixes
  - `/format-fix` - Fixes most formatting issues.
  - `/bump-version` - Bumps connector versions, scraping `changelog` description from the PR title.
- ❇️ AI Testing and Review:
  - `/ai-docs-review` - Provides AI-powered documentation recommendations for PRs with connector changes.
  - `/ai-prove-fix` - Runs prerelease readiness checks, including testing against customer connections.
  - `/ai-canary-prerelease` - Rolls out prerelease to 5-10 connections for canary testing.
  - `/ai-review` - AI-powered PR review for connector safety and quality gates.
- 🚀 Connector Releases:
  - `/publish-connectors-prerelease` - Publishes pre-release connector builds (tagged as `{version}-preview.{git-sha}`) for all modified connectors in the PR.
  - `/bump-progressive-rollout-version` - Bumps connector version with an RC suffix (`2.16.10-rc.1`) for progressive rollouts (`enableProgressiveRollout: true`).
    - Example: `/bump-progressive-rollout-version changelog="Add new feature for progressive rollout"`
- ☕️ JVM connectors:
  - `/update-connector-cdk-version connector=<CONNECTOR_NAME>` - Updates the specified connector to the latest CDK version.
    Example: `/update-connector-cdk-version connector=destination-bigquery`
  - `/bump-bulk-cdk-version bump=patch changelog='foo'` - Bump the Bulk CDK's version. `bump` can be major/minor/patch.
- 🐍 Python connectors:
  - `/poe connector source-example lock` - Run the Poe `lock` task on the `source-example` connector, committing the results back to the branch.
  - `/poe source example lock` - Alias for `/poe connector source-example lock`.
  - `/poe source example use-cdk-branch my/branch` - Pin the `source-example` CDK reference to the branch name specified.
  - `/poe source example use-cdk-latest` - Update the `source-example` CDK dependency to the latest available version.
- ⚙️ Admin commands:
  - `/force-merge reason="<REASON>"` - Force merges the PR using admin privileges, bypassing CI checks. Requires a reason.
    Example: `/force-merge reason="CI is flaky, tests pass locally"`

</details>

<details>
<summary><b>📚 Show Repo Guidance</b></summary>

### Helpful Resources

- [Breaking Changes Guide](https://docs.airbyte.com/platform/connector-development/connector-breaking-changes) - Breaking changes, migration guides, and upgrade deadlines
- [Developing Connectors Locally](https://docs.airbyte.com/platform/connector-development/local-connector-development)
- [Managing Connector Secrets](https://docs.airbyte.com/platform/connector-development/local-connector-development#managing-connector-secrets)
- [On-Demand Regression Tests](https://github.com/airbytehq/airbyte/actions/workflows/regression_tests.yml)
- [`#connector-ci-issues`](https://airbytehq-team.slack.com/archives/C05KSGM8MNC)
- [`#connector-publish-updates`](https://airbytehq-team.slack.com/archives/C056HGD1QSW)
- [`#connector-build-statuses`](https://airbytehq-team.slack.com/archives/C02TYE9QL9M)

[📝 _Edit this welcome message._](https://github.com/airbytehq/airbyte/blob/master/.github/pr-welcome-internal.md)

</details>
