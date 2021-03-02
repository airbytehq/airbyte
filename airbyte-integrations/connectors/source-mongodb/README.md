# Mongodb Source 

This is the repository for the Mongodb source connector, written in Ruby. 

## Local development
### Build
First, build the module by running the following from the airbyte project root directory: 
```
cd airbyte-integrations/connectors/source-mongodb/
docker build . -t airbyte/source-mongodb:dev
```

### Integration Tests 
From the airbyte project root, run:
```
./gradlew clean :airbyte-integrations:connectors:source-mongodb:integrationTest
```

## Configure credentials
### Configuring credentials as a community contributor
Required credentials are stored in `secrets` folder already. You can adjust them manually to run some advanced tests, but by default they should work as is.

## Discover phase
MongoDB does not have anything like table definition, thus we have to define column types from actual attributes and their values. Discover phase have two steps:

### Step 1. Find all unique properties
Connector runs the map-reduce command which returns all unique document props in the collection. Map-reduce approach should be sufficient even for large clusters.

### Step 2. Determine property types
For each property found, connector selects 10k documents from the collection where this property is not empty. If all the selected values have the same type - connector will set appropriate type to the property. In all other cases connector will fallback to `string` type.

## Author
This connector was authored by [Yury Koleda](https://github.com/FUT).
