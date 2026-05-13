# source-mongodb-v2: Contributor notes

## Test configuration

Standalone MongoDB tests use MongoDB Testcontainers and do not need specific external configuration.

To test MongoDB Atlas or a replica set, provide credentials in `secrets/credentials.json`.

If you're a community contributor, create `secrets/credentials.json` with this shape:

```json
{
  "cluster_type": "ATLAS_REPLICA_SET",
  "database": "database_name",
  "username": "username",
  "password": "password",
  "connection_string": "mongodb+srv://cluster0.abcd1.mongodb.net/",
  "auth_source": "auth_database"
}
```

`cluster_type` can be `ATLAS_REPLICA_SET` or `SELF_HOSTED_REPLICA_SET`, depending on the target cluster.

If you're an Airbyte employee:

1. Access the `MONGODB_TEST_CREDS` secret in LastPass.
2. Create `secrets/credentials.json` with the secret contents.
