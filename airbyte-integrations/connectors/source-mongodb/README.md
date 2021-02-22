# Mongodb Source 

This is the repository for the Mongodb source connector, written in Ruby. 

## Local development
### Build
First, build the module by running the following from the `airbyte` project root directory: 
```
cd airbyte-integrations/connectors/source-mongodb/
docker build . -t airbyte/source-mongodb:dev
```

### Integration Tests 
1. Configure credentials as appropriate, described below
1. From the airbyte project root, run `./gradlew clean :airbyte-integrations:connectors:source-mongodb:integrationTest`

## Configure credentials
### Configuring credentials as a community contributor
Follow the instructions in the [MongoDB documentation](https://docs.airbyte.io/integrations/sources/mongodb) for generating credentials to access the Mongo DB, then put those 
in a file named `secrets/valid_credentials.json`. 
