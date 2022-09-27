# Mongo DB

The MongoDB source supports Full Refresh and Incremental sync strategies.

## Resulting schema

MongoDB does not have anything like table definition, thus we have to define column types from actual attributes and their values. Discover phase have two steps:

### Step 1. Find all unique properties

Connector runs the map-reduce command which returns all unique document props in the collection. Map-reduce approach should be sufficient even for large clusters.

#### Note

To work with Atlas MongoDB, a **non-free** tier is required, as the free tier does not support the ability to perform the mapReduce operation.

### Step 2. Determine property types

For each property found, connector selects 10k documents from the collection where this property is not empty. If all the selected values have the same type - connector will set appropriate type to the property. In all other cases connector will fallback to `string` type.

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
db.createUser({user: "READ_ONLY_USER", pwd: "READ_ONLY_PASSWORD", roles: [{role: "read", db: "TARGET_DATABASE"}]}
```

Make sure the user have appropriate access levels.

### Configure application

In case your application uses MongoDB without authentication you will have to adjust code base and MongoDB config to enable MongoDB authentication. **Otherwise your application might go down once MongoDB authentication will be enabled.**

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


#### Possible configuration Parameters

* [Authentication Source](https://docs.mongodb.com/manual/reference/connection-string/#mongodb-urioption-urioption.authSource)
* Host: URL of the database
* Port: Port to use for connecting to the database
* User: username to use when connecting
* Password: used to authenticate the user
* [Replica Set](https://docs.mongodb.com/manual/reference/connection-string/#mongodb-urioption-urioption.replicaSet)
* Whether to enable SSL


## Changelog
| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.2.3   | 2021-07-20 | [4669](https://github.com/airbytehq/airbyte/pull/4669) | Subscriptions Stream now returns all kinds of subscriptions (including expired and canceled)|
