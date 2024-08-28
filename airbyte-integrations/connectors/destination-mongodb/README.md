# MongoDB Test Configuration

In order to test the MongoDB destination, you need a service account key file.

## Community Contributor

As a community contributor, you will need access to a MongoDB to run tests.

1. Create a new account or log into an already created account for mongodb
1. Go to the `Database Access` page and add new database user with read and write permissions
1. Add new database with default collection
1. Add host, port, database name, username and password to `secrets/credentials.json` file

## Airbyte Employee

1. Access the `MongoDB Integration Test User` secret on Rippling under the `Engineering` folder
1. Create a file with the contents at `secrets/credentials.json`
