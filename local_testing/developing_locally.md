# Prerequisites 

1. Java 21
2. `abctl` [command](https://docs.airbyte.com/platform/2.0/using-airbyte/getting-started/oss-quickstart)
3. `gradle`
4. `docker`

# Relevant documentation

1. https://docs.airbyte.com/platform/2.0/contributing-to-airbyte/developing-locally / https://docs.airbyte.com/platform/connector-development/local-connector-development
2. https://github.com/airbytehq/airbyte/tree/master/connector-writer/destination
3. https://docs.airbyte.com/platform/connector-development/debugging-docker

# Set up sources and destination

Prerequisites: This requires that you have used the `abctl` command to bring up Airbyte. The `docker-compose` file references the `kind` network of the docker container in which the `abctl` command brings up the Kubernetes cluster with all the Airbyte components.

1. `cd local-testing` && `docker-compose up -d` 
2. The above will bring up `nessie` (catalog), `postgres` (used as a source), `trino` and `s3` (using `localstack`).
    a. The postgres database will have a table `postgres.public.test_table` created at startup.
    b. The localstack s3 service will have an s3 bucket `local-bucket` created at startup.

# Building the connector locally

1. Ensure you are at the root of the project. Run
```
./gradlew :airbyte-integrations:connectors:destination-s3-data-lake:build -x compileTestKotlin -x compileIntegrationTestKotlin
```
2. Run Airbyte using the `abctl` command (the `abctl` command uses `kind` to create a Kubernetes cluster as a Docker container, [reference](https://docs.airbyte.com/platform/2.0/contributing-to-airbyte/developing-locally#using-abctl-for-airbyte-development)) 
3. Load the docker image built by the command in 1. into the Kubernetes cluster brought up by `abctl` command. ` 
kind load docker-image airbyte/destination-s3-data-lake:dev -n airbyte-abctl`.
4. Go to http://localhost:8000/ and enter the credentials (you can find out the credentials using the command `abctl local credentials`)
5. Add the destination as "S3 Data Lake" with the following details. Ensure the version of the connector is `dev` (the tag of the image built in 1, you can change the version of the connector if needed using "Workspace settings" on Airbyte UI): -
    a. AWS Access Key ID: `test`
    b. AWS Secret Access Key: `test`
    c. S3 Bucket Name: `local-bucket` 
    d. S3 Bucket Region: `us-east-1`
    e. Warehouse location: `s3://local-bucket/local-warehouse`
    f. Main branch name: `main`
    g. Catalog type: `Nessie`
    h. Nessie Server URI: `http://nessie:19120/api/v2`
    i. Default namespace: `local_namespace`
    j. S3 Endpoint: `http://localstack:4566`
6. Add the source as "Postgres" with the following details: -
    a. Host: `postgresdb`
    b. Port: 5432
    c: Database Name: `postgres`
    d. Username: `postgres`
    e. Password: `password`
7. Create a connection from "Postgres" source to "S3 Data lake" destination and start testing it.

# ToDo:

1. 
