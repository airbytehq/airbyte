---
description: Working with Airbyte Platform
---

# Overview

In order to facilitate faster development workflows, airbytehq/airbyte was split into two repositories on 2023-19-02:

- airbytehq/airbyte connectors and development around
- airbytehq/airbyte-platform the codebase that facilitates connectors
- airbytehq/airbyte-protocol used by both connectors and platform, the underlying protocol that airbyte uses to perform data transfers

If you have an existing pull request in airbytehq/airbyte that should instead target airbyte-platform you can use our tool mentioned below to perform the migration.

# Migrating from airbytehq/airbyte

Using our /create-platform-pr [slash command tool](https://github.com/airbytehq/airbyte/blob/master/.github/workflows/create-oss-pr-snapshot.yml) for platform. Simply comment "create-platform-pr" on your existing airbytehq/airbyte pull request and let our automation perform the migration for you. Note that if there are any conflicts between files, for the purposes of simplicity the tool will always use your version of the file in the pull request vs the version that exists in airbyte-platform.

