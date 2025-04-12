# Oracle Siebel CRM

[Oracle Siebel CRM] is a Customer Relationship Management platform.

Airbyte reccommends using the connector for the underlying database in your deployment of Oracle Siebel CRM to replicate data. 
Oracle Siebel CRM can be hosted on: [Oracle Database, IBM DB2, or Microsoft SQL Server](https://docs.oracle.com/cd/F26413_42/books/DMR/c-Overview-of-Siebel-Data-Model-afs1022619.html)

## Preqrequisties

To sync data from Oracle Siebel CRM, determine where the application is hosted and verify that you can access the underlying database.

## Setup Guide

1. Determine which database your Oracle Siebel CRM instace is hosted on
2. Use the relevant setup guide to create a source for the underlying database:

- [Source Oracle (Enterprise)](https://docs.airbyte.com/integrations/enterprise-connectors/source-oracle-enterprise)
- [Source Microsoft SQL Serrver (MSSQL)](https://docs.airbyte.com/integrations/sources/mssql#microsoft-sql-server-mssql)
- [Source DB2](https://docs.airbyte.com/integrations/enterprise-connectors/source-db2)
- [Source Oracle (Marketplace)](https://docs.airbyte.com/integrations/sources/oracle)
  

