# Oracle Source
The Oracle source connector allows syncing the data from the Oracle DB. The current source connector supports Oracle 11g or above.
The connector uses *ojdbc8* driver underneath to establish the connection. The Oracle source does not alter the schema present in your database.

### Important details
Connector works with `useFetchSizeWithLongColumn=true` property, which required to select the data from `LONG` or `LONG RAW` type columns.
Oracle recommends avoiding LONG and LONG RAW columns. Use LOB instead. They are included in Oracle only for legacy reasons.
THIS IS A THIN ONLY PROPERTY. IT SHOULD NOT BE USED WITH ANY OTHER DRIVERS.

See [this](https://docs.airbyte.io/integrations/sources/oracle) link for the nuances about the connector.