# Managing Connector Updates in Airbyte

A Guide for Administrators
As you maintain your Airbyte instance, connector updates are inevitable and essential for improved functionality and reliability. This guide helps you understand the different update types, their impact on your Airbyte environment, and the actions you may need to take in response.

## Understanding Connector Versions 
and the Changelog
Every connector in Airbyte's catalog follows semantic versioning (semver):

Major.Minor.Patch (e.g., 1.2.5)
A connector reaching version 1.0 is considered mature and comes with semver guarantees. This means:

Minor updates (1.2.x): These typically contain bug fixes and small improvements that won't affect your existing configurations.
Patch updates (1.x.x): These might introduce new features like streams or properties, but they are designed to be fully backward compatible with your existing setup.
Major updates (x.0.0): These are significant changes that may require you to adjust your configurations. We'll discuss this in more detail below.

### Reviewing the Changelog

Each connector's changelog details its update history. You can find it in the connector catalog within Airbyte's documentation.

## How Airbyte Handles Connector Updates

### Airbyte Cloud
Minor and Patch Updates: These are applied automatically and immediately to your instance. You don't need to take any action.
Major Updates: These are opt-in. You'll receive notifications about major updates and have a deadline to decide whether to apply them. If you choose not to opt-in by the deadline, any syncs using the affected connector will be paused to prevent compatibility issues.


## Airbyte Open Source (OSS) and Self-Managed Enterprise (SME)
All Updates (Major, Minor, Patch): These are opt-in via the settings page. You'll see a badge in the sidebar indicating available updates.
Minor and Patch Updates: Once you opt-in, these are applied immediately and globally to all connectors of that type in your instance.
Major Updates: These require a two-step opt-in process:
Opt-in to the update on the settings page.
Accept the update for each individual connection using the affected connector. This allows you to review and potentially adjust the connection settings before applying the update.
Syncs are Not Automatically Paused: Unlike Airbyte Cloud, syncs will not be paused if you miss the deadline for a major update. However, it's strongly recommended to update promptly to avoid potential compatibility issues.

## Actions to Take in Response to Connector Updates
Review the Changelog: Before applying any update, carefully review the changelog to understand the changes and their potential impact on your existing connections.
Test in a Staging Environment (if possible): If you have a staging environment, it's always a good practice to test connector updates there before applying them to your production instance.
Plan for Major Updates: Major updates may require you to adjust connection settings or even make changes to your data pipelines. Be sure to allocate time and resources for this.

:::info
Important Note: Airbyte provides tooling that guarantees safe connector version bumps and enforces automated version bumps for minor and patch updates.  You will always need to manually update for major version bumps.
:::