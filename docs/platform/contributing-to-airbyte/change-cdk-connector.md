# Connector Updates

<!-- TODO: Rename this file to connector-updates.md after this PR is merged -->

## Breaking Changes to Connectors

Often times, changes to connectors can be made without impacting the user experience.  However, there are some changes that will require users to take action before they can continue to sync data.  These changes are considered **Breaking Changes** and require:

1. A **Major Version** increase. (Or minor in the case of a pre-1.0.0 connector in accordance with Semantic Versioning rules)
2. A [`breakingChanges` entry](https://docs.airbyte.com/connector-development/connector-metadata-file/) in the `releases` section of the `metadata.yaml` file
3. A migration guide which details steps that users should take to resolve the change
4. An Airbyte Engineer to follow the  [Connector Breaking Change Release Playbook](https://docs.google.com/document/u/0/d/1VYQggHbL_PN0dDDu7rCyzBLGRtX-R3cpwXaY8QxEgzw/edit) before merging.

### Types of Breaking Changes

A breaking change is any change that will require users to take action before they can continue to sync data. The following are examples of breaking changes:

- **Spec Change** - The configuration required by users of this connector have been changed and syncs will fail until users reconfigure or re-authenticate.  This change is not possible via a Config Migration
- **Schema Change** - The type of property previously present within a record has changed
- **Stream or Property Removal** - Data that was previously being synced is no longer going to be synced.
- **Destination Format / Normalization Change** - The way the destination writes the final data or how normalization cleans that data is changing in a way that requires a full-refresh.
- **State Changes** - The format of the source’s state has changed, and the full dataset will need to be re-synced

### Limiting the Impact of Breaking Changes

Some of the changes listed above may not impact all users of the connector. For example, a change to the schema of a specific stream only impacts users who are syncing that stream.

The breaking change metadata allows you to specify narrowed scopes that are specifically affected by a breaking change. See the [`breakingChanges` entry](https://docs.airbyte.com/connector-development/connector-metadata-file/) documentation for supported scopes.

## Migration Guide Requirements

Your migration guide must be created as a separate file at `docs/integrations/{sources|destinations}/{connector-name}-migrations.md`. The guide should be detailed and user-focused, addressing the following for each breaking change version:

- **WHAT** - What changed: Specifically, what is fixed or better for the user after this change?
- **WHY** - Why did we make this change? (API improvements, upstream deprecation, bug fixes, performance improvements)
- **WHO** - Which users are affected? Be specific about streams, sync modes, or configuration options that are impacted.
- **STEPS** - Exact steps users must take to migrate, including when to take them (before/after upgrade, before/after first sync)

Your migration guide can be as long as necessary and may include images, code snippets, SQL examples, and compatibility tables to help users understand and execute the migration.

### Examples of Good Migration Guides

Review these examples to understand the expected format and level of detail:

- [HubSpot Migration Guide](/integrations/sources/hubspot-migrations) - Clear version sections with affected stream identification
- [Google Ads Migration Guide](/integrations/sources/google-ads-migrations) - Table-based field change documentation
- [Stripe Migration Guide](/integrations/sources/stripe-migrations) - Detailed sync mode and cursor field changes
- [Snowflake Destination Migration Guide](/integrations/destinations/snowflake-migrations) - Use case-based migration paths

## Breaking Change Metadata Requirements

When adding a `breakingChanges` entry to your connector's `metadata.yaml` file, you must provide two critical fields:

### Message Field

The `message` field is a short summary shown in-app to all users of the connector. This message should:

- Be concise but informative (users should know if they're affected and what action is needed)
- Identify which users are affected (e.g., "users syncing the `campaigns` stream")
- Summarize the action required (detailed steps go in the migration guide)
- Link to the migration guide for full details

The platform uses this message to send automated emails to affected users, so clear communication is critical.

### Upgrade Deadline Field

The `upgradeDeadline` field specifies the date by which users should upgrade (format: `YYYY-MM-DD`). When setting this deadline:

- **Minimum timelines:**
  - Source connectors: At least 7 days (2 weeks recommended for simple changes)
  - Destination connectors: At least 1 month (destinations have broader impact on data pipelines)

- **Rationale:** The deadline should provide enough time for users to review the migration guide, test in staging environments, and execute the migration steps. Don't tie the deadline directly to an upstream API deprecation date—users who remain pinned to the old version won't receive future bug fixes and improvements.

- **Automated notifications:** The platform automatically emails users when a breaking change is released and sends reminders as the deadline approaches.

## Related Topics

- [Semantic Versioning for Connectors](./resources/pull-requests-handbook.md#semantic-versioning-for-connectors) - Guidelines for determining Major/Minor/Patch version changes
- [Connector Metadata File](https://docs.airbyte.com/connector-development/connector-metadata-file/) - Technical reference for `breakingChanges` metadata format
- [Pull Request Title Convention](./resources/pull-requests-handbook.md#pull-request-title-convention) - How to format PR titles (use 🚨 emoji for breaking changes)
- [QA Checks](./resources/qa-checks.md) - Automated quality checks including breaking change requirements
- [Connector Breaking Change Release Playbook](https://docs.google.com/document/u/0/d/1VYQggHbL_PN0dDDu7rCyzBLGRtX-R3cpwXaY8QxEgzw/edit) - Internal process for Airbyte Engineers (requires access)
