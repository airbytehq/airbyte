# jOOQ Code Generation

## How to Use
This module generates jOOQ code for the configs and jobs database. To use the generated code, add the following dependency:

```gradle
dependencies {
  implementation project(':airbyte-db:jooq')
}
```

The generated code exists in the package `io.airbyte.db.instance.<db-name>.jooq` under the directory `build/generated/<db-name>Database/src/main/java`.

## Code Generation
Gradle plugin `nu.studer.jooq` is used for jOOQ code generation. See [here](https://github.com/etiennestuder/gradle-jooq-plugin) for details.

It is necessary to separate this module from the `lib` module, because we use a custom database (`FlywayMigrationDatabase`) that runs Flyway migration first for the code generator. This implementation needs to be compiled before it can be used.

To manually update the generated code, run the `compileJava` task:

```sh
SUB_BUILD=PLATFORM ./gradlew :airbyte-db:jooq:compileJava
```

Or run the following tasks for individual database:

```sh
# for configs database
SUB_BUILD=PLATFORM ./gradlew :airbyte-db:jooq:generateConfigsDatabaseJooq

# for jobs database
SUB_BUILD=PLATFORM ./gradlew :airbyte-db:jooq:generateJobsDatabaseJooq
```
