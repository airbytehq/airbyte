# destination-mongodb-strict-encrypt: Contributor notes

## Test configuration

To run integration tests, you need access to MongoDB.

If you're a community contributor:

1. Create a MongoDB account, or use an existing one.
2. In Database Access, add a database user with read and write permissions.
3. Add a database with a default collection.
4. Add the host, port or cluster URL, database name, username, and password to `secrets/credentials.json`.

Example:

```json
{
  "database": "database_name",
  "user": "user",
  "password": "password",
  "cluster_url": "cluster_url",
  "host": "host",
  "port": "port"
}
```

If you're an Airbyte employee:

1. Access the `MONGODB_TEST_CREDS` secret in LastPass.
2. Create `secrets/credentials.json` with the secret contents.
