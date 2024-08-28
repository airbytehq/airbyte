# Spree Commerce

[Spree Commerce](https://spreecommerce.org) is an open source eCommerce platform for global brands.

## Sync overview

Spree Commerce can run on the MySQL or Postgres databases. You can use Airbyte to sync your Spree Commerce instance by connecting to the underlying database using the appropriate Airbyte connector:

- [MySQL](mysql.md)
- [Postgres](postgres.md)

:::info

Reach out to your service representative or system admin to find the parameters required to connect to the underlying database

:::

### Output schema

The Spree Commerce schema is described in the [Spree Internals](https://dev-docs.spreecommerce.org/internals/) section of the Spree docs. Otherwise, the schema will follow the rules of the MySQL or Postgres connectors.
