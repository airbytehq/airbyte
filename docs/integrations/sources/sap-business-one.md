# SAP Business One

[SAP Business One](https://www.sap.com/products/business-one.html) is an Enterprise Resource Planning \(ERP\) system.

## Sync overview

SAP Business One can run on the MSSQL or SAP HANA databases. If your instance is deployed on MSSQL, you can use Airbyte to sync your SAP Business One instance by using the [MSSQL connector](mssql.md).

:::info

Reach out to your service representative or system admin to find the parameters required to connect to the underlying database

:::

### Output schema

The schema will be loaded according to the rules of the underlying database's connector and the data available in your B1 instance.
