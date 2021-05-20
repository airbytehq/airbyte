# Airbyte Config Migration

This module migrates configs specified in `airbyte-config` to new versions.

## Run production migration in docker
```sh
docker run --rm -v ~/Downloads:/config airbyte/migration:0.23.0-alpha -- \
  --input /config/airbyte_archive.tar.gz \
  --output ~/Downloads/new_airbyte_archive.tar.gz
```

See [Upgrading Airbyte](https://docs.airbyte.io/tutorials/upgrading-airbyte) for details.

## Run dev migration in IDE
Run `MigrationRunner.java` with arguments.

## Run dev migration locally

Run the following command in project root:

```sh
# Get the current version
BUILD_VERSION=$(cat .env | grep VERSION | awk -F"=" '{print $2}')

# Build the migration bundle file
./gradlew airbyte-migration:build

# Extract the bundle file
tar xf ./airbyte-migration/build/distributions/airbyte-migration-${BUILD_VERSION}.tar --strip-components=1

# Run the migration
bin/airbyte-migration \
  --input <input_config_archive.tar.gz> \
  --output <output_config_archive.tar.gz>
```

See [MigrationRunner](./src/main/java/io/airbyte/migrate/MigrationRunner.java) for details.
