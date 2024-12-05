# Oracle Siebel CRM

[Oracle Siebel CRM](https://www.oracle.com/cx/siebel/) is a Customer Relationship Management platform.

## Sync overview

Oracle Siebel CRM can run on the [Oracle, MSSQL, or IBM DB2](https://docs.oracle.com/cd/E88140_01/books/DevDep/installing-and-configuring-siebel-crm.html#PrerequisiteSoftware) databases. You can use Airbyte to sync your Oracle Siebel CRM instance by connecting to the underlying database using the appropriate Airbyte connector:

- [DB2](db2.md)
- [MSSQL](mssql.md)
- [Oracle](oracle.md)

:::info

Reach out to your service representative or system admin to find the parameters required to connect to the underlying database

:::

### Output schema

To understand your Oracle Siebel CRM database schema, see the [Organization Setup Overview docs](https://docs.oracle.com/cd/E88140_01/books/DevDep/basic-organization-setup-overview.html#basic-organization-setup-overview) documentation. Otherwise, the schema will be loaded according to the rules of the underlying database's connector.
