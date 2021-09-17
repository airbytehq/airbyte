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

Only `datetime` and `integer` cursor types are supported. Cursor type is determined based on the cursor field name:

* `datetime` - if cursor field name contains a string from: `time`, `date`, `_at`, `timestamp`, `ts`
* `integer` - otherwise

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

### Сonfiguration Parameters
* Database: database name
* Authentication Source: specifies the database that the supplied credentials should be validated against. Defaults to `admin`.
* User: username to use when connecting
* Password: used to authenticate the user
* TSL: whether to use TSL connection
* **Standalone MongoDb instance**
  * Host: URL of the database
  * Port: Port to use for connecting to the database
* **Replica Set**
  * Server addresses: the members of a replica set
  * Replica Set: A replica set name
* **MongoDb Atlas Cluster**
  * Cluster URL: URL of a cluster to connect to

For more information regarding configuration parameters, please see [MongoDb Documentation](https://docs.mongodb.com/drivers/java/sync/v4.3/fundamentals/connection/).

## Changelog
| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.0   | 2021-08-30 | [5530](https://github.com/airbytehq/airbyte/pull/5530) | New source: MongoDb ported to java |
