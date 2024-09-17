# Oracle Peoplesoft

[Oracle PeopleSoft](https://www.oracle.com/applications/peoplesoft/) is a Human Resource, Financial, Supply Chain, Customer Relationship, and Enterprise Performance Management System.

## Sync overview

Oracle PeopleSoft can run on the [Oracle, MSSQL, or IBM DB2](https://docs.oracle.com/en/applications/peoplesoft/peopletools/index.html) databases. You can use Airbyte to sync your Oracle PeopleSoft instance by connecting to the underlying database using the appropriate Airbyte connector:

- [DB2](db2.md)
- [MSSQL](mssql.md)
- [Oracle](oracle.md)

:::info

Reach out to your service representative or system admin to find the parameters required to connect to the underlying database

:::

### Output schema

The schema will be loaded according to the rules of the underlying database's connector. Oracle provides ERD diagrams but they are behind a paywall. Contact your Oracle rep to gain access.
