---
products: oss-community
---

# Migrating from Docker Compose

:::warning

Migration from Docker Compose is no longer supported. The `--migrate` flag has been deprecated and removed from `abctl`.

:::

If you were previously running Airbyte using Docker Compose, we recommend performing a fresh deployment of Airbyte using `abctl`. Docker Compose deployments are no longer supported.

## Fresh Deployment

To get started with a fresh Airbyte installation:

1. Install the latest version of `abctl`:

```bash
curl -LsfS https://get.airbyte.com | bash -
```

2. Run the installation:

```bash
abctl local install
```

For detailed installation instructions, see the [Quickstart guide](../using-airbyte/getting-started/oss-quickstart.md).

## Data Migration

If you need to preserve your existing connection configurations, you can manually recreate them in your new Airbyte instance. Historical sync data from your Docker Compose deployment cannot be migrated to the new installation.

For users with an external database, you can configure your new `abctl` installation to use the same database. See the [database integration documentation](integrations/database.md) for setup instructions.
