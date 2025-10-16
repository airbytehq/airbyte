# Managing Breaking Changes in Connectors

Whenever possible, changes to connectors should be implemented in a non-breaking way. This allows users to upgrade to the latest version of a connector without additional action required on their part. Assume that _every_ breaking changes creates friction for users and should be avoided except when absolutely necessary.

When it is not possible to make changes in a non-breaking manner, additional **breaking change requirements** include:

1. A **Major Version** increase. (Or minor in the case of a pre-1.0.0 connector in accordance with Semantic Versioning rules)
2. A [`breakingChanges` entry](https://docs.airbyte.com/connector-development/connector-metadata-file/) in the `releases` section of the `metadata.yaml` file
3. A migration guide which details steps that users should take to resolve the change
4. An Airbyte Engineer to complete the [Connector Breaking Change Release Playbook](https://docs.google.com/document/u/0/d/1VYQggHbL_PN0dDDu7rCyzBLGRtX-R3cpwXaY8QxEgzw/edit) (internal link) before merging the PR.

## Types of Breaking Changes

A breaking change is any change that requires users to take action before they can continue to sync data. The following are examples of breaking changes:

- **Spec Change** - The configuration required by users of this connector have been changed and syncs will fail until users reconfigure or re-authenticate.  This change is not possible via a Config Migration
- **Schema Change** - The type of property previously present within a record has changed
- **Stream or Property Removal** - Data that was previously being synced is no longer going to be synced.
- **Destination Format / Normalization Change** - The way the destination writes the final data or how normalization cleans that data is changing in a way that requires a full-refresh.
- **State Changes** - The format of the source’s state has changed, and the full dataset will need to be re-synced
- **Full Downstream Rewrite** - Very rarely, a change is so sigificant that it requires a full rewrite of downstream SQL transformations or BI dashboards. In these cases, consider forking the connector as a "Gen 2" version instead of making a breaking change that would fully break users' downstream pipelines.
  - Example: Migration from legacy JSON-only "raw" tables to normalized typed columns in a destination tables. These historic changes were so significant that they would break all downstream SQL transformations and BI dashboards. A "gen-2" approach in these cases gives users the ability to run both "Gen 1" and "Gen 2" in parallel, migrating only after they have had a chance to adapt their code to the new data models.

### Avoiding Breaking Changes with Migrations

In some cases, breaking changes can be avoided through automated migrations:

- **Config Migrations** - For low-code connectors, config migrations can automatically transform old configurations to new formats, avoiding the need for users to manually reconfigure. See the [low-code config migration model](https://github.com/airbytehq/airbyte-python-cdk/blob/8158f0d2a07c0480d25581359d54c8f9d30dbb29/airbyte_cdk/sources/declarative/declarative_component_schema.yaml#L4021-L4045) for technical reference.
  
- **State Migrations** - For low-code connectors, state migrations can automatically transform old state formats to new formats, avoiding the need for a full refresh. See the [low-code state migration model](https://github.com/airbytehq/airbyte-python-cdk/blob/8158f0d2a07c0480d25581359d54c8f9d30dbb29/airbyte_cdk/sources/declarative/declarative_component_schema.yaml#L1579-L1587) for technical reference.

When considering spec or state changes, evaluate whether a migration can eliminate the need for a breaking change before proceeding with a major version bump.

### Schema Change Considerations: Data Type Compatibility

When changing data types in schemas, consider type compatibility to determine whether the change is truly breaking:

- **Widening that is breaking downstream:** Changes like `float` to `str` or `datetime` to `str` widen the type but may break downstream processes that expect numeric or date values.

- **Widening that is non-breaking:** Changes like `int` to `bigint` or `int` to `double` widen the type in a compatible way that preserves data semantics.

- **Non-compatible type changes:** Changes between fundamentally incompatible types (e.g., `datetime` to `float` or vice versa) are breaking and should be avoided if at all possible, as they change the semantic meaning of the data.

When in doubt, treat type changes as breaking unless you can verify that all downstream use cases will handle the new type correctly.

## Defining the Scope of Breaking Changes

Some legitimate breaking changes may not impact all users of the connector. For example, a change to the schema of a specific stream only impacts users who are syncing that stream.

The breaking change metadata allows you to specify narrowed scopes, and specifically _which streams_ are specifically affected by a breaking change. See the [`breakingChanges` entry](https://docs.airbyte.com/connector-development/connector-metadata-file/) documentation for supported scopes. If a user is not using the affected streams and therefor are not affected by a breaking change, they will not see any in-app messaging or emails about the change.

## Migration Guide Documentation Requirements

Your migration guide must be created as a separate file at `docs/integrations/{sources|destinations}/{connector-name}-migrations.md`. The guide should be detailed and user-focused, addressing the following for each breaking change version:

- **WHAT** - What changed? Specifically, what's fixed or better for the user after this change?
- **WHY** - Why did you make this change? (API improvements, upstream deprecation, bug fixes, performance improvements).
- **WHO** - Which users does this change affect? Be specific about streams, sync modes, or configuration options that are impacted.
- **STEPS** - Exact steps users must take to migrate, including when to take them (before/after upgrade, before/after first sync).

Your migration guide can be as long as necessary and may include images, code snippets, SQL examples, and compatibility tables to help users understand and execute the migration.

### Examples of Good Migration Guides

Review these examples to understand the expected format and level of detail:

- [HubSpot Migration Guide](/integrations/sources/hubspot-migrations) - Clear version sections with affected stream identification
- [Google Ads Migration Guide](/integrations/sources/google-ads-migrations) - Table-based field change documentation
- [Stripe Migration Guide](/integrations/sources/stripe-migrations) - Detailed sync mode and cursor field changes
- [Snowflake Destination Migration Guide](/integrations/destinations/snowflake-migrations) - Use case-based migration paths

### Reusable Migration Content

It's desirable for a migration guide to instruct your reader how to plan for, execute, and clean up after an upgrade. This information is applicable to most upgrades for most connectors, and you shouldn't normally need to document it. A reusable content snippet exists at `docusaurus/static/_migration_guides_upgrade_guide.md`. It contains generic upgrade information shared by every connector, and you can import it into your migration guide seamlessly.

This avoids duplicating content, increases the likelihood that documentation remains up-to-date, and makes it easier to author your migration guide. The only migration content you should author in a bespoke fashion should focus on the specifics of this connector and connector version.

#### How to use the snippet

1. Import the reusable content into your doc as a React component.

    ```js title="mydoc.md"
    import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';
    ```

2. Display it.

    ```js title="mydoc.md"
    <MigrationGuide />
    ```

#### Example usage

```md title="asana-migrations.md"
import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Asana Migration Guide

## Upgrading to 1.0.0

Here are the details of this breaking change that are specific to Asana.

## Connector upgrade guide

<MigrationGuide />
```

## Breaking Change Metadata Requirements

When adding a `breakingChanges` entry to your connector's `metadata.yaml` file, you must provide two critical fields:

### Message Field

The `message` field is a short summary shown in-app to all users of the connector. This message should:

- Be concise but informative (users should know if they're affected and what action is needed).
- Identify which users are affected.
  For example: "users syncing the `campaigns` stream"
- Summarize the action required (detailed steps go in the migration guide).
- Link to the migration guide for full details.

The platform uses this message to send automated emails to affected users, so clear communication is critical.

### Upgrade Deadline Field

The `upgradeDeadline` field specifies the date by which users should upgrade (format: `YYYY-MM-DD`). When setting this deadline:

- **Minimum timelines:**
  - Source connectors: At least 7 days (2 weeks recommended for simple changes)
  - Destination connectors: At least 1 month (destinations have broader impact on data pipelines)

- **Rationale:** The deadline should provide enough time for users to review the migration guide, test in staging environments, and execute the migration steps.

- **Exception: Immediate upstream breakage:** In the case of immediate upstream breaking changes, such as an already-removed upstream API endpoint, the deadline can be present-day or even in the past - with the rationale that users' connections are _already_ broken without the fix and therefor need the upgrade applied immediately.

- **Automated notifications:** The platform automatically emails users when a breaking change is released and sends reminders as the deadline approaches.

## Related Topics

- [Semantic Versioning for Connectors](../contributing-to-airbyte/resources/pull-requests-handbook.md#semantic-versioning-for-connectors) - Guidelines for determining Major/Minor/Patch version changes
- [Connector Metadata File](https://docs.airbyte.com/connector-development/connector-metadata-file/) - Technical reference for `breakingChanges` metadata format
- [Pull Request Title Convention](../contributing-to-airbyte/resources/pull-requests-handbook.md#pull-request-title-convention) - How to format PR titles (use 🚨 emoji for breaking changes)
- [QA Checks](../contributing-to-airbyte/resources/qa-checks.md) - Automated quality checks including breaking change requirements
- [Connector Breaking Change Release Playbook](https://docs.google.com/document/u/0/d/1VYQggHbL_PN0dDDu7rCyzBLGRtX-R3cpwXaY8QxEgzw/edit) - Internal process for Airbyte Engineers (requires access)
