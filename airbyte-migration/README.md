# Airbyte Config Migration

This module migrates configs specified in `airbyte-config` to new versions.

WARNING: the file-based migrations are deprecated. Please write a Flyway migration whenever you want to update the database. See [here](../airbyte-db/lib/README.md) for details.

## Change Airbyte Configs
- Update the config json schema in [`airbyte-config/models`](../airbyte-config/models).
- Add the changed json schema to the [main resources](./src/main/resources/migrations).
- If a migration is needed, create a migration file under [`io.airbyte.migrate.migrations`](./src/main/java/io/airbyte/migrate/migrations).
- Register the migration in [`Migrations.java`](./src/main/java/io/airbyte/migrate/Migrations.java).
- If needed, write a migration unit test under [`io.airbyte.migrate.migrations`](./src/test/java/io/airbyte/migrate/migrations).
- Test the migration locally in IDE or commandline (see below).

## Test Migration Locally

### IDE
Run `MigrationRunner.java` with arguments (`--input`, `--output`, `--target-version`).

### Command line

Run the following command in project root:

```sh
# Get the current version
BUILD_VERSION=$(cat .env | grep VERSION | awk -F"=" '{print $2}')

# Build the migration bundle file
SUB_BUILD=PLATFORM ./gradlew airbyte-migration:build

# Extract the bundle file
tar xf ./airbyte-migration/build/distributions/airbyte-migration-${BUILD_VERSION}.tar --strip-components=1

# Run the migration
bin/airbyte-migration \
  --input <input_config_archive.tar.gz> \
  --output <output_config_archive.tar.gz>
```

See [MigrationRunner](./src/main/java/io/airbyte/migrate/MigrationRunner.java) for details.

## Run migration in production

```sh
BUILD_VERSION=$(cat .env | grep VERSION | awk -F"=" '{print $2}')
INPUT_PATH=<path to directory containing downloaded airbyte_archive.tar.gz>
OUTPUT_PATH=<path to where migrated archive will be written (should end in .tar.gz)>
TARGET_VERSION=<version you are migrating to or empty for latest>

docker run --rm -v ${INPUT_PATH}:/config airbyte/migration:${BUILD_VERSION} -- \
  --input /config/airbyte_archive.tar.gz \
  --output ${OUTPUT_PATH} \
  [ --target-version ${TARGET_VERSION} ]
```

See [Upgrading Airbyte](https://docs.airbyte.io/tutorials/upgrading-airbyte) for details.
