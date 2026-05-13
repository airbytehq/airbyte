# destination-mongodb: Contributor notes

## Test configuration

To run integration tests, you need access to MongoDB.

If you're a community contributor:

1. Create a MongoDB account, or use an existing one.
2. In Database Access, add a database user with read and write permissions.
3. Add a database with a default collection.
4. Add the host, port, database name, username, and password to `secrets/credentials.json`.

If you're an Airbyte employee:

1. Access the `MongoDB Integration Test User` secret in Rippling under the Engineering folder.
2. Create `secrets/credentials.json` with the secret contents.
