# Zencart

[Zencart](https://www.zen-cart.com) is an open source online store management system built on PHP, MySQL, and HTML.

## Sync overview

Zencart runs on a MySQL database. You can use Airbyte to sync your Zencart instance by connecting to the underlying MySQL database and leveraging the [MySQL](mysql) connector.

:::info

Reach out to your service representative or system admin to find the parameters required to connect to the underlying database

:::

### Output schema

The output schema is the same as that of the [Zencart Database](https://docs.zen-cart.com/dev/schema/) described here.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.
