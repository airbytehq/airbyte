---
products: oss-community
---

# Migrating from Docker Compose

:::warning

Migration from Docker Compose is no longer supported. The `--migrate` flag has been deprecated and removed from `abctl`.

:::

If you were previously running Airbyte using Docker Compose, we recommend performing a fresh deployment of Airbyte. Docker Compose deployments are no longer supported.

To get started with a fresh installation, see the [Quickstart guide](../using-airbyte/getting-started/oss-quickstart.md) or the [Deploy Airbyte](deploying-airbyte.md) section for more deployment options.

If you need to preserve your existing connection configurations, you can manually recreate them in your new Airbyte instance. Historical sync data from your Docker Compose deployment cannot be migrated to the new installation.

For users with an external database, you can configure your new installation to use the same database. See the [database integration documentation](integrations/database.md) for setup instructions.
