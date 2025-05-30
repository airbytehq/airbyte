# MongoDb Source

## Schema

For each collection, if you want to define a schema in order to propagate type the destination, specify the schema for the collection as a unique string. 

Example:

{"embedded_movies":{"fields":[{"name":"_id","type":"string"},{"name":"tomatoes","type":"object","subfields":[{"name":"production","type":"string"}]}]}}

This means that the collection `embedded_movies` has a schema with a field `_id` of type `string` and a field `tomatoes` of type `object` with a subfield `production` of type `string`.

Valid types are:
private static JsonSchemaType convertToSchemaType(final String type) {
    return switch (type) {
      case "boolean" -> JsonSchemaType.BOOLEAN;
      case "int", "long", "double", "decimal" -> JsonSchemaType.NUMBER;
      case "array" -> JsonSchemaType.ARRAY;
      case "object", "javascriptWithScope" -> JsonSchemaType.OBJECT;
      case "null" -> JsonSchemaType.NULL;
      default -> JsonSchemaType.STRING;
    };
  }

## Documentation

This is the repository for the MongoDb source connector in Java.
For information about how to use this connector within Airbyte, see [User Documentation](https://docs.airbyte.io/integrations/sources/mongodb-v2)

## Local development

#### Building via Gradle

From the Airbyte repository root, run:

```
./gradlew :airbyte-integrations:connectors:source-mongodb-v2:build
```

### Locally running the connector docker image

#### Build

Build the connector image via Gradle:

```
./gradlew :airbyte-integrations:connectors:source-mongodb-v2:buildConnectorImage
```

Once built, the docker image name and tag on your host will be `airbyte/source-mongodb-v2:dev`.
the Dockerfile.

## Testing

We use `JUnit` for Java tests.

### Test Configuration

No specific configuration needed for testing Standalone MongoDb instance, MongoDb Test Container is used.
In order to test the MongoDb Atlas or Replica set, you need to provide configuration parameters.

## Community Contributor

As a community contributor, you will need to have an Atlas cluster to test MongoDb source.

1. Create `secrets/credentials.json` file
   1. Insert below json to the file with your configuration
      ```
      {
           "cluster_type": "ATLAS_REPLICA_SET"
           "database": "database_name",
           "username": "username",
           "password": "password",
           "connection_string": "mongodb+srv://cluster0.abcd1.mongodb.net/",
           "auth_source": "auth_database",
      }
      ```
      where `installation_type` is one of `ATLAS_REPLICA_SET` or `SELF_HOSTED_REPLICA_SET` depending on the location of the target cluster.

## Airbyte Employee

1. Access the `MONGODB_TEST_CREDS` secret on LastPass
1. Create a file with the contents at `secrets/credentials.json`

#### Acceptance Tests

To run acceptance and custom integration tests:

```
./gradlew :airbyte-integrations:connectors:source-mongodb-v2:integrationTest
```
