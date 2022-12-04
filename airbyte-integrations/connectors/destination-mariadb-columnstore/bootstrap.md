# MariaDB ColumnStore

## Overview

MariaDB ColumnStore is a columnar storage engine that utilizes a massively parallel distributed data architecture.
From MariaDB 10.5.4, it is available as a storage engine for MariaDB Server.

## Endpoints

 This destination connector uses MariaDB official JDBC driver. [MariaDB Connector/J](https://mariadb.com/docs/clients/mariadb-connectors/connector-j/)

 ## Quick Notes

 - SSH Tunnel supported.
 - TLS connection not supported yet.
 - When creating ColumnStore table, we have to specify storage engine. `CREATE TABLE ... (...) ENGINE=ColumnStore;`
 - Normalization not supported yet for the following reasons:
    - [dbt-mysql](https://github.com/dbeatty10/dbt-mysql#dbt-mysql) adapter don't support MariaDB officially.
    - When using [dbt-mysql](https://github.com/dbeatty10/dbt-mysql#dbt-mysql), we cannot specify the storage engine. For that reason tables are created with system's default storage engine.(it maybe InnoDB)

## Reference

- MariaDB ColumnStore documents: [https://mariadb.com/kb/en/mariadb-columnstore/](https://mariadb.com/kb/en/mariadb-columnstore/)
- MariaDB JDBC driver (Connector/J) reference: [https://mariadb.com/docs/clients/mariadb-connectors/connector-j/](https://mariadb.com/docs/clients/mariadb-connectors/connector-j/)
