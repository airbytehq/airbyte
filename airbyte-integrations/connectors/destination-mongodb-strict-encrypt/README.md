# MongoDB Test Configuration

In order to test the MongoDB secure only destination, you need a service account key file.

## Community Contributor

As a community contributor, you will need access to a MongoDB to run tests.

1. Create a new account or log into an already created account for mongodb
2. Go to the `Database Access` page and add new database user with read and write permissions
3. Add new database with default collection
4. Add host, port or cluster_url, database name, username and password to `secrets/credentials.json` file
     ```
      {
         "database": "database_name",
         "user": "user",
         "password": "password",
         "cluster_url": "cluster_url",
         "host": "host",
         "port": "port"
       }
      ```

## Airbyte Employee

1. Access the `MONGODB_TEST_CREDS` secret on the LastPass
1. Create a file with the contents at `secrets/credentials.json`