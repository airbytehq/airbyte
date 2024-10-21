# Sugar CRM

[Sugar CRM](https://www.sugarcrm.com/) is an open source eCommerce platform built on Wordpress.

## Sync overview

:::caution

You will only be able to connect to a self-hosted instance of Sugar CRM using these instructions.

:::

Sugar CRM can run on the MySQL, MSSQL, Oracle, or Db2 databases. You can use Airbyte to sync your Sugar CRM instance by connecting to the underlying database using the appropriate Airbyte connector:

- [DB2](db2.md)
- [MySQL](mysql.md)
- [MSSQL](mssql.md)
- [Oracle](oracle.md)

:::info

To use Oracle or DB2, you'll require an Enterprise or Ultimate Sugar subscription.

:::

:::info

Reach out to your service representative or system admin to find the parameters required to connect to the underlying database

:::

### Output schema

To understand your Sugar CRM database schema, see the [VarDefs](https://support.sugarcrm.com/Documentation/Sugar_Developer/Sugar_Developer_Guide_11.0/Data_Framework/Vardefs/) documentation. Otherwise, the schema will be loaded according to the rules of the underlying database's connector.
