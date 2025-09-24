import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Gitlab Migration Guide

## Upgrading to 4.0.0

We're continuously striving to enhance the quality and reliability of our connectors at Airbyte.
As part of our commitment to delivering exceptional service, we are transitioning Source Gitlab from the Python Connector Development Kit (CDK)
to our new low-code framework improving maintainability and reliability of the connector.
However, due to differences between the Python and low-code CDKs, this migration constitutes a breaking change.

The primary key was changed for streams `group_members`, `group_labels`, `project_members`, `project_labels`, `branches`, and `tags`.
Users will need to reset the affected streams after upgrading.

<MigrationGuide />

## Upgrading to 3.0.0

In this release, `merge_request_commits` stream schema has been fixed so that it returns commits for each merge_request.
Users will need to refresh the source schema and reset `merge_request_commits` stream after upgrading.

<MigrationGuide />

## Connector upgrade guide

<MigrationGuide />

## Upgrading to 2.0.0

In the 2.0.0 config change, several streams were updated to date-time field format, as declared in the Gitlab API.
These changes impact `pipeline.created_at` and` pipeline.updated_at` fields for stream Deployments and `expires_at` field for stream Group Members and stream Project Members.
You will need to refresh the source schema and reset affected streams after upgrading.
