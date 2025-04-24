# MS SQL Server Migration Guide

## Upgrading to 2.0.0

This version removes the Airbyte "raw" tables introduced in version 1.0.0.  As such,
any attempt to upgrade an existing connection will fail unless a "truncate refresh" is first executed.  It is 
recommended that you should create a new connection using this upgraded destination and delete the existing
connection and generated "raw" tables in the destination after performing a successful sync via the new connection.

In addition to removing the Airbyte "raw" tables, this version also introduces a new insert mode:  bulk insert via 
Azure Blob Storage.  This mode is only supported with Microsoft SQL Server 2017 (14.x) and newer and in scenarios where
the database instance has access to Azure Cloud.  This is a net-new configuration option and may be opted in to at any point after upgrading to 
the new connection version.