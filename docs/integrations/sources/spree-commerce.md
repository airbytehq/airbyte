# Spree Commerce

[Spree Commerce](https://www.sugarcrm.com/) is an open source eCommerce platform built on Wordpress.

## Sync overview

Spree Commerce can run on the MySQL or Postgres databases. You can use Airbyte to sync your Spree Commerce instance by connecting to the underlying database using the appropriate Airbyte connector: 

* [MySQL](mysql.md)
* [Postgres](postgres.md)

### Output schema
The Spree Commerce schema is described in the [Spree Internals](https://guides.spreecommerce.org/developer/internals/) section of the Spree docs. Otherwise, the schema will follow the rules of the MySQL or Postgres connectors. 
