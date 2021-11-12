# Drupal

[Drupal](https://www.drupal.org) is an open source Content Management Platform.

## Sync overview

{% hint style="warning" %}
You will only be able to connect to a self-hosted instance of Drupal using these instructions.
{% endhint %}

Drupal can run on MySQL, Percona, MariaDb, MSSQL, MongoDB, Postgres, or SQL-Lite. If you're not using SQL-lite, you can use Airbyte to sync your Drupal instance by connecting to the underlying database using the appropriate Airbyte connector:

* [MySQL/Percona/MariaDB](mysql.md)
* [MSSQL](mssql.md)
* [Mongo]()
* [Postgres](postgres.md)

{% hint style="info" %}
Reach out to your service representative or system admin to find the parameters required to connect to the underlying database
{% endhint %}

### Output schema

The schema will be loaded according to the rules of the underlying database's connector.

