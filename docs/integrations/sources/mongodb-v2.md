# Mongo DB

The MongoDB source allows to sync data from MongoDb. Source supports Full Refresh and Incremental sync strategies.

## Resulting schema

MongoDB does not have anything like table definition, thus we have to define column types from actual attributes and their values. Discover phase have two steps:

### Step 1. Find all unique properties

Connector select 10k documents to collect all distinct field.

### Step 2. Determine property types

For each property found, connector determines its type, if all the selected values have the same type - connector will set appropriate type to the property. In all other cases connector will fallback to `string` type.

## Features

| Feature | Supported |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| Replicate Incremental Deletes | No |
| Namespaces | No |

### Full Refresh sync

Works as usual full refresh sync.

### Incremental sync

Cursor field can not be nested. Currently only top level document properties are supported.

Cursor should **never** be blank. In case cursor is blank - the incremental sync results might be unpredictable and will totally rely on MongoDB comparison algorithm.

Only `datetime` and `number` cursor types are supported. Cursor type is determined based on the cursor field name:

* `datetime` - if cursor field name contains a string from: `time`, `date`, `_at`, `timestamp`, `ts`
* `number` - otherwise

## Getting started

This guide describes in details how you can configure MongoDB for integration with Airbyte.

### Create users

Run `mongo` shell, switch to `admin` database and create a `READ_ONLY_USER`. `READ_ONLY_USER` will be used for Airbyte integration. Please make sure that user has read-only privileges.

```javascript
mongo
use admin;
db.createUser({user: "READ_ONLY_USER", pwd: "READ_ONLY_PASSWORD", roles: [{role: "read", db: "TARGET_DATABASE"}]})
```

Make sure the user have appropriate access levels.

### Enable MongoDB authentication

Open `/etc/mongod.conf` and add/replace specific keys:

```yaml
net:
  bindIp: 0.0.0.0

security:
  authorization: enabled
```

Binding to `0.0.0.0` will allow to connect to database from any IP address.

The last line will enable MongoDB security. Now only authenticated users will be able to access the database.

### Configure firewall

Make sure that MongoDB is accessible from external servers. Specific commands will depend on the firewall you are using \(UFW/iptables/AWS/etc\). Please refer to appropriate documentation.

Your `READ_ONLY_USER` should now be ready for use with Airbyte.

### TLS/SSL on a Connection

It is recommended to use encrypted connection. Connection with TLS/SSL security protocol for MongoDb Atlas Cluster and Replica Set instances is enabled by default. To enable TSL/SSL connection with Standalone MongoDb instance, please refer to [MongoDb Documentation](https://docs.mongodb.com/manual/tutorial/configure-ssl/).

### Сonfiguration Parameters

* Database: database name
* Authentication Source: specifies the database that the supplied credentials should be validated against. Defaults to `admin`.
* User: username to use when connecting
* Password: used to authenticate the user
* **Standalone MongoDb instance**
  * Host: URL of the database
  * Port: Port to use for connecting to the database
  * TLS: indicates whether to create encrypted connection
* **Replica Set**
  * Server addresses: the members of a replica set
  * Replica Set: A replica set name
* **MongoDb Atlas Cluster**
  * Cluster URL: URL of a cluster to connect to

For more information regarding configuration parameters, please see [MongoDb Documentation](https://docs.mongodb.com/drivers/java/sync/v4.3/fundamentals/connection/).

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.16 | 2022-08-18 | [14356](https://github.com/airbytehq/airbyte/pull/14356) | DB Sources: only show a table can sync incrementally if at least one column can be used as a cursor field |
| 0.1.15 | 2022-06-17 | [13864](https://github.com/airbytehq/airbyte/pull/13864) | Updated stacktrace format for any trace message errors |
| 0.1.14 | 2022-05-05 | [12428](https://github.com/airbytehq/airbyte/pull/12428) | JsonSchema: Add properties to fields with type 'object' |
| 0.1.13  | 2022-02-21 | [10276](https://github.com/airbytehq/airbyte/pull/10276) | Create a custom codec registry to handle DBRef MongoDB objects |
| 0.1.12 | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256) | (unpublished) Add `-XX:+ExitOnOutOfMemoryError` JVM option |
| 0.1.11 | 2022-01-10 | [9238](https://github.com/airbytehq/airbyte/pull/9238) | Return only those collections for which the user has privileges |
| 0.1.10 | 2021-12-30 | [9202](https://github.com/airbytehq/airbyte/pull/9202) | Update connector fields title/description |
| 0.1.9  | 2021-12-07 | [8491](https://github.com/airbytehq/airbyte/pull/8491) | Configure 10000 limit doc reading during Discovery step |
| 0.1.8  | 2021-11-29 | [8306](https://github.com/airbytehq/airbyte/pull/8306) | Added milliseconds for date format for cursor |
| 0.1.7  | 2021-11-22 | [8161](https://github.com/airbytehq/airbyte/pull/8161) | Updated Performance and updated cursor for timestamp type |
| 0.1.5  | 2021-11-17 | [8046](https://github.com/airbytehq/airbyte/pull/8046) | Added milliseconds to convert timestamp to datetime format |
| 0.1.4  | 2021-11-15 | [7982](https://github.com/airbytehq/airbyte/pull/7982) | Updated Performance |
| 0.1.3  | 2021-10-19 | [7160](https://github.com/airbytehq/airbyte/pull/7160) | Fixed nested document parsing |
| 0.1.2  | 2021-10-07 | [6860](https://github.com/airbytehq/airbyte/pull/6860) | Added filter to avoid MongoDb system collections |
| 0.1.1  | 2021-09-21 | [6364](https://github.com/airbytehq/airbyte/pull/6364) | Source MongoDb: added support via TLS/SSL |
| 0.1.0  | 2021-08-30 | [5530](https://github.com/airbytehq/airbyte/pull/5530) | New source: MongoDb ported to java |
