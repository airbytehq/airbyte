# Updating Existing Connectors

<!-- TODO: Rename this file to connector-updates.md after this PR is merged -->

## Contribution Process

Before you begin, it is a good idea check if the improvement you want to make or bug you want to fix is already captured in an [existing issue](https://github.com/airbytehq/airbyte/issues?q=is%3Aopen+is%3Aissue+label%3Aarea%2Fconnectors+-label%3Aneeds-triage+label%3Acommunity) or [pull request](https://github.com/airbytehq/airbyte/pulls).

See the [Connector Development Guide](https://docs.airbyte.com/connector-development/) for additional details on developing and testing connectors.
After coding the necessary changes, open a pull request (PR) against the default branch of the Airbyte repository. Ensure your PR adheres to the [Pull Request Title Convention](./resources/pull-requests-handbook.md#pull-request-title-convention) and includes a clear description of the changes made.

## Breaking Changes to Connectors

Whenever possible, changes to connectors should be implemented in a non-breaking way. This allows users to upgrade to the latest version of a connector without additional action required on their part. Assume that _every_ breaking changes creates friction for users and should be avoided except when absolutely necessary.

When it is not possible to make changes in a non-breaking manner, additional **breaking change requirements** include:

1. A **Major Version** increase. (Or minor in the case of a pre-1.0.0 connector in accordance with Semantic Versioning rules)
2. A [`breakingChanges` entry](https://docs.airbyte.com/connector-development/connector-metadata-file/) in the `releases` section of the `metadata.yaml` file
3. A migration guide which details steps that users should take to resolve the change
4. An Airbyte Engineer to complete the [Connector Breaking Change Release Playbook](https://docs.google.com/document/u/0/d/1VYQggHbL_PN0dDDu7rCyzBLGRtX-R3cpwXaY8QxEgzw/edit) (internal link) before merging the PR.

### Types of Breaking Changes

A breaking change is any change that requires users to take action before they can continue to sync data. The following are examples of breaking changes:

- **Spec Change** - The configuration required by users of this connector have been changed and syncs will fail until users reconfigure or re-authenticate.  This change is not possible via a Config Migration
- **Schema Change** - The type of property previously present within a record has changed
- **Stream or Property Removal** - Data that was previously being synced is no longer going to be synced.
- **Destination Format / Normalization Change** - The way the destination writes the final data or how normalization cleans that data is changing in a way that requires a full-refresh.
- **State Changes** - The format of the source’s state has changed, and the full dataset will need to be re-synced
- **Full Downstream Rewrite** - Very rarely, a change is so sigificant that it requires a full rewrite of downstream SQL transformations or BI dashboards. In these cases, consider forking the connector as a "Gen 2" version instead of making a breaking change that would fully break users' downstream pipelines.
  - Example: Migration from legacy JSON-only "raw" tables to normalized typed columns in a destination tables. These historic changes were so significant that they would break all downstream SQL transformations and BI dashboards. A "gen-2" approach in these cases gives users the ability to run both "Gen 1" and "Gen 2" in parallel, migrating only after they have had a chance to adapt their code to the new data models.

### Defining the Scope of Breaking Changes

Some legitimate breaking changes may not impact all users of the connector. For example, a change to the schema of a specific stream only impacts users who are syncing that stream.

The breaking change metadata allows you to specify narrowed scopes, and specifically _which streams_ are specifically affected by a breaking change. See the [`breakingChanges` entry](https://docs.airbyte.com/connector-development/connector-metadata-file/) documentation for supported scopes. If a user is not using the affected streams and therefor are not affected by a breaking change, they will not see any in-app messaging or emails about the change.

### Migration Guide Documentation Requirements

Your migration guide must be created as a separate file at `docs/integrations/{sources|destinations}/{connector-name}-migrations.md`. The guide should be detailed and user-focused, addressing the following for each breaking change version:

- **WHAT** - What changed: Specifically, what is fixed or better for the user after this change?
- **WHY** - Why did we make this change? (API improvements, upstream deprecation, bug fixes, performance improvements).
- **WHO** - Which users are affected? Be specific about streams, sync modes, or configuration options that are impacted.
- **STEPS** - Exact steps users must take to migrate, including when to take them (before/after upgrade, before/after first sync).

Your migration guide can be as long as necessary and may include images, code snippets, SQL examples, and compatibility tables to help users understand and execute the migration.

#### Examples of Good Migration Guides

Review these examples to understand the expected format and level of detail:

- [HubSpot Migration Guide](/integrations/sources/hubspot-migrations) - Clear version sections with affected stream identification
- [Google Ads Migration Guide](/integrations/sources/google-ads-migrations) - Table-based field change documentation
- [Stripe Migration Guide](/integrations/sources/stripe-migrations) - Detailed sync mode and cursor field changes
- [Snowflake Destination Migration Guide](/integrations/destinations/snowflake-migrations) - Use case-based migration paths

### Breaking Change Metadata Requirements

When adding a `breakingChanges` entry to your connector's `metadata.yaml` file, you must provide two critical fields:

#### Message Field

The `message` field is a short summary shown in-app to all users of the connector. This message should:

- Be concise but informative (users should know if they're affected and what action is needed).
- Identify which users are affected.
  For example: "users syncing the `campaigns` stream"
- Summarize the action required (detailed steps go in the migration guide).
- Link to the migration guide for full details.

The platform uses this message to send automated emails to affected users, so clear communication is critical.

#### Upgrade Deadline Field

The `upgradeDeadline` field specifies the date by which users should upgrade (format: `YYYY-MM-DD`). When setting this deadline:

- **Minimum timelines:**
  - Source connectors: At least 7 days (2 weeks recommended for simple changes)
  - Destination connectors: At least 1 month (destinations have broader impact on data pipelines)

- **Rationale:** The deadline should provide enough time for users to review the migration guide, test in staging environments, and execute the migration steps.

- **Exception: Immediate upstream breakage:** In the case of immediate upstream breaking changes, such as an already-removed upstream API endpoint, the deadline can be present-day or even in the past - with the rationale that users' connections are _already_ broken without the fix and therefor need the upgrade applied immediately.

- **Automated notifications:** The platform automatically emails users when a breaking change is released and sends reminders as the deadline approaches.

## Related Topics

- [Semantic Versioning for Connectors](./resources/pull-requests-handbook.md#semantic-versioning-for-connectors) - Guidelines for determining Major/Minor/Patch version changes
- [Connector Metadata File](https://docs.airbyte.com/connector-development/connector-metadata-file/) - Technical reference for `breakingChanges` metadata format
- [Pull Request Title Convention](./resources/pull-requests-handbook.md#pull-request-title-convention) - How to format PR titles (use 🚨 emoji for breaking changes)
- [QA Checks](./resources/qa-checks.md) - Automated quality checks including breaking change requirements
- [Connector Breaking Change Release Playbook](https://docs.google.com/document/u/0/d/1VYQggHbL_PN0dDDu7rCyzBLGRtX-R3cpwXaY8QxEgzw/edit) - Internal process for Airbyte Engineers (requires access)
