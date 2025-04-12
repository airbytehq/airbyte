# Oracle PeopleSoft

[Oracle PeopleSoft](https://www.oracle.com/applications/peoplesoft/) is a Human Resource, Financial, Supply Chain, Customer Relationship, and Enterprise Performance Management System.

Airbyte reccommends using the connector for the underlying database in your deployment of Oracle PeopleSoft to replicate data. 
Oracle PeopleSoft can be hosted on: [Oracle Database, IBM DB2, or Microsoft SQL Server](https://docs.oracle.com/cd/E92519_02/pt856pbr3/eng/pt/tgst/task_PeopleSoftDatabase-827f35.html)

## Preqrequisties

To sync data from Oracle PeopleSoft, determine where the application is hosted and verify that you can access the underlying database.

## Setup Guide

1. Determine which database your Oracle PeopleSoft instace is hosted on
2. Use the relevant setup guide to create a source for the underlying database:

- [Source Oracle (Enterprise)](https://docs.airbyte.com/integrations/enterprise-connectors/source-oracle-enterprise)
- [Source Microsoft SQL Serrver (MSSQL)](https://docs.airbyte.com/integrations/sources/mssql#microsoft-sql-server-mssql)
- [Source DB2](https://docs.airbyte.com/integrations/enterprise-connectors/source-db2)
- [Source Oracle (Marketplace)](https://docs.airbyte.com/integrations/sources/oracle)
  
