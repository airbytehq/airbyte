# Mongodb 

The MongoDB source supports Full Refresh only.

## Resulting schema 
MongoDB does not have anything like table definition, thus we have to define column types from actual attributes and their values. The discover phase has two steps:

### Step 1. Find all unique properties
Connector runs the [map-reduce command](https://docs.mongodb.com/manual/core/map-reduce/)  which returns all unique document props in the collection. Map-reduce approach should be sufficient even for large clusters.

### Step 2. Determine property types
For each property found, the connector selects 10k documents from the collection where this property is not empty. If all the selected values have the same type - connector will set appropriate type to the property. In all other cases connector will fallback to `string` type.

## Features

| Feature | Supported |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | No |
| Replicate Incremental Deletes | No |

## Getting started
Usually MongoDB is used locally behind the firewall without authentication. This guide describes in details how you can configure MongoDB for integration with Airbyte.

### Create users

Run `mongo` shell, switch to `admin` database and create three users: 

1. ADMIN_USER will be used for database administration (you can skip this user in case you already use authentication for MongoDB access).
2. APP_USER will be used for authentication inside your application (you can skip this user in case you already use authentication for MongoDB access).
3. READ_ONLY_USER will be used for Airbyte integration. Please make sure that user has read-only privileges.

```js
mongo
use admin;
db.createUser({user: "ADMIN_USER", pwd: "ADMIN_PASSWORD", roles: [{role: "dbOwner", db: "admin"}]})
db.createUser({user: "APP_USER", pwd: "APP_PASSWORD", roles: [{role: "readWrite", db: "APP_DATABASE"}]})
db.createUser({user: "READ_ONLY_USER", pwd: "READ_ONLY_PASSWORD", roles: [{role: "read", db: "TARGET_DATABASE"}]}
```

Make sure all created users have appropriate access levels.

### Configure application

In case your application uses MongoDB without authentication you will have to adjust code base to enable MongoDB authentication. **Otherwise your application will go down once MongoDB authentication will be enabled.**

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

Make sure that MongoDB is accessible from external servers. Specific commands will depend on the firewall you are using (UFW/iptables/AWS/etc). Please refer to appropriate documentation.

Your `READ_ONLY_USER` should now be ready for use with Airbyte.
