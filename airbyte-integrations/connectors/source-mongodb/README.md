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
1. Download Atlas sample dump for MongoDB [here](https://atlas-education.s3.amazonaws.com/sampledata.archive)
1. Import the dump to your local MongoDB: 
```
mongorestore --archive=sampledata.archive
```
4. Configure credentials as appropriate, described below
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