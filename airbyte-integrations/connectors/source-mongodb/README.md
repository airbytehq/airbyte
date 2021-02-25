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
1. Setup MongoDB on your local machine
1. Import the dump from `integration_tests/dump` folder to your local MongoDB: 
```
mongorestore --archive=integration_tests/dump/analytics.archive
```
3. Configure credentials as appropriate, described below
1. From the airbyte project root, run:
```
./gradlew clean :airbyte-integrations:connectors:source-mongodb:integrationTest
```

## Configure credentials
### Configuring credentials as a community contributor
You will need to copy sample configs and adjust them to your test setup. From the airbyte project root directory run:
```
cd airbyte-integrations/connectors/source-mongodb/
cp -r secrets.sample secrets
```

#### secrets/valid_credentials.json
Adjust the config to your local test setup.

It is better to use `sample_analytics` database because there are several different collections.

#### secrets/fullrefresh_configured_catalog.json
This config will work as is if you use provided dump and `sample_analytics` database. Adjust the config to your local test setup in any other case.

## Discover phase
MongoDB does not have anything like table definition, thus we have to define column types from actual attributes and their values. Discover phase have two steps:

### Step 1. Find all unique properties
Connector runs the map-reduce command which returns all unique document props in the collection. Map-reduce approach should be sufficient even for large clusters.

### Step 2. Determine property types
For each property found, connector selects 10k documents from the collection where this property is not empty. If all the selected values have the same type - connector will set appropriate type to the property. In all other cases connector will fallback to `string` type.

## Author
This connector was authored by [Yury Koleda](https://github.com/FUT).
