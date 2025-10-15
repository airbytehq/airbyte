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

## Related Topics

- [Semantic Versioning for Connectors](./resources/pull-requests-handbook.md#semantic-versioning-for-connectors) - Guidelines for determining Major/Minor/Patch version changes
- [Connector Metadata File](https://docs.airbyte.com/connector-development/connector-metadata-file/) - Technical reference for `breakingChanges` metadata format
- [Pull Request Title Convention](./resources/pull-requests-handbook.md#pull-request-title-convention) - How to format PR titles (use 🚨 emoji for breaking changes)
- [QA Checks](./resources/qa-checks.md) - Automated quality checks including breaking change requirements
- [Connector Breaking Change Release Playbook](https://docs.google.com/document/u/0/d/1VYQggHbL_PN0dDDu7rCyzBLGRtX-R3cpwXaY8QxEgzw/edit) - Internal process for Airbyte Engineers (requires access)
