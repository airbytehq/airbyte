# SAP Business One

[SAP Business One](https://www.sap.com/products/erp/business-one.html) is an Enterprise Resource Planning (ERP) system for small businesses.

Airbyte reccommends using the connector for the underlying database in your deployment of SAP Business One to replicate data. 
SAP Business One can be hosted on: [SAP HANA or Microsoft SQL Server](https://help.sap.com/docs/SAP_BUSINESS_ONE_PRODUCT_LINE)

## Prerequisites

To sync data from SAP Business One, determine where the application is hosted and verify that you can access the underlying database.

## Setup Guide

1. Determine which database your Oracle Siebel CRM instace is hosted on
2. Use the relevant setup guide to create a source for the underlying database:

- [Source SAP HANA (Enterprise)](https://docs.airbyte.com/integrations/enterprise-connectors/source-sap-hana)
- [Source Microsoft SQL Serrver (MSSQL)](https://docs.airbyte.com/integrations/sources/mssql#microsoft-sql-server-mssql)


