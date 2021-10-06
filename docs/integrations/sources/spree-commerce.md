# Spree Commerce

[Spree Commerce](https://www.sugarcrm.com/) is an open source eCommerce platform built on Wordpress.

## Sync overview

Spree Commerce can run on the MySQL or Postgres databases. You can use Airbyte to sync your Spree Commerce instance by connecting to the underlying database using the appropriate Airbyte connector: 

* [MySQL](mysql.md)
* [Postgres](postgres.md)

{% hint style="info" %}
Reach out to your service representative or system admin to find the parameters required to connect to the underlying database 
{% endhint %}


### Output schema
The Spree Commerce schema is described in the [Spree Internals](https://guides.spreecommerce.org/developer/internals/) section of the Spree docs. Otherwise, the schema will follow the rules of the MySQL or Postgres connectors. 
