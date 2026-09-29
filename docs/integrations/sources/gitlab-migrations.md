import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# GitLab Migration Guide

## Upgrading to 4.0.0

This release migrates Source GitLab from the Python Connector Development Kit (CDK) to the low-code framework. The primary key changed for the following streams: `group_members`, `group_labels`, `project_members`, `project_labels`, `branches`, and `tags`.

After upgrading, refresh schemas and reset the affected streams.

<MigrationGuide />

## Upgrading to 3.0.0

This release fixes the `merge_request_commits` stream so that it returns commits for each merge request.

After upgrading, refresh the source schema and reset the `merge_request_commits` stream.

<MigrationGuide />

## Upgrading to 2.0.0

This release updates several streams to use date-time field formats as declared in the GitLab API. The affected fields are:

- `pipeline.created_at` and `pipeline.updated_at` in the Deployments stream
- `expires_at` in the Group Members and Project Members streams

After upgrading, refresh the source schema and reset the affected streams.

<MigrationGuide />

## Connector upgrade guide

<MigrationGuide />
